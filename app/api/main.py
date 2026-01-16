"""FastAPI application factory."""

import os
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pathlib import Path
from pydantic import BaseModel

from app.storage.database import Database
from app.storage.repositories import (
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
    PriceHistoryRepository,
)

app = FastAPI(
    title="Price Spy",
    description="Visual price tracking with AI",
    version="0.3.0"
)

# Templates directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount screenshots directory if it exists
screenshots_dir = Path("screenshots")
if screenshots_dir.exists():
    app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Test database path override (used in tests)
_test_db_path: Optional[str] = None


def get_db() -> Database:
    """Get database connection."""
    global _test_db_path
    db_path = _test_db_path if _test_db_path else "data/pricespy.db"
    db = Database(db_path)
    db.initialize()
    return db


class DashboardItem(BaseModel):
    """View model for dashboard items."""
    id: int
    product_name: str
    store_name: str
    url: str
    price: Optional[float] = None
    currency: str = "EUR"
    target_price: Optional[float] = None
    unit_price: Optional[float] = None
    unit: Optional[str] = None
    is_available: Optional[bool] = None
    screenshot_path: Optional[str] = None
    last_checked: Optional[str] = None


class ExtractResponse(BaseModel):
    """Response for extract endpoint."""
    status: str
    item_id: int
    message: Optional[str] = None


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.3.0"}


@app.get("/api/items", response_model=List[DashboardItem])
async def get_items():
    """Get all tracked items with their latest prices."""
    db = get_db()
    try:
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        items = tracked_repo.get_active()
        result = []

        for item in items:
            product = product_repo.get_by_id(item.product_id)
            store = store_repo.get_by_id(item.store_id)
            latest_price = price_repo.get_latest_by_url(item.url)

            # Check if screenshot exists
            screenshot_path = f"screenshots/{item.id}.png"
            has_screenshot = Path(screenshot_path).exists()

            dashboard_item = DashboardItem(
                id=item.id,
                product_name=product.name if product else "Unknown",
                store_name=store.name if store else "Unknown",
                url=item.url,
                price=latest_price.price if latest_price else None,
                currency=latest_price.currency if latest_price else "EUR",
                target_price=product.target_price if product else None,
                screenshot_path=screenshot_path if has_screenshot else None,
                last_checked=item.last_checked_at.isoformat() if item.last_checked_at else None,
            )
            result.append(dashboard_item)

        return result
    finally:
        db.close()


async def run_extraction(item_id: int, db_path: str):
    """Background task to run price extraction."""
    from app.core.browser import capture_screenshot
    from app.core.vision import extract_with_structured_output
    from app.models.schemas import PriceHistoryRecord
    from datetime import datetime, timezone

    db = Database(db_path)
    db.initialize()

    try:
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        item = tracked_repo.get_by_id(item_id)
        if not item:
            return

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return

        # Capture screenshot
        screenshot_bytes = await capture_screenshot(item.url)

        # Save screenshot
        screenshot_path = Path(f"screenshots/{item_id}.png")
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(screenshot_bytes)

        # Extract price
        result = await extract_with_structured_output(screenshot_bytes, api_key)

        # Save to price history
        record = PriceHistoryRecord(
            product_name=result.product_name,
            price=result.price,
            currency=result.currency,
            confidence=1.0,  # Structured output is trusted
            url=item.url,
            store_name=result.store_name,
        )
        price_repo.insert(record)

        # Update last checked time
        tracked_repo.set_last_checked(item_id)

    finally:
        db.close()


@app.post("/api/extract/{item_id}", response_model=ExtractResponse, status_code=202)
async def trigger_extraction(item_id: int, background_tasks: BackgroundTasks):
    """Trigger price extraction for a tracked item."""
    db = get_db()
    try:
        tracked_repo = TrackedItemRepository(db)
        item = tracked_repo.get_by_id(item_id)

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        db_path = _test_db_path if _test_db_path else "data/pricespy.db"
        background_tasks.add_task(run_extraction, item_id, db_path)

        return ExtractResponse(
            status="queued",
            item_id=item_id,
            message="Extraction queued"
        )
    finally:
        db.close()


@app.get("/")
async def dashboard(request: Request):
    """Render dashboard page."""
    db = get_db()
    try:
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        tracked_items = tracked_repo.get_active()
        items = []

        for item in tracked_items:
            product = product_repo.get_by_id(item.product_id)
            store = store_repo.get_by_id(item.store_id)
            latest_price = price_repo.get_latest_by_url(item.url)

            screenshot_path = f"screenshots/{item.id}.png"
            has_screenshot = Path(screenshot_path).exists()

            items.append({
                "id": item.id,
                "product_name": product.name if product else "Unknown",
                "store_name": store.name if store else "Unknown",
                "url": item.url,
                "price": latest_price.price if latest_price else None,
                "currency": latest_price.currency if latest_price else "EUR",
                "target_price": product.target_price if product else None,
                "screenshot_path": screenshot_path if has_screenshot else None,
            })

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {"items": items}
        )
    finally:
        db.close()
