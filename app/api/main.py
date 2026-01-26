"""FastAPI application factory."""

import os
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pathlib import Path
from pydantic import BaseModel, ValidationError
from fastapi.responses import JSONResponse

from app.storage.database import Database
from app.storage.repositories import (
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
    PriceHistoryRepository,
    CategoryRepository,
    LabelRepository,
)
from app.core.scheduler import (
    get_scheduler_status,
    trigger_run_now,
    pause_scheduler,
    resume_scheduler,
    lifespan_scheduler,
)
from app.api.deps import get_db, _test_db_path
from app.api.routers import products, categories, units, purchase_types, stores, labels, tracked_items

app = FastAPI(
    title="Price Spy",
    description="Visual price tracking with AI",
    version="0.3.0",
    lifespan=lifespan_scheduler
)

# Include routers
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(units.router)
app.include_router(purchase_types.router)
app.include_router(stores.router)
app.include_router(labels.router)
app.include_router(tracked_items.router)

# Templates directory
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount screenshots directory if it exists
screenshots_dir = Path("screenshots")
if screenshots_dir.exists():
    app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors by returning a 422 JSON response."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
    )


class DashboardItem(BaseModel):
    """View model for dashboard items."""
    id: int
    product_name: str
    store_name: str
    url: str
    price: Optional[float] = None
    currency: str = "EUR"
    target_price: Optional[float] = None
    target_unit: Optional[str] = None
    unit_price: Optional[float] = None
    unit: Optional[str] = None
    is_available: Optional[bool] = None
    notes: Optional[str] = None
    screenshot_path: Optional[str] = None
    last_checked: Optional[str] = None
    original_price: Optional[float] = None
    deal_type: Optional[str] = None
    discount_percentage: Optional[float] = None
    discount_fixed_amount: Optional[float] = None
    deal_description: Optional[str] = None
    is_deal: bool = False
    is_price_drop: bool = False
    is_target_hit: bool = False
    is_best_deal: bool = False


class ExtractResponse(BaseModel):
    """Response for extract endpoint."""
    status: str  # "success", "error"
    item_id: int
    message: Optional[str] = None
    price: Optional[float] = None
    error: Optional[str] = None









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








# --- Brand Sizes API ---




def _get_chart_color(index: int) -> str:
    """Get a color for chart lines based on index."""
    colors = [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
    ]
    return colors[index % len(colors)]


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
            is_available=result.is_available,
            confidence=1.0,  # Structured output is trusted
            url=item.url,
            store_name=result.store_name,
            original_price=result.original_price,
            deal_type=result.deal_type,
            deal_description=result.deal_description,
            notes=result.notes,
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


from app.core.config import settings

# ... imports ...

