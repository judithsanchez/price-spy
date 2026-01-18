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
from app.core.scheduler import (
    get_scheduler_status,
    trigger_run_now,
    pause_scheduler,
    resume_scheduler,
    lifespan_scheduler,
)

app = FastAPI(
    title="Price Spy",
    description="Visual price tracking with AI",
    version="0.3.0",
    lifespan=lifespan_scheduler
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
    status: str  # "success", "error"
    item_id: int
    message: Optional[str] = None
    price: Optional[float] = None
    error: Optional[str] = None


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


class TrackedItemCreate(BaseModel):
    """Request model for creating a tracked item."""
    product_id: int
    store_id: int
    url: str
    item_name_on_site: Optional[str] = None
    quantity_size: float
    quantity_unit: str
    items_per_lot: int = 1
    is_active: bool = True
    alerts_enabled: bool = True


class TrackedItemResponse(BaseModel):
    """Response model for tracked item."""
    id: int
    product_id: int
    store_id: int
    url: str
    item_name_on_site: Optional[str] = None
    quantity_size: float
    quantity_unit: str
    items_per_lot: int = 1
    is_active: bool = True
    alerts_enabled: bool = True


class ExtractionLogResponse(BaseModel):
    """Response model for extraction log."""
    id: int
    tracked_item_id: int
    status: str
    model_used: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: str


class ErrorLogResponse(BaseModel):
    """Response model for error log."""
    id: int
    error_type: str
    message: str
    url: Optional[str] = None
    screenshot_path: Optional[str] = None
    stack_trace: Optional[str] = None
    created_at: str


class ExtractionStatsResponse(BaseModel):
    """Response model for extraction statistics."""
    total_today: int
    success_count: int
    error_count: int
    avg_duration_ms: int


class ApiUsageResponse(BaseModel):
    """Response model for API usage per model."""
    model: str
    used: int
    limit: int
    remaining: int
    exhausted: bool


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


@app.get("/api/items/{item_id}/price-history")
async def get_price_history(item_id: int, days: int = 30):
    """Get price history for a tracked item."""
    db = get_db()
    try:
        product_repo = ProductRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        item = tracked_repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        product = product_repo.get_by_id(item.product_id)

        # Get all prices for this URL
        all_prices = price_repo.get_by_url(item.url)

        # Filter by days
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)
        prices = [p for p in all_prices if p.created_at >= cutoff]

        # Sort chronologically (oldest first)
        prices.sort(key=lambda p: p.created_at)

        # Format prices for response
        price_list = [
            {"date": p.created_at.strftime("%Y-%m-%d"), "price": p.price}
            for p in prices
        ]

        # Calculate stats
        if prices:
            price_values = [p.price for p in prices]
            min_price = min(price_values)
            max_price = max(price_values)
            avg_price = round(sum(price_values) / len(price_values), 2)
            current_price = prices[-1].price
            price_drop_pct = round(((current_price - max_price) / max_price) * 100, 2)
            currency = prices[0].currency
        else:
            min_price = None
            max_price = None
            avg_price = None
            current_price = None
            price_drop_pct = None
            currency = "EUR"

        return {
            "item_id": item_id,
            "product_name": product.name if product else "Unknown",
            "currency": currency,
            "target_price": product.target_price if product else None,
            "prices": price_list,
            "stats": {
                "min": min_price,
                "max": max_price,
                "avg": avg_price,
                "current": current_price,
                "price_drop_pct": price_drop_pct,
            },
        }
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


class BatchExtractResponse(BaseModel):
    """Response for batch extract endpoint."""
    total: int
    success_count: int
    error_count: int
    results: list


@app.post("/api/extract/all", response_model=BatchExtractResponse)
async def trigger_batch_extraction():
    """Run price extraction for all active tracked items."""
    from app.core.batch_extraction import extract_all_items, get_batch_summary

    db = get_db()
    try:
        # Use shorter delay in API context (configurable)
        delay = float(os.getenv("BATCH_DELAY_SECONDS", "2"))
        results = await extract_all_items(db, delay_seconds=delay)
        summary = get_batch_summary(results)
        return BatchExtractResponse(**summary)
    finally:
        db.close()


