"""Extraction queue with concurrency management."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, cast

from app.core.browser import capture_screenshot
from app.core.config import settings
from app.core.rate_limiter import RateLimitTracker
from app.core.vision import extract_with_structured_output
from app.models.schemas import (
    ExtractionContext,
    ExtractionLog,
    PriceHistoryRecord,
    TrackedItem,
)
from app.storage.database import Database
from app.storage.repositories import (
    CategoryRepository,
    ExtractionLogRepository,
    PriceHistoryRepository,
    ProductRepository,
    TrackedItemRepository,
)

# Maximum concurrent extractions (respects Gemini's 15 RPM limit)
MAX_CONCURRENT = 10


def _raise_item_not_found(item_id: int) -> None:
    """Raise ValueError when item is not found."""
    msg = f"Item {item_id} not found"
    raise ValueError(msg)


def get_api_key() -> str | None:
    """Get Gemini API key from environment."""
    return settings.GEMINI_API_KEY


async def extract_single_item(
    item_id: int, url: str, api_key: str, db: Database
) -> dict[str, Any]:
    """
    Extract price for a single tracked item.

    Args:
        item_id: The tracked item ID
        url: The URL to extract from
        api_key: Gemini API key
        db: Database connection

    Returns:
        Dict with item_id, status, and optional price/error
    """

    tracked_repo = TrackedItemRepository(db)
    price_repo = PriceHistoryRepository(db)
    log_repo = ExtractionLogRepository(db)
    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)
    tracker = RateLimitTracker(db)

    start_time = time.time()
    model_used = None

    try:
        item = tracked_repo.get_by_id(item_id)
        if not item:
            _raise_item_not_found(item_id)

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

        # Capture screenshot
        screenshot_bytes = await capture_screenshot(
            url,
            target_size=str(item.target_size) if item and item.target_size else None,
        )

        # Save screenshot
        screenshot_path = Path(f"screenshots/{item_id}.png")
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(screenshot_bytes)

        # Extract price with rate limiting
        result, model_used = await extract_with_structured_output(
            screenshot_bytes, api_key, tracker, context=context
        )

        duration_ms = int((time.time() - start_time) * 1000)

        # Save to price history
        record = PriceHistoryRecord(
            item_id=item_id,
            product_name=result.product_name,
            price=result.price,
            currency=result.currency,
            confidence=1.0,
            url=url,
            store_name=result.store_name,
            original_price=result.original_price,
            deal_type=result.deal_type,
            discount_percentage=result.discount_percentage,
            discount_fixed_amount=result.discount_fixed_amount,
            deal_description=result.deal_description,
            available_sizes=json.dumps(result.available_sizes)
            if result.available_sizes
            else None,
            is_available=result.is_available,
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

    except Exception as e:
        # Log failed extraction
        duration_ms = int((time.time() - start_time) * 1000)
        logging.exception("Extraction failed for item %s", item_id)

        log_repo.insert(
            ExtractionLog(
                tracked_item_id=item_id,
                status="error",
                model_used=model_used,
                error_message=str(e)[:2000],
                duration_ms=duration_ms,
            )
        )

        return {
            "item_id": item_id,
            "status": "error",
            "error": str(e),
            "duration_ms": duration_ms,
        }

    else:
        return {
            "item_id": item_id,
            "status": "success",
            "price": result.price,
            "currency": result.currency,
            "model_used": model_used,
            "duration_ms": duration_ms,
        }


async def process_extraction_queue(
    items: list[TrackedItem], db: Database
) -> list[dict[str, Any]]:
    """
    Process extraction queue with concurrency limit.

    Uses asyncio.Semaphore to limit concurrent extractions to MAX_CONCURRENT.

    Args:
        items: List of tracked items to process
        db: Database connection

    Returns:
        List of extraction results for each item
    """
    if not items:
        return []

    api_key = get_api_key()
    if not api_key:
        return [
            {
                "item_id": item.id,
                "status": "error",
                "error": "GEMINI_API_KEY not configured",
            }
            for item in items
        ]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def extract_with_limit(item: TrackedItem) -> dict[str, Any]:
        """Extract with semaphore limit."""
        async with semaphore:
            try:
                return await extract_single_item(
                    item_id=int(item.id or 0), url=str(item.url), api_key=api_key, db=db
                )
            except Exception as e:
                return {"item_id": item.id, "status": "error", "error": str(e)}

    # Process all items with concurrency limit
    tasks = [extract_with_limit(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert any exceptions to error results
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append(
                {"item_id": items[i].id, "status": "error", "error": str(result)}
            )
        else:
            final_results.append(cast(dict[str, Any], result))

    return final_results


def get_queue_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Generate summary statistics from queue results.

    Args:
        results: List of extraction results

    Returns:
        Summary with total, success_count, error_count
    """
    success_count = sum(1 for r in results if r.get("status") == "success")
    error_count = sum(1 for r in results if r.get("status") == "error")

    return {
        "total": len(results),
        "success_count": success_count,
        "error_count": error_count,
        "results": results,
    }
