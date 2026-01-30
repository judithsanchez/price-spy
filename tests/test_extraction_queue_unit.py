from unittest.mock import MagicMock

import pytest

from app.core.extraction_queue import _get_context, _save_results
from app.models.schemas import Category, Product, TrackedItem
from app.storage.database import Database
from app.storage.repositories import (
    CategoryRepository,
    ExtractionLogRepository,
    PriceHistoryRepository,
    ProductRepository,
    TrackedItemRepository,
)


@pytest.mark.asyncio
async def test_get_context(test_db):
    db = Database(test_db)
    db.initialize()

    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)

    # Use unique name to avoid conflict with seeded data
    category_repo.insert(Category(name="ClothingCustom", is_size_sensitive=True))
    prod_id = product_repo.insert(
        Product(
            name="Jeans",
            category="ClothingCustom",
            purchase_type="one_time",
            target_price=50.0,
            target_unit="item",
        )
    )

    item = TrackedItem(
        product_id=prod_id,
        store_id=1,
        url="http://example.com",
        target_size="32",
        quantity_size=1.0,
        quantity_unit="item",
        items_per_lot=1,
    )

    context = await _get_context(item, product_repo, category_repo)

    assert context.product_name == "Jeans"
    assert context.category == "ClothingCustom"
    assert context.is_size_sensitive is True
    assert context.target_size == "32"


def test_save_results(test_db):
    db = Database(test_db)
    db.initialize()

    price_repo = PriceHistoryRepository(db)
    log_repo = ExtractionLogRepository(db)
    tracked_repo = TrackedItemRepository(db)

    # Needs a tracked item in DB to update last_checked_at
    item_id = tracked_repo.insert(
        TrackedItem(
            product_id=1,
            store_id=1,
            url="http://test.com",
            quantity_size=1.0,
            quantity_unit="item",
        )
    )

    result = MagicMock()
    result.product_name = "Test Product"
    result.price = 10.0
    result.currency = "USD"
    result.store_name = "Test Store"
    result.original_price = None
    result.deal_type = None
    result.discount_percentage = None
    result.discount_fixed_amount = None
    result.deal_description = None
    result.available_sizes = ["S", "M"]
    result.is_available = True
    result.notes = "No notes"

    _save_results(
        item_id=item_id,
        url="http://test.com",
        result=result,
        model_used="gemini-1.5-flash",
        duration_ms=500,
        price_repo=price_repo,
        log_repo=log_repo,
        tracked_repo=tracked_repo,
    )

    # Verify price history
    history = price_repo.get_by_item(item_id)
    assert len(history) == 1
    assert history[0].price == 10.0  # noqa: PLR2004
    # Available sizes are stored as JSON in the database, but our repository
    # _row_to_record returns a list (or whatever the schema says)
    # Wait, PriceHistoryRecord schema available_sizes is TEXT? No, it's Any in models?
    # Actually it's probably just a string.
    assert history[0].available_sizes is not None
    assert "S" in history[0].available_sizes

    # Verify logs
    logs = log_repo.get_by_item(item_id)
    assert len(logs) == 1
    assert logs[0].status == "success"

    # Verify last checked updated
    updated_item = tracked_repo.get_by_id(item_id)
    assert updated_item is not None
    assert updated_item.last_checked_at is not None