@app.post("/api/extract/{item_id}", response_model=ExtractResponse)
async def trigger_extraction(item_id: int):
    """Run price extraction for a tracked item with rate limiting and logging."""
    import time
    from app.core.browser import capture_screenshot
    from app.core.vision import extract_with_structured_output
    from app.models.schemas import PriceHistoryRecord, ExtractionLog
    from app.storage.repositories import ExtractionLogRepository
    from app.core.rate_limiter import RateLimitTracker

    db = get_db()
    start_time = time.time()
    model_used = None

    try:
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)
        log_repo = ExtractionLogRepository(db)
        tracker = RateLimitTracker(db)
        item = tracked_repo.get_by_id(item_id)

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            log_repo.insert(ExtractionLog(
                tracked_item_id=item_id,
                status="error",
                error_message="GEMINI_API_KEY not configured"
            ))
            return ExtractResponse(
                status="error",
                item_id=item_id,
                error="GEMINI_API_KEY not configured"
            )

        try:
            # Capture screenshot
            screenshot_bytes = await capture_screenshot(item.url)

            # Save screenshot
            screenshot_path = Path(f"screenshots/{item_id}.png")
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot_path.write_bytes(screenshot_bytes)

            # Extract price with rate limiting
            result, model_used = await extract_with_structured_output(
                screenshot_bytes, api_key, tracker
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Save to price history
            record = PriceHistoryRecord(
                product_name=result.product_name,
                price=result.price,
                currency=result.currency,
                confidence=1.0,
                url=item.url,
                store_name=result.store_name,
            )
            price_repo.insert(record)

            # Log successful extraction
            log_repo.insert(ExtractionLog(
                tracked_item_id=item_id,
                status="success",
                model_used=model_used,
                price=result.price,
                currency=result.currency,
                duration_ms=duration_ms
            ))

            # Update last checked time
            tracked_repo.set_last_checked(item_id)

            return ExtractResponse(
                status="success",
                item_id=item_id,
                message=f"Extracted price: {result.currency} {result.price:.2f}",
                price=result.price
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)

            # Log failed extraction
            log_repo.insert(ExtractionLog(
                tracked_item_id=item_id,
                status="error",
                model_used=model_used,
                error_message=error_msg[:2000],
                duration_ms=duration_ms
            ))

            # Parse common errors for friendlier messages
            if "429" in error_msg or "quota" in error_msg.lower():
                error_msg = "Gemini API quota exceeded. Try again later."
            elif "401" in error_msg or "API key" in error_msg.lower():
                error_msg = "Invalid Gemini API key."
            elif "exhausted" in error_msg.lower():
                error_msg = "All AI models exhausted for today. Try again tomorrow."

            return ExtractResponse(
                status="error",
                item_id=item_id,
                error=error_msg
            )

    finally:
        db.close()


@app.get("/")
async def dashboard(request: Request):
    """Render dashboard page."""
    from app.core.price_calculator import calculate_volume_price

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

            # Calculate unit price if we have a price
            unit_price = None
            unit = None
            if latest_price and latest_price.price:
                unit_price, unit = calculate_volume_price(
                    latest_price.price,
                    item.items_per_lot,
                    item.quantity_size,
                    item.quantity_unit
                )
                unit_price = round(unit_price, 2)

            # Determine if this is a deal (price at or below target)
            price = latest_price.price if latest_price else None
            target = product.target_price if product else None
            is_deal = price is not None and target is not None and price <= target

            items.append({
                "id": item.id,
                "product_name": product.name if product else "Unknown",
                "store_name": store.name if store else "Unknown",
                "url": item.url,
                "price": price,
                "currency": latest_price.currency if latest_price else "EUR",
                "target_price": target,
                "unit_price": unit_price,
                "unit": unit,
                "is_deal": is_deal,
                "screenshot_path": screenshot_path if has_screenshot else None,
            })

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {"items": items}
        )
    finally:
        db.close()


@app.get("/products")
async def products_page(request: Request):
    """Render products management page."""
    return templates.TemplateResponse(request, "products.html", {})


@app.get("/stores")
async def stores_page(request: Request):
    """Render stores management page."""
    return templates.TemplateResponse(request, "stores.html", {})


@app.get("/tracked-items")
async def tracked_items_page(request: Request):
    """Render tracked items management page."""
    return templates.TemplateResponse(request, "tracked-items.html", {})


@app.get("/logs")
async def logs_page(request: Request):
    """Render logs page."""
    return templates.TemplateResponse(request, "logs.html", {})


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


# --- Tracked Items API ---

@app.get("/api/tracked-items", response_model=List[TrackedItemResponse])
async def get_tracked_items():
    """Get all tracked items."""
    db = get_db()
    try:
        repo = TrackedItemRepository(db)
        items = repo.get_active()
        return [
            TrackedItemResponse(
                id=i.id,
                product_id=i.product_id,
                store_id=i.store_id,
                url=i.url,
                item_name_on_site=i.item_name_on_site,
                quantity_size=i.quantity_size,
                quantity_unit=i.quantity_unit,
                items_per_lot=i.items_per_lot,
                is_active=i.is_active,
                alerts_enabled=i.alerts_enabled,
            )
            for i in items
        ]
    finally:
        db.close()


