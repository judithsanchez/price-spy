"""Batch extraction for all tracked items."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

from app.core.browser import capture_screenshot
from app.core.config import settings
from app.core.rate_limiter import RateLimitTracker
from app.core.vision import extract_with_structured_output
from app.models.schemas import (
    ExtractionContext,
    ExtractionLog,
    ExtractionResult,
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

logger = logging.getLogger(__name__)


class ExtractionError(RuntimeError):
    """Custom exception for extraction failures."""


async def _get_extraction_context(
    item_id: int, db: Database
) -> tuple[ExtractionContext | None, Any | None, TrackedItem | None]:
    """Fetch database records and build extraction context."""
    tracked_repo = TrackedItemRepository(db)
    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)

    item = tracked_repo.get_by_id(item_id)
    if not item:
        return None, None, None

    product = product_repo.get_by_id(item.product_id)
    category = (
        category_repo.get_by_name(product.category)
        if product and product.category
        else None
    )

    context = ExtractionContext(
        product_name=str(product.name) if product else "Unknown",
        category=str(category.name) if category else None,
        is_size_sensitive=bool(category.is_size_sensitive) if category else False,
        target_size=str(item.target_size) if item.target_size else None,
        quantity_size=float(item.quantity_size),
        quantity_unit=str(item.quantity_unit),
    )
    return context, product, item


async def _run_extraction_loop(
    api_key: str,
    context: ExtractionContext,
    tracker: RateLimitTracker | None,
    item: TrackedItem,
    db: Database,
    start_time: float,
) -> tuple[ExtractionResult | None, str | None]:
    """Run the extraction retry loop."""
    log_repo = ExtractionLogRepository(db)
    item_id = int(item.id or 0)
    url = item.url
    max_retries = 2
    attempt = 0
    result = None
    model_used = None

    while attempt <= max_retries:
        attempt += 1
        logger.info(
            "Price extraction attempt %d/%d",
            attempt,
            max_retries + 1,
            extra={"item_id": item_id, "url": url},
        )

        screenshot_bytes = await capture_screenshot(url, target_size=item.target_size)
        screenshot_path = Path(f"screenshots/{item_id}.png")
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(screenshot_bytes)
        context.screenshot_path = str(screenshot_path)

        if tracker:
            result, model_used = await extract_with_structured_output(
                screenshot_bytes, api_key, tracker, context=context
            )
        else:
            result, model_used = await extract_with_structured_output(
                screenshot_bytes, api_key, context=context
            )

        if not result:
            break

        is_soft_failure = result.is_blocked or result.is_screenshot_faulty
        if is_soft_failure and attempt <= max_retries:
            logger.warning(
                "Soft failure detected, retrying...",
                extra={
                    "item_id": item_id,
                    "blocking_type": result.blocking_type,
                    "is_screenshot_faulty": result.is_screenshot_faulty,
                },
            )
            log_repo.insert(
                ExtractionLog(
                    tracked_item_id=item_id,
                    status="error",
                    model_used=model_used,
                    error_message=f"Retry {attempt}: {result.blocking_type}",
                    duration_ms=int((time.time() - start_time) * 1000),
                    blocking_type=result.blocking_type,
                    is_screenshot_faulty=result.is_screenshot_faulty,
                )
            )
            await asyncio.sleep(5 * attempt)
            continue
        break
    return result, model_used


async def _process_extraction_result(
    item_id: int,
    url: str,
    result: ExtractionResult,
    model_used: str | None,
    duration_ms: int,
    db: Database,
) -> dict[str, Any]:
    """Save results to DB and return summary."""
    price_repo = PriceHistoryRepository(db)
    log_repo = ExtractionLogRepository(db)
    tracked_repo = TrackedItemRepository(db)

    if not result.is_blocked and result.price > 0:
        price_repo.insert(
            PriceHistoryRecord(
                item_id=item_id,
                product_name=result.product_name,
                price=result.price,
                currency=result.currency,
                is_available=result.is_available,
                is_size_matched=result.is_size_matched,
                confidence=1.0,
                url=url,
                store_name=result.store_name,
                original_price=result.original_price,
                deal_type=result.deal_type,
                discount_percentage=result.discount_percentage,
                discount_fixed_amount=result.discount_fixed_amount,
                deal_description=result.deal_description,
                notes=result.notes,
                available_sizes=json.dumps(result.available_sizes)
                if result.available_sizes
                else None,
            )
        )

    log_repo.insert(
        ExtractionLog(
            tracked_item_id=item_id,
            status="success" if not result.is_blocked else "error",
            model_used=model_used,
            price=result.price if result.price > 0 else None,
            currency=result.currency if result.currency != "N/A" else None,
            duration_ms=duration_ms,
            blocking_type=result.blocking_type,
            is_screenshot_faulty=result.is_screenshot_faulty,
            error_message=f"Blocked: {result.blocking_type}"
            if result.is_blocked
            else None,
        )
    )
    tracked_repo.set_last_checked(item_id)

    return {
        "item_id": item_id,
        "status": "error" if result.is_blocked else "success",
        "price": result.price,
        "currency": result.currency,
        "original_price": result.original_price,
        "deal_type": result.deal_type,
        "discount_percentage": result.discount_percentage,
        "discount_fixed_amount": result.discount_fixed_amount,
        "deal_description": result.deal_description,
        "model_used": model_used,
        "duration_ms": duration_ms,
    }


async def extract_single_item(
    item_id: int,
    api_key: str,
    db: Database,
    tracker: RateLimitTracker | None = None,
    delay_seconds: float = 0,
) -> dict[str, Any]:
    """Extract price for a single tracked item via AI vision."""
    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)

    start_time = time.time()
    log_repo = ExtractionLogRepository(db)

    # Initial data fetching (outside try to avoid TRY301)
    context, _product, item = await _get_extraction_context(item_id, db)
    if not context or not item:
        duration_ms = int((time.time() - start_time) * 1000)
        log_repo.insert(
            ExtractionLog(
                tracked_item_id=item_id,
                status="error",
                error_message="Item not found",
                duration_ms=duration_ms,
            )
        )
        return {
            "item_id": item_id,
            "status": "error",
            "error": "Item not found",
            "duration_ms": duration_ms,
        }

    try:
        result, model_used = await _run_extraction_loop(
            api_key, context, tracker, item, db, start_time
        )
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        log_repo.insert(
            ExtractionLog(
                tracked_item_id=item_id,
                status="error",
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

    if not result:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "item_id": item_id,
            "status": "error",
            "error": "Extraction failed",
            "duration_ms": duration_ms,
        }

    duration_ms = int((time.time() - start_time) * 1000)
    return await _process_extraction_result(
        item_id, item.url, result, model_used, duration_ms, db
    )


async def extract_all_items(
    db: Database, delay_seconds: float = 5.0
) -> list[dict[str, Any]]:
    """
    Extract prices for all active tracked items.

    Args:
        db: Database connection
        delay_seconds: Delay between extractions (default 5s for rate limiting)

    Returns:
        List of extraction results for each item
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return [
            {
                "item_id": None,
                "status": "error",
                "error": "GEMINI_API_KEY not configured",
            }
        ]

    tracked_repo = TrackedItemRepository(db)
    tracker = RateLimitTracker(db)

    items = tracked_repo.get_active()
    results = []

    for i, item in enumerate(items):
        # Add delay between items (except for the first one)
        delay = delay_seconds if i > 0 else 0

        result = await extract_single_item(
            item_id=int(item.id or 0),
            api_key=api_key,
            db=db,
            tracker=tracker,
            delay_seconds=delay,
        )
        results.append(result)

    return results


def get_batch_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Generate summary statistics from batch extraction results.

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
