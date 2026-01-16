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


class ProductCreate(BaseModel):
    """Request model for creating a product."""
    name: str
    category: Optional[str] = None
    purchase_type: Optional[str] = None
    target_price: Optional[float] = None
    preferred_unit_size: Optional[str] = None
    current_stock: int = 0


class ProductResponse(BaseModel):
    """Response model for product."""
    id: int
    name: str
    category: Optional[str] = None
    purchase_type: Optional[str] = None
    target_price: Optional[float] = None
    preferred_unit_size: Optional[str] = None
    current_stock: int = 0


class StoreCreate(BaseModel):
    """Request model for creating a store."""
    name: str
    shipping_cost_standard: Optional[float] = None
    free_shipping_threshold: Optional[float] = None
    notes: Optional[str] = None


class StoreResponse(BaseModel):
    """Response model for store."""
    id: int
    name: str
    shipping_cost_standard: Optional[float] = None
    free_shipping_threshold: Optional[float] = None
    notes: Optional[str] = None


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


@app.get("/api/items/{item_id}", response_model=DashboardItem)
async def get_item(item_id: int):
    """Get a single tracked item by ID."""
    db = get_db()
    try:
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        item = tracked_repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        product = product_repo.get_by_id(item.product_id)
        store = store_repo.get_by_id(item.store_id)
        latest_price = price_repo.get_latest_by_url(item.url)

        screenshot_path = f"screenshots/{item.id}.png"
        has_screenshot = Path(screenshot_path).exists()

        return DashboardItem(
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


# --- Products API ---

@app.get("/api/products", response_model=List[ProductResponse])
async def get_products():
    """Get all products."""
    db = get_db()
    try:
        repo = ProductRepository(db)
        products = repo.get_all()
        return [
            ProductResponse(
                id=p.id,
                name=p.name,
                category=p.category,
                purchase_type=p.purchase_type,
                target_price=p.target_price,
                preferred_unit_size=p.preferred_unit_size,
                current_stock=p.current_stock,
            )
            for p in products
        ]
    finally:
        db.close()


@app.post("/api/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product."""
    from app.models.schemas import Product

    db = get_db()
    try:
        repo = ProductRepository(db)
        # Build kwargs, excluding None values to use schema defaults
        kwargs = {"name": product.name}
        if product.category is not None:
            kwargs["category"] = product.category
        if product.purchase_type is not None:
            kwargs["purchase_type"] = product.purchase_type
        if product.target_price is not None:
            kwargs["target_price"] = product.target_price
        if product.preferred_unit_size is not None:
            kwargs["preferred_unit_size"] = product.preferred_unit_size
        kwargs["current_stock"] = product.current_stock

        new_product = Product(**kwargs)
        product_id = repo.insert(new_product)
        created = repo.get_by_id(product_id)
        return ProductResponse(
            id=created.id,
            name=created.name,
            category=created.category,
            purchase_type=created.purchase_type,
            target_price=created.target_price,
            preferred_unit_size=created.preferred_unit_size,
            current_stock=created.current_stock,
        )
    finally:
        db.close()


@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get a product by ID."""
    db = get_db()
    try:
        repo = ProductRepository(db)
        product = repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductResponse(
            id=product.id,
            name=product.name,
            category=product.category,
            purchase_type=product.purchase_type,
            target_price=product.target_price,
            preferred_unit_size=product.preferred_unit_size,
            current_stock=product.current_stock,
        )
    finally:
        db.close()


@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate):
    """Update a product."""
    from app.models.schemas import Product

    db = get_db()
    try:
        repo = ProductRepository(db)
        existing = repo.get_by_id(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        kwargs = {"name": product.name}
        if product.category is not None:
            kwargs["category"] = product.category
        if product.purchase_type is not None:
            kwargs["purchase_type"] = product.purchase_type
        if product.target_price is not None:
            kwargs["target_price"] = product.target_price
        if product.preferred_unit_size is not None:
            kwargs["preferred_unit_size"] = product.preferred_unit_size
        kwargs["current_stock"] = product.current_stock

        updated_product = Product(**kwargs)
        repo.update(product_id, updated_product)
        result = repo.get_by_id(product_id)
        return ProductResponse(
            id=result.id,
            name=result.name,
            category=result.category,
            purchase_type=result.purchase_type,
            target_price=result.target_price,
            preferred_unit_size=result.preferred_unit_size,
            current_stock=result.current_stock,
        )
    finally:
        db.close()


@app.delete("/api/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """Delete a product."""
    db = get_db()
    try:
        repo = ProductRepository(db)
        existing = repo.get_by_id(product_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")
        repo.delete(product_id)
    finally:
        db.close()


# --- Stores API ---

@app.get("/api/stores", response_model=List[StoreResponse])
async def get_stores():
    """Get all stores."""
    db = get_db()
    try:
        repo = StoreRepository(db)
        stores = repo.get_all()
        return [
            StoreResponse(
                id=s.id,
                name=s.name,
                shipping_cost_standard=s.shipping_cost_standard,
                free_shipping_threshold=s.free_shipping_threshold,
                notes=s.notes,
            )
            for s in stores
        ]
    finally:
        db.close()


@app.post("/api/stores", response_model=StoreResponse, status_code=201)
async def create_store(store: StoreCreate):
    """Create a new store."""
    from app.models.schemas import Store

    db = get_db()
    try:
        repo = StoreRepository(db)
        kwargs = {"name": store.name}
        if store.shipping_cost_standard is not None:
            kwargs["shipping_cost_standard"] = store.shipping_cost_standard
        if store.free_shipping_threshold is not None:
            kwargs["free_shipping_threshold"] = store.free_shipping_threshold
        if store.notes is not None:
            kwargs["notes"] = store.notes

        new_store = Store(**kwargs)
        store_id = repo.insert(new_store)
        created = repo.get_by_id(store_id)
        return StoreResponse(
            id=created.id,
            name=created.name,
            shipping_cost_standard=created.shipping_cost_standard,
            free_shipping_threshold=created.free_shipping_threshold,
            notes=created.notes,
        )
    finally:
        db.close()


@app.get("/api/stores/{store_id}", response_model=StoreResponse)
async def get_store(store_id: int):
    """Get a store by ID."""
    db = get_db()
    try:
        repo = StoreRepository(db)
        store = repo.get_by_id(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return StoreResponse(
            id=store.id,
            name=store.name,
            shipping_cost_standard=store.shipping_cost_standard,
            free_shipping_threshold=store.free_shipping_threshold,
            notes=store.notes,
        )
    finally:
        db.close()


@app.put("/api/stores/{store_id}", response_model=StoreResponse)
async def update_store(store_id: int, store: StoreCreate):
    """Update a store."""
    from app.models.schemas import Store

    db = get_db()
    try:
        repo = StoreRepository(db)
        existing = repo.get_by_id(store_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Store not found")

        kwargs = {"name": store.name}
        if store.shipping_cost_standard is not None:
            kwargs["shipping_cost_standard"] = store.shipping_cost_standard
        if store.free_shipping_threshold is not None:
            kwargs["free_shipping_threshold"] = store.free_shipping_threshold
        if store.notes is not None:
            kwargs["notes"] = store.notes

        updated_store = Store(**kwargs)
        repo.update(store_id, updated_store)
        result = repo.get_by_id(store_id)
        return StoreResponse(
            id=result.id,
            name=result.name,
            shipping_cost_standard=result.shipping_cost_standard,
            free_shipping_threshold=result.free_shipping_threshold,
            notes=result.notes,
        )
    finally:
        db.close()


@app.delete("/api/stores/{store_id}", status_code=204)
async def delete_store(store_id: int):
    """Delete a store."""
    db = get_db()
    try:
        repo = StoreRepository(db)
        existing = repo.get_by_id(store_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Store not found")
        repo.delete(store_id)
    finally:
        db.close()