@app.post("/api/tracked-items", response_model=TrackedItemResponse, status_code=201)
async def create_tracked_item(item: TrackedItemCreate):
    """Create a new tracked item."""
    from app.models.schemas import TrackedItem

    db = get_db()
    try:
        repo = TrackedItemRepository(db)
        new_item = TrackedItem(
            product_id=item.product_id,
            store_id=item.store_id,
            url=item.url,
            item_name_on_site=item.item_name_on_site,
            quantity_size=item.quantity_size,
            quantity_unit=item.quantity_unit,
            items_per_lot=item.items_per_lot,
            is_active=item.is_active,
            alerts_enabled=item.alerts_enabled,
        )
        item_id = repo.insert(new_item)
        created = repo.get_by_id(item_id)
        return TrackedItemResponse(
            id=created.id,
            product_id=created.product_id,
            store_id=created.store_id,
            url=created.url,
            item_name_on_site=created.item_name_on_site,
            quantity_size=created.quantity_size,
            quantity_unit=created.quantity_unit,
            items_per_lot=created.items_per_lot,
            is_active=created.is_active,
            alerts_enabled=created.alerts_enabled,
        )
    finally:
        db.close()


@app.get("/api/tracked-items/{item_id}", response_model=TrackedItemResponse)
async def get_tracked_item(item_id: int):
    """Get a tracked item by ID."""
    db = get_db()
    try:
        repo = TrackedItemRepository(db)
        item = repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Tracked item not found")
        return TrackedItemResponse(
            id=item.id,
            product_id=item.product_id,
            store_id=item.store_id,
            url=item.url,
            item_name_on_site=item.item_name_on_site,
            quantity_size=item.quantity_size,
            quantity_unit=item.quantity_unit,
            items_per_lot=item.items_per_lot,
            is_active=item.is_active,
            alerts_enabled=item.alerts_enabled,
        )
    finally:
        db.close()


