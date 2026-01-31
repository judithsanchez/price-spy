from unittest.mock import AsyncMock, patch

import pytest

from app.core import batch_extraction
from app.models.schemas import Category, ExtractionResult, Product, Store, TrackedItem
from app.storage.database import Database
from app.storage.repositories import (
    CategoryRepository,
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
)

# Constants for lint compliance
PRICE_TEN = 10.0
ATTEMPTS_TWO = 2
ATTEMPTS_THREE = 3


@pytest.mark.asyncio
async def test_extract_single_item_retry_on_blocked(test_db):
    db = Database(test_db)
    db.initialize()

    # Setup data
    cat_repo = CategoryRepository(db)
    prod_repo = ProductRepository(db)
    tracked_repo = TrackedItemRepository(db)
    store_repo = StoreRepository(db)

    # Insert necessary related data
    store_id: int
    try:
        store_id = store_repo.insert(Store(name="TestStore1"))
    except Exception:
        store = store_repo.get_by_name("TestStore1")
        assert store is not None
        assert store.id is not None
        store_id = store.id

    cat_repo.insert(Category(name="TestCat", is_size_sensitive=False))
    p_id = prod_repo.insert(Product(name="TestProd", category="TestCat"))
    item_id = tracked_repo.insert(
        TrackedItem(
            product_id=p_id,
            store_id=store_id,
            url="http://ex.com",
            quantity_size=1.0,
            quantity_unit="unit",
        )
    )

    # Patch the references where they are USED in batch_extraction
    with (
        patch(
            "app.core.batch_extraction.capture_screenshot", new_callable=AsyncMock
        ) as mock_screenshot,
        patch(
            "app.core.batch_extraction.extract_with_structured_output",
            new_callable=AsyncMock,
        ) as mock_extract,
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        mock_screenshot.return_value = b"fake_bytes"

        blocked_result = ExtractionResult(
            price=0.0,
            currency="N/A",
            is_available=True,
            product_name="TestProd",
            is_blocked=True,
            blocking_type="cookie_banner",
        )
        success_result = ExtractionResult(
            price=10.0,
            currency="EUR",
            is_available=True,
            product_name="TestProd",
            is_blocked=False,
            blocking_type="none",
        )

        mock_extract.side_effect = [(blocked_result, "m1"), (success_result, "m1")]

        result = await batch_extraction.extract_single_item(item_id, "key", db)

        assert result["status"] == "success"
        # We check price from the PriceHistoryRecord if needed
        assert mock_extract.call_count == ATTEMPTS_TWO
        assert mock_screenshot.call_count == ATTEMPTS_TWO


@pytest.mark.asyncio
async def test_extract_single_item_hard_block_all_attempts(test_db):
    db = Database(test_db)
    db.initialize()

    # Setup data
    cat_repo = CategoryRepository(db)
    prod_repo = ProductRepository(db)
    tracked_repo = TrackedItemRepository(db)
    store_repo = StoreRepository(db)

    store_id: int
    try:
        store_id = store_repo.insert(Store(name="TestStore2"))
    except Exception:
        store = store_repo.get_by_name("TestStore2")
        assert store is not None
        assert store.id is not None
        store_id = store.id

    cat_repo.insert(Category(name="TestCat", is_size_sensitive=False))
    p_id = prod_repo.insert(Product(name="TestProd", category="TestCat"))
    item_id = tracked_repo.insert(
        TrackedItem(
            product_id=p_id,
            store_id=store_id,
            url="http://ex.com",
            quantity_size=1.0,
            quantity_unit="unit",
        )
    )

    with (
        patch(
            "app.core.batch_extraction.capture_screenshot", new_callable=AsyncMock
        ) as mock_screenshot,
        patch(
            "app.core.batch_extraction.extract_with_structured_output",
            new_callable=AsyncMock,
        ) as mock_extract,
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        mock_screenshot.return_value = b"fake_bytes"

        blocked_result = ExtractionResult(
            price=0.0,
            currency="N/A",
            is_available=True,
            product_name="TestProd",
            is_blocked=True,
            blocking_type="login_wall",
        )

        mock_extract.return_value = (blocked_result, "m1")

        result = await batch_extraction.extract_single_item(item_id, "key", db)

        assert result["status"] == "error"
        assert mock_extract.call_count == ATTEMPTS_THREE
        assert mock_screenshot.call_count == ATTEMPTS_THREE
