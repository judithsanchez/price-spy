import os
import time
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_db
from app.core.config import settings
from app.core.browser import capture_screenshot
from app.core.vision import extract_with_structured_output
from app.core.batch_extraction import extract_all_items, get_batch_summary
from app.core.rate_limiter import RateLimitTracker
from app.models.schemas import PriceHistoryRecord, ExtractionLog, ExtractionContext
from app.storage.database import Database
from app.storage.repositories import (
    TrackedItemRepository,
    PriceHistoryRepository,
    ExtractionLogRepository,
    ProductRepository,
    CategoryRepository,
)

router = APIRouter(prefix="/api/extract", tags=["Extraction"])


class ExtractResponse(BaseModel):
    """Response for extract endpoint."""

    status: str  # "success", "error"
    item_id: int
    message: Optional[str] = None
    price: Optional[float] = None
    error: Optional[str] = None


class BatchExtractResponse(BaseModel):
    """Response for batch extract endpoint."""

    total: int
    success_count: int
    error_count: int
    results: list


async def run_extraction(item_id: int, db_path: str):
    """Background task to run price extraction."""
    db = Database(db_path)
    db.initialize()

    try:
        tracked_repo = TrackedItemRepository(db)
        product_repo = ProductRepository(db)
        category_repo = CategoryRepository(db)
        price_repo = PriceHistoryRepository(db)

        item = tracked_repo.get_by_id(item_id)
        if not item:
            return

        product = product_repo.get_by_id(item.product_id)
        category = (
            category_repo.get_by_name(product.category)
            if product and product.category
            else None
        )

        # Build context
        context = ExtractionContext(
            product_name=product.name if product else "Unknown",
            category=category.name if category else None,
            is_size_sensitive=category.is_size_sensitive if category else False,
            target_size=item.target_size,
            quantity_size=item.quantity_size,
            quantity_unit=item.quantity_unit,
        )

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return

        # Capture screenshot
        screenshot_bytes = await capture_screenshot(
            item.url, target_size=item.target_size if item else None
        )

        # Save screenshot
        screenshot_path = Path(f"screenshots/{item_id}.png")
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(screenshot_bytes)

        context.screenshot_path = str(screenshot_path)

        # Extract price
        result, _ = await extract_with_structured_output(
            screenshot_bytes, api_key, context=context
        )

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


@router.post("/all", response_model=BatchExtractResponse)
async def trigger_batch_extraction(db=Depends(get_db)):
    """Run price extraction for all active tracked items."""
    try:
        # Use shorter delay in API context (configurable)
        delay = settings.BATCH_DELAY_SECONDS
        results = await extract_all_items(db, delay_seconds=delay)
        summary = get_batch_summary(results)
        return BatchExtractResponse(**summary)
    finally:
        db.close()


@router.post("/{item_id}", response_model=ExtractResponse)
async def trigger_extraction(item_id: int, db=Depends(get_db)):
    """Run price extraction for a tracked item with rate limiting and logging."""
    start_time = time.time()
    model_used = None

    try:
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)
        log_repo = ExtractionLogRepository(db)
        tracker = RateLimitTracker(db)
        product_repo = ProductRepository(db)
        category_repo = CategoryRepository(db)

        item = tracked_repo.get_by_id(item_id)

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        product = product_repo.get_by_id(item.product_id)
        category = (
            category_repo.get_by_name(product.category)
            if product and product.category
            else None
        )

        # Build context
        context = ExtractionContext(
            product_name=product.name if product else "Unknown",
            category=category.name if category else None,
            is_size_sensitive=category.is_size_sensitive if category else False,
            target_size=item.target_size,
            quantity_size=item.quantity_size,
            quantity_unit=item.quantity_unit,
        )

        api_key = settings.GEMINI_API_KEY
        if not api_key:
            from app.core.error_logger import log_error_to_db

            log_error_to_db(
                error_type="config_error",
                message="GEMINI_API_KEY not configured",
                url=item.url,
            )
            log_repo.insert(
                ExtractionLog(
                    tracked_item_id=item_id,
                    status="error",
                    error_message="GEMINI_API_KEY not configured",
                )
            )
            return ExtractResponse(
                status="error", item_id=item_id, error="GEMINI_API_KEY not configured"
            )

        try:
            # Capture screenshot
            screenshot_bytes = await capture_screenshot(
                item.url, target_size=item.target_size if item else None
            )

            # Save screenshot
            screenshot_path = Path(f"screenshots/{item_id}.png")
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            screenshot_path.write_bytes(screenshot_bytes)

            # Update context with screenshot path for logging
            context.screenshot_path = str(screenshot_path)

            # Extract price with rate limiting
            result, model_used = await extract_with_structured_output(
                screenshot_bytes, api_key, tracker, context=context
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
            log_repo.insert(
                ExtractionLog(
                    tracked_item_id=item_id,
                    status="success",
                    model_used=model_used,
                    price=result.price,
                    currency=result.currency,
                    duration_ms=duration_ms,
                )
            )

            # Update last checked time
            tracked_repo.set_last_checked(item_id)

            return ExtractResponse(
                status="success",
                item_id=item_id,
                message=f"Extracted price: {result.currency} {result.price:.2f}",
                price=result.price,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            error_msg = str(e)

            # Log failed extraction
            log_repo.insert(
                ExtractionLog(
                    tracked_item_id=item_id,
                    status="error",
                    model_used=model_used,
                    error_message=error_msg[:2000],
                    duration_ms=duration_ms,
                )
            )

            # Parse common errors for friendlier messages
            if "429" in error_msg or "quota" in error_msg.lower():
                error_msg = "Gemini API quota exceeded. Try again later."
            elif "401" in error_msg or "API key" in error_msg.lower():
                error_msg = "Invalid Gemini API key."
            elif "exhausted" in error_msg.lower():
                error_msg = "All AI models exhausted for today. Try again tomorrow."

            return ExtractResponse(status="error", item_id=item_id, error=error_msg)

    finally:
        db.close()
