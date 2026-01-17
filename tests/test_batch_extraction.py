"""Tests for batch extraction."""

import pytest
from unittest.mock import patch, AsyncMock
import tempfile
import os


class TestBatchExtraction:
    """Tests for batch extraction functionality."""

    @pytest.mark.asyncio
    async def test_batch_extracts_all_active_items(self, db_with_items):
        """Batch extraction should process all active items."""
        from app.core.batch_extraction import extract_all_items
        from app.models.schemas import ExtractionResult

        mock_result = ExtractionResult(
            price=12.99,
            currency="EUR",
            is_available=True,
            product_name="Test",
            store_name="Store"
        )

        with patch('app.core.browser.capture_screenshot', new_callable=AsyncMock) as mock_screenshot, \
             patch('app.core.vision.extract_with_structured_output', new_callable=AsyncMock) as mock_extract:
            mock_screenshot.return_value = b"fake_image"
            mock_extract.return_value = (mock_result, "gemini-2.5-flash")

            results = await extract_all_items(db_with_items)

            # Should have processed 3 items
            assert len(results) == 3
            assert mock_screenshot.call_count == 3
            assert mock_extract.call_count == 3

    @pytest.mark.asyncio
    async def test_batch_skips_inactive_items(self, db_with_inactive_item):
        """Batch extraction should skip inactive items."""
        from app.core.batch_extraction import extract_all_items
        from app.models.schemas import ExtractionResult

        mock_result = ExtractionResult(
            price=12.99,
            currency="EUR",
            is_available=True,
            product_name="Test",
            store_name="Store"
        )

        with patch('app.core.browser.capture_screenshot', new_callable=AsyncMock) as mock_screenshot, \
             patch('app.core.vision.extract_with_structured_output', new_callable=AsyncMock) as mock_extract:
            mock_screenshot.return_value = b"fake_image"
            mock_extract.return_value = (mock_result, "gemini-2.5-flash")

            results = await extract_all_items(db_with_inactive_item)

            # Should only process 2 active items (not the inactive one)
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_batch_continues_on_single_item_failure(self, db_with_items):
        """Batch extraction should continue even if one item fails."""
        from app.core.batch_extraction import extract_all_items
        from app.models.schemas import ExtractionResult

        mock_result = ExtractionResult(
            price=12.99,
            currency="EUR",
            is_available=True,
            product_name="Test",
            store_name="Store"
        )

        call_count = [0]

        async def mock_screenshot_with_failure(url):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Screenshot failed")
            return b"fake_image"

        with patch('app.core.browser.capture_screenshot', side_effect=mock_screenshot_with_failure), \
             patch('app.core.vision.extract_with_structured_output', new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = (mock_result, "gemini-2.5-flash")

            results = await extract_all_items(db_with_items)

            # Should still have 3 results (2 success, 1 error)
            assert len(results) == 3
            success_count = sum(1 for r in results if r.get("status") == "success")
            error_count = sum(1 for r in results if r.get("status") == "error")
            assert success_count == 2
            assert error_count == 1

    @pytest.mark.asyncio
    async def test_batch_returns_summary(self, db_with_items):
        """Batch extraction should return summary with success/error counts."""
        from app.core.batch_extraction import extract_all_items
        from app.models.schemas import ExtractionResult

        mock_result = ExtractionResult(
            price=12.99,
            currency="EUR",
            is_available=True,
            product_name="Test",
            store_name="Store"
        )

        with patch('app.core.browser.capture_screenshot', new_callable=AsyncMock) as mock_screenshot, \
             patch('app.core.vision.extract_with_structured_output', new_callable=AsyncMock) as mock_extract:
            mock_screenshot.return_value = b"fake_image"
            mock_extract.return_value = (mock_result, "gemini-2.5-flash")

            results = await extract_all_items(db_with_items)

            # Check result format
            for result in results:
                assert "item_id" in result
                assert "status" in result
                assert result["status"] in ["success", "error"]


class TestBatchExtractionAPI:
    """Tests for batch extraction API endpoint."""

    def test_extract_all_endpoint_returns_200(self, client_with_items):
        """POST /api/extract/all should return 200."""
        from app.models.schemas import ExtractionResult

        mock_result = ExtractionResult(
            price=12.99,
            currency="EUR",
            is_available=True,
            product_name="Test",
            store_name="Store"
        )

        with patch('app.core.browser.capture_screenshot', new_callable=AsyncMock) as mock_screenshot, \
             patch('app.core.vision.extract_with_structured_output', new_callable=AsyncMock) as mock_extract:
            mock_screenshot.return_value = b"fake_image"
            mock_extract.return_value = (mock_result, "gemini-2.5-flash")

            response = client_with_items.post("/api/extract/all")
            assert response.status_code == 200

    def test_extract_all_returns_results_list(self, client_with_items):
        """POST /api/extract/all should return list of results."""
        from app.models.schemas import ExtractionResult

        mock_result = ExtractionResult(
            price=12.99,
            currency="EUR",
            is_available=True,
            product_name="Test",
            store_name="Store"
        )

        with patch('app.core.browser.capture_screenshot', new_callable=AsyncMock) as mock_screenshot, \
             patch('app.core.vision.extract_with_structured_output', new_callable=AsyncMock) as mock_extract:
            mock_screenshot.return_value = b"fake_image"
            mock_extract.return_value = (mock_result, "gemini-2.5-flash")

            response = client_with_items.post("/api/extract/all")
            data = response.json()

            assert "results" in data
            assert isinstance(data["results"], list)
            assert "total" in data
            assert "success_count" in data
            assert "error_count" in data


@pytest.fixture
def db_with_items():
    """Create database with multiple tracked items."""
    from app.storage.database import Database
    from app.storage.repositories import ProductRepository, StoreRepository, TrackedItemRepository
    from app.models.schemas import Product, Store, TrackedItem

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.initialize()

    product_repo = ProductRepository(db)
    store_repo = StoreRepository(db)
    tracked_repo = TrackedItemRepository(db)

    # Create one product and store
    product = Product(name="Batch Test Product", category="Test", target_price=10.00)
    product_id = product_repo.insert(product)

    store = Store(name="Batch Test Store", shipping_cost_standard=0)
    store_id = store_repo.insert(store)

    # Create 3 tracked items
    for i in range(3):
        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url=f"https://example.com/item-{i}",
            quantity_size=100,
            quantity_unit="ml",
            is_active=True
        )
        tracked_repo.insert(tracked)

    yield db

    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_with_inactive_item():
    """Create database with mix of active and inactive items."""
    from app.storage.database import Database
    from app.storage.repositories import ProductRepository, StoreRepository, TrackedItemRepository
    from app.models.schemas import Product, Store, TrackedItem

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.initialize()

    product_repo = ProductRepository(db)
    store_repo = StoreRepository(db)
    tracked_repo = TrackedItemRepository(db)

    product = Product(name="Test Product", category="Test", target_price=10.00)
    product_id = product_repo.insert(product)

    store = Store(name="Test Store", shipping_cost_standard=0)
    store_id = store_repo.insert(store)

    # Create 2 active items
    for i in range(2):
        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url=f"https://example.com/active-{i}",
            quantity_size=100,
            quantity_unit="ml",
            is_active=True
        )
        tracked_repo.insert(tracked)

    # Create 1 inactive item
    inactive = TrackedItem(
        product_id=product_id,
        store_id=store_id,
        url="https://example.com/inactive",
        quantity_size=100,
        quantity_unit="ml",
        is_active=False
    )
    tracked_repo.insert(inactive)

    yield db

    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def client_with_items():
    """Create test client with tracked items."""
    from fastapi.testclient import TestClient
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import ProductRepository, StoreRepository, TrackedItemRepository
    from app.models.schemas import Product, Store, TrackedItem
    import app.api.main as main_module

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)

        product = Product(name="API Test Product", category="Test", target_price=10.00)
        product_id = product_repo.insert(product)

        store = Store(name="API Test Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        for i in range(3):
            tracked = TrackedItem(
                product_id=product_id,
                store_id=store_id,
                url=f"https://example.com/api-item-{i}",
                quantity_size=100,
                quantity_unit="ml",
                is_active=True
            )
            tracked_repo.insert(tracked)

        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