@app.put("/api/tracked-items/{item_id}", response_model=TrackedItemResponse)
async def update_tracked_item(item_id: int, item: TrackedItemCreate):
    """Update a tracked item."""
    from app.models.schemas import TrackedItem

    db = get_db()
    try:
        repo = TrackedItemRepository(db)
        existing = repo.get_by_id(item_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tracked item not found")

        updated_item = TrackedItem(
            product_id=item.product_id,
            store_id=item.store_id,
            url=item.url,
            item_name_on_site=item.item_name_on_site,
            quantity_size=item.quantity_size,
            quantity_unit=item.quantity_unit,
            items_per_lot=item.items_per_lot,
            is_active=item.is_active,
            alerts_enabled=item.alerts_enabled,
        )
        repo.update(item_id, updated_item)
        result = repo.get_by_id(item_id)
        return TrackedItemResponse(
            id=result.id,
            product_id=result.product_id,
            store_id=result.store_id,
            url=result.url,
            item_name_on_site=result.item_name_on_site,
            quantity_size=result.quantity_size,
            quantity_unit=result.quantity_unit,
            items_per_lot=result.items_per_lot,
            is_active=result.is_active,
            alerts_enabled=result.alerts_enabled,
        )
    finally:
        db.close()


@app.delete("/api/tracked-items/{item_id}", status_code=204)
async def delete_tracked_item(item_id: int):
    """Delete a tracked item."""
    db = get_db()
    try:
        repo = TrackedItemRepository(db)
        existing = repo.get_by_id(item_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tracked item not found")
        repo.delete(item_id)
    finally:
        db.close()


# --- Extraction Logs & API Usage ---

@app.get("/api/logs", response_model=List[ExtractionLogResponse])
async def get_extraction_logs(
    status: Optional[str] = None,
    item_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get recent extraction logs with optional filters."""
    from app.storage.repositories import ExtractionLogRepository

    db = get_db()
    try:
        repo = ExtractionLogRepository(db)
        logs = repo.get_all_filtered(
            status=status,
            item_id=item_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return [
            ExtractionLogResponse(
                id=log.id,
                tracked_item_id=log.tracked_item_id,
                status=log.status,
                model_used=log.model_used,
                price=log.price,
                currency=log.currency,
                error_message=log.error_message,
                duration_ms=log.duration_ms,
                created_at=log.created_at.isoformat(),
            )
            for log in logs
        ]
    finally:
        db.close()


@app.get("/api/errors", response_model=List[ErrorLogResponse])
async def get_error_logs(
    error_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get recent error logs with optional filters."""
    from app.storage.repositories import ErrorLogRepository

    db = get_db()
    try:
        repo = ErrorLogRepository(db)
        logs = repo.get_all_filtered(
            error_type=error_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return [
            ErrorLogResponse(
                id=log.id,
                error_type=log.error_type,
                message=log.message,
                url=log.url,
                screenshot_path=log.screenshot_path,
                stack_trace=log.stack_trace,
                created_at=log.created_at.isoformat(),
            )
            for log in logs
        ]
    finally:
        db.close()


@app.get("/api/logs/stats", response_model=ExtractionStatsResponse)
async def get_extraction_stats():
    """Get extraction statistics for today."""
    from app.storage.repositories import ExtractionLogRepository

    db = get_db()
    try:
        repo = ExtractionLogRepository(db)
        stats = repo.get_stats()
        return ExtractionStatsResponse(**stats)
    finally:
        db.close()


@app.get("/api/usage", response_model=List[ApiUsageResponse])
async def get_api_usage():
    """Get API usage for all models today."""
    from app.core.rate_limiter import RateLimitTracker
    from app.core.gemini import GeminiModels

    db = get_db()
    try:
        tracker = RateLimitTracker(db)
        status = tracker.get_status()

        # Include all vision models even if not used today
        result = []
        for config in GeminiModels.VISION_MODELS:
            model_name = config.model.value
            if model_name in status:
                result.append(ApiUsageResponse(
                    model=model_name,
                    **status[model_name]
                ))
            else:
                result.append(ApiUsageResponse(
                    model=model_name,
                    used=0,
                    limit=config.rate_limits.rpd,
                    remaining=config.rate_limits.rpd,
                    exhausted=False,
                ))
        return result
    finally:
        db.close()


# --- Scheduler API ---

class SchedulerStatusResponse(BaseModel):
    """Response model for scheduler status."""
    running: bool
    enabled: bool
    next_run: Optional[str] = None
    last_run: Optional[dict] = None
    items_count: int
    config: dict


class SchedulerRunResponse(BaseModel):
    """Response model for scheduler run trigger."""
    status: str
    message: Optional[str] = None


@app.get("/api/scheduler/status", response_model=SchedulerStatusResponse)
async def scheduler_status():
    """Get current scheduler status."""
    status = get_scheduler_status()
    return SchedulerStatusResponse(**status)


@app.post("/api/scheduler/run-now", response_model=SchedulerRunResponse)
async def scheduler_run_now(background_tasks: BackgroundTasks):
    """Trigger an immediate extraction run."""
    background_tasks.add_task(trigger_run_now)
    return SchedulerRunResponse(
        status="started",
        message="Extraction run started in background"
    )


@app.post("/api/scheduler/pause", response_model=SchedulerRunResponse)
async def scheduler_pause():
    """Pause the scheduler."""
    pause_scheduler()
    return SchedulerRunResponse(
        status="paused",
        message="Scheduler paused"
    )


@app.post("/api/scheduler/resume", response_model=SchedulerRunResponse)
async def scheduler_resume():
    """Resume the scheduler."""
    resume_scheduler()
    return SchedulerRunResponse(
        status="resumed",
        message="Scheduler resumed"
    )


# --- Email API ---

class EmailTestResponse(BaseModel):
    """Response for email test endpoint."""
    success: bool
    message: str
    recipient: Optional[str] = None


class EmailStatusResponse(BaseModel):
    """Response for email status endpoint."""
    enabled: bool
    configured: bool
    recipient: Optional[str] = None


@app.get("/api/email/status", response_model=EmailStatusResponse)
async def email_status():
    """Get email configuration status."""
    from app.core.email_report import get_email_config, is_email_configured

    config = get_email_config()
    return EmailStatusResponse(
        enabled=config["enabled"],
        configured=is_email_configured(),
        recipient=config.get("recipient"),
    )


@app.post("/api/email/test", response_model=EmailTestResponse)
async def email_test():
    """Send a test email to verify configuration."""
    from app.core.email_report import get_email_config, is_email_configured, send_email

    if not is_email_configured():
        return EmailTestResponse(
            success=False,
            message="Email not configured. Set EMAIL_ENABLED=true and configure SMTP settings.",
        )

    config = get_email_config()

    # Build test email content
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2563eb;">Price Spy Test Email</h2>
        <p>This is a test email to verify your email configuration is working.</p>
        <p style="color: #16a34a; font-weight: bold;">If you received this, your daily reports will work!</p>
        <hr style="margin: 20px 0;">
        <p style="color: #666; font-size: 12px;">- Price Spy</p>
    </body>
    </html>
    """

    text = """
Price Spy Test Email

This is a test email to verify your email configuration is working.
If you received this, your daily reports will work!

- Price Spy
"""

    success = send_email(
        to=config["recipient"],
        subject="Price Spy Test Email",
        html=html,
        text=text,
        config=config
    )

    if success:
        return EmailTestResponse(
            success=True,
            message=f"Test email sent successfully!",
            recipient=config["recipient"],
        )
    else:
        return EmailTestResponse(
            success=False,
            message="Failed to send email. Check SMTP settings and credentials.",
        )
