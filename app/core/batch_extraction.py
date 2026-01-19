"""Batch extraction for all tracked items."""

import os
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.storage.database import Database
from app.storage.repositories import (
    TrackedItemRepository,
    PriceHistoryRepository,
    ExtractionLogRepository,
)
from app.models.schemas import PriceHistoryRecord, ExtractionLog
from app.core.rate_limiter import RateLimitTracker


async def extract_single_item(
    item_id: int,
    url: str,
    api_key: str,
    db: Database,
    tracker: Optional[RateLimitTracker] = None,
    delay_seconds: float = 0
) -> Dict[str, Any]:
    """
    Extract price for a single tracked item.

    Args:
        item_id: The tracked item ID
        url: The URL to extract from
        api_key: Gemini API key
        db: Database connection
        tracker: Optional rate limit tracker
        delay_seconds: Delay before extraction (for rate limiting)

    Returns:
        Dict with item_id, status, and optional price/error
    """
    from app.core.browser import capture_screenshot
    from app.core.vision import extract_with_structured_output

    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)

    tracked_repo = TrackedItemRepository(db)
    price_repo = PriceHistoryRepository(db)
    log_repo = ExtractionLogRepository(db)

    start_time = time.time()
    model_used = None

    try:
        # Capture screenshot
        screenshot_bytes = await capture_screenshot(url)

        # Save screenshot
        screenshot_path = Path(f"screenshots/{item_id}.png")
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(screenshot_bytes)

        # Extract price with rate limiting
        if tracker:
            result, model_used = await extract_with_structured_output(
                screenshot_bytes, api_key, tracker
            )
        else:
            result, model_used = await extract_with_structured_output(
                screenshot_bytes, api_key
            )

        duration_ms = int((time.time() - start_time) * 1000)

        # Save to price history
        record = PriceHistoryRecord(
            product_name=result.product_name,
            price=result.price,
            currency=result.currency,
            confidence=1.0,
            url=url,
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

        return {
            "item_id": item_id,
            "status": "success",
            "price": result.price,
            "currency": result.currency,
            "model_used": model_used,
            "duration_ms": duration_ms
        }

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

        return {
            "item_id": item_id,
            "status": "error",
            "error": error_msg,
            "duration_ms": duration_ms
        }


from app.core.config import settings

# ...

async def extract_all_items(
    db: Database,
    delay_seconds: float = 5.0
) -> List[Dict[str, Any]]:
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
        return [{
            "item_id": None,
            "status": "error",
            "error": "GEMINI_API_KEY not configured"
        }]

    tracked_repo = TrackedItemRepository(db)
    tracker = RateLimitTracker(db)

    items = tracked_repo.get_active()
    results = []

    for i, item in enumerate(items):
        # Add delay between items (except for the first one)
        delay = delay_seconds if i > 0 else 0

        result = await extract_single_item(
            item_id=item.id,
            url=item.url,
            api_key=api_key,
            db=db,
            tracker=tracker,
            delay_seconds=delay
        )
        results.append(result)

    return results


def get_batch_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        "results": results
    }
