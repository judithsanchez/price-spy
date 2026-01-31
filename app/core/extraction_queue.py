"""Extraction queue with concurrency management."""

import asyncio
from typing import Any, cast

from app.core.batch_extraction import extract_single_item
from app.core.config import settings
from app.models.schemas import (
    ExtractionContext,
    TrackedItem,
)
from app.storage.database import Database
from app.storage.repositories import (
    CategoryRepository,
    ProductRepository,
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


async def _get_context(
    item: TrackedItem,
    product_repo: ProductRepository,
    category_repo: CategoryRepository,
) -> ExtractionContext:
    """Build extraction context for an item."""
    product = product_repo.get_by_id(item.product_id)
    category = (
        category_repo.get_by_name(product.category)
        if product and product.category
        else None
    )

    return ExtractionContext(
        product_name=product.name if product else "Unknown",
        category=category.name if category else None,
        is_size_sensitive=category.is_size_sensitive if category else False,
        target_size=item.target_size,
        quantity_size=item.quantity_size,
        quantity_unit=item.quantity_unit,
    )


# Redundant _save_results removed as all processing now happens in batch_extraction.py


# Local extract_single_item removed, using batch_extraction.extract_single_item


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

    # Mypy doesn't infer strict optional across the closure properly
    assert api_key is not None

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def extract_with_limit(item: TrackedItem) -> dict[str, Any]:
        """Extract with semaphore limit."""
        # Ensure api_key is treated as str in this scope
        assert api_key is not None
        async with semaphore:
            try:
                return await extract_single_item(
                    item_id=int(item.id or 0), api_key=api_key, db=db
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