@app.post("/api/extract/all", response_model=BatchExtractResponse)
async def trigger_batch_extraction():
    """Run price extraction for all active tracked items."""
    from app.core.batch_extraction import extract_all_items, get_batch_summary

    db = get_db()
    try:
        # Use shorter delay in API context (configurable)
        delay = settings.BATCH_DELAY_SECONDS
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

        api_key = settings.GEMINI_API_KEY
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
                is_available=result.is_available,
                confidence=1.0,
                url=item.url,
                store_name=result.store_name,
                original_price=result.original_price,
                deal_type=result.deal_type,
                discount_percentage=result.discount_percentage,
                discount_fixed_amount=result.discount_fixed_amount,
                deal_description=result.deal_description,
                notes=result.notes,
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
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=7)

    db = get_db()
    try:
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)
        cat_repo = CategoryRepository(db)

        tracked_items = tracked_repo.get_all()
        products_map = {}
        low_stock_warnings = []
        price_increase_warnings = []
        graph_data = {
            "labels": [],
            "datasets": []
        }
        
        # Collection of all history points for graph axes
        all_timestamps = set()

        for item in tracked_items:
            # We only care about active items for the dashboard summary
            if not item.is_active:
                continue

            product = product_repo.get_by_id(item.product_id)
            if not product:
                continue
                
            if product.id not in products_map:
                products_map[product.id] = {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "target_price": product.target_price,
                    "target_unit": product.target_unit,
                    "current_stock": product.current_stock,
                    "tracked_items": []
                }
            
            store = store_repo.get_by_id(item.store_id)
            
            # Get latest for card info
            latest_price_rec = price_repo.get_latest_by_url(item.url)
            
            # Get 7-day history for graph and trend
            history = price_repo.get_history_since(item.url, cutoff)
            
            # Trend calculation
            trend = "stable"
            if len(history) >= 2:
                prev_price = history[1].price
                curr_price = history[0].price
                if curr_price and prev_price:
                    if curr_price > prev_price:
                        trend = "up"
                        price_increase_warnings.append({
                            "product_name": product.name,
                            "store_name": store.name if store else "Unknown",
                            "price": curr_price,
                            "previous_price": prev_price,
                            "currency": latest_price_rec.currency if latest_price_rec else "EUR"
                        })
                    elif curr_price < prev_price:
                        trend = "down"

            screenshot_path = f"screenshots/{item.id}.png"
            has_screenshot = Path(screenshot_path).exists()

            # Calculate unit price
            unit_price = None
            unit = None
            if latest_price_rec and latest_price_rec.price:
                unit_price, unit = calculate_volume_price(
                    latest_price_rec.price,
                    item.items_per_lot,
                    item.quantity_size,
                    item.quantity_unit
                )
                unit_price = round(unit_price, 2)

            # Determine if this is a deal
            price = latest_price_rec.price if latest_price_rec else None
            original_price = latest_price_rec.original_price if latest_price_rec else None
            deal_type = latest_price_rec.deal_type if latest_price_rec else None
            deal_description = latest_price_rec.deal_description if latest_price_rec else None

            # Target hit logic: Use unit price if target unit matches, otherwise use total price
            is_target_hit = False
            if price is not None and product.target_price is not None:
                if product.target_unit:
                    from app.core.price_calculator import normalize_unit
                    normalized_target_unit = normalize_unit(product.target_unit)
                    # Normalize our unit just in case
                    normalized_current_unit = normalize_unit(unit) if unit else None
                    
                    if unit_price is not None and normalized_target_unit == normalized_current_unit:
                        is_target_hit = unit_price <= product.target_price
                    else:
                        # Unit mismatch or missing unit_price, don't consider it a hit
                        is_target_hit = False
                else:
                    # No target unit set, use total price
                    is_target_hit = price <= product.target_price

            is_price_drop = trend == "down"
            is_deal = False
            if price is not None:
                has_original_higher = original_price is not None and original_price > price
                has_deal_type = deal_type is not None and deal_type.lower() != "none"
                is_deal = has_original_higher or has_deal_type

            products_map[product.id]["tracked_items"].append({
                "id": item.id,
                "store_name": store.name if store else "Unknown",
                "url": item.url,
                "price": price,
                "currency": latest_price_rec.currency if latest_price_rec else "EUR",
                "unit_price": unit_price,
                "unit": unit,
                "target_unit": product.target_unit,
                "trend": trend,
                "is_deal": is_deal,
                "is_price_drop": is_price_drop,
                "is_target_hit": is_target_hit,
                "is_best_deal": False, # Will be calculated after collecting all sources
                "is_available": latest_price_rec.is_available if latest_price_rec else None,
                "notes": latest_price_rec.notes if latest_price_rec else None,
                "screenshot_path": screenshot_path if has_screenshot else None,
                "original_price": original_price,
                "deal_type": deal_type,
                "deal_description": deal_description,
            })
            
            # Low stock detection
            if latest_price_rec and latest_price_rec.notes:
                notes_lower = latest_price_rec.notes.lower()
                low_stock_keywords = ["low stock", "units left", "stock low", "only", "last units"]
                if any(kw in notes_lower for kw in low_stock_keywords):
                    low_stock_warnings.append({
                        "product_name": product.name,
                        "store_name": store.name if store else "Unknown",
                        "notes": latest_price_rec.notes
                    })
            
            # Prepare graph dataset for this item
            if history:
                item_label = f"{product.name} ({store.name if store else '?'})"
                dataset = {
                    "label": item_label,
                    "data": [],
                    "borderColor": f"hsl({(item.id * 137) % 360}, 70%, 50%)",
                    "fill": False,
                    "tension": 0.1
                }
                for h in reversed(history): # Chronological order
                    ts = h.created_at.strftime("%Y-%m-%d %H:%M")
                    all_timestamps.add(ts)
                    dataset["data"].append({"x": ts, "y": h.price})
                graph_data["datasets"].append(dataset)

        # Sort all timestamps to create global labels
        sorted_labels = sorted(list(all_timestamps))
        graph_data["labels"] = sorted_labels
        # Sort products by name
        sorted_products = sorted(products_map.values(), key=lambda p: p["name"])
        
        # Identify Best Deal per product (lowest available unit price)
        # And set summary flags for sorting
        for p in sorted_products:
            p["has_best_deal"] = False
            p["has_target_hit"] = any(it["is_target_hit"] for it in p["tracked_items"])
            p["has_deal"] = any(it["is_deal"] or it["is_price_drop"] for it in p["tracked_items"])
            
            # Only consider items with unit prices and that are available (or availability unknown)
            valid_items = [it for it in p["tracked_items"] if it["unit_price"] is not None and it["is_available"] is not False]
            if len(valid_items) > 1:
                # Find the one with the minimum unit price
                best_item = min(valid_items, key=lambda x: x["unit_price"])
                for it in p["tracked_items"]:
                    if it["id"] == best_item["id"]:
                        it["is_best_deal"] = True
                        p["has_best_deal"] = True
        
        # Advanced sorting: Target Hits > Deals > Name
        sorted_products.sort(key=lambda p: (not p["has_target_hit"], not p["has_deal"], p["name"]))
        
        # Calculate global deals for the banner
        all_deals = []
        for p in sorted_products:
            for item in p["tracked_items"]:
                if item["is_target_hit"] or item["is_deal"]:
                    all_deals.append({
                        "product_name": p["name"],
                        "price": item["price"],
                        "currency": item["currency"],
                        "unit_price": item["unit_price"],
                        "unit": item["unit"],
                        "target_price": p["target_price"],
                        "target_unit": p["target_unit"],
                        "is_target_hit": item["is_target_hit"]
                    })

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "products": sorted_products,
                "deals": all_deals,
                "low_stock": low_stock_warnings,
                "price_increases": price_increase_warnings,
                "graph_data": graph_data,
                "has_any_items": len(tracked_items) > 0
            }
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


@app.get("/categories")
async def categories_page(request: Request):
    """Render categories management page."""
    return templates.TemplateResponse(request, "categories.html", {})


@app.get("/labels")
async def labels_page(request: Request):
    """Render labels management page."""
    return templates.TemplateResponse(request, "labels.html", {})









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
