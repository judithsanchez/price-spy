"""Extraction queue with concurrency management."""

import os
import asyncio
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.storage.database import Database
from app.storage.repositories import (
    TrackedItemRepository,
    PriceHistoryRepository,
    ExtractionLogRepository,
)
from app.models.schemas import PriceHistoryRecord, ExtractionLog, TrackedItem
from app.core.rate_limiter import RateLimitTracker

# Maximum concurrent extractions (respects Gemini's 15 RPM limit)
MAX_CONCURRENT = 10


def get_api_key() -> Optional[str]:
    """Get Gemini API key from environment."""
    return os.getenv("GEMINI_API_KEY")


async def extract_single_item(
    item_id: int,
    url: str,
    api_key: str,
    db: Database
) -> Dict[str, Any]:
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
    from app.core.browser import capture_screenshot
    from app.core.vision import extract_with_structured_output

    tracked_repo = TrackedItemRepository(db)
    price_repo = PriceHistoryRepository(db)
    log_repo = ExtractionLogRepository(db)
    tracker = RateLimitTracker(db)

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


async def process_extraction_queue(
    items: List[TrackedItem],
    db: Database
) -> List[Dict[str, Any]]:
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
        return [{
            "item_id": item.id,
            "status": "error",
            "error": "GEMINI_API_KEY not configured"
        } for item in items]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def extract_with_limit(item: TrackedItem) -> Dict[str, Any]:
        """Extract with semaphore limit."""
        async with semaphore:
            try:
                return await extract_single_item(
                    item_id=item.id,
                    url=item.url,
                    api_key=api_key,
                    db=db
                )
            except Exception as e:
                return {
                    "item_id": item.id,
                    "status": "error",
                    "error": str(e)
                }

    # Process all items with concurrency limit
    tasks = [extract_with_limit(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Convert any exceptions to error results
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append({
                "item_id": items[i].id,
                "status": "error",
                "error": str(result)
            })
        else:
            final_results.append(result)

    return final_results


def get_queue_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        "results": results
    }
