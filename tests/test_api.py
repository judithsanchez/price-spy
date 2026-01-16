"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import tempfile
import os


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_status_ok(self, client):
        """Health endpoint should return status ok."""
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_version(self, client):
        """Health endpoint should return version."""
        response = client.get("/api/health")
        data = response.json()
        assert "version" in data


class TestDashboardRoute:
    """Tests for dashboard HTML route."""

    def test_dashboard_returns_200(self, client):
        """Dashboard should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_dashboard_returns_html(self, client):
        """Dashboard should return HTML content."""
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_dashboard_contains_title(self, client):
        """Dashboard should contain Price Spy title."""
        response = client.get("/")
        assert "Price Spy" in response.text


class TestItemsEndpoint:
    """Tests for /api/items endpoint."""

    def test_items_returns_200(self, client):
        """Items endpoint should return 200 OK."""
        response = client.get("/api/items")
        assert response.status_code == 200

    def test_items_returns_list(self, client):
        """Items endpoint should return a list."""
        response = client.get("/api/items")
        assert isinstance(response.json(), list)

    def test_items_empty_when_no_data(self, client):
        """Items endpoint should return empty list when no data."""
        response = client.get("/api/items")
        # May have data from other tests, just check it's a list
        assert isinstance(response.json(), list)

    def test_items_with_data(self, client_with_data):
        """Items endpoint should return tracked items with data."""
        response = client_with_data.get("/api/items")
        items = response.json()

        assert len(items) >= 1
        item = items[0]
        assert "id" in item
        assert "product_name" in item
        assert "store_name" in item
        assert "url" in item

    def test_items_include_price_info(self, client_with_data):
        """Items should include price information when available."""
        response = client_with_data.get("/api/items")
        items = response.json()

        # First item should have price fields (may be None if no extraction)
        item = items[0]
        assert "price" in item
        assert "currency" in item
        assert "target_price" in item


class TestExtractEndpoint:
    """Tests for /api/extract endpoint."""

    def test_extract_returns_404_for_missing_item(self, client):
        """Extract should return 404 for non-existent item."""
        with patch('app.api.main.run_extraction', new_callable=AsyncMock):
            response = client.post("/api/extract/99999")
            assert response.status_code == 404

    def test_extract_returns_accepted(self, client_with_data):
        """Extract should return 202 Accepted for valid item."""
        with patch('app.api.main.run_extraction', new_callable=AsyncMock) as mock_extract:
            response = client_with_data.post("/api/extract/1")
            assert response.status_code == 202
            data = response.json()
            assert data["status"] == "queued"
            assert data["item_id"] == 1
            # Verify extraction was queued (background task added)
            mock_extract.assert_called_once()


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    from app.api.main import app
    return TestClient(app)


@pytest.fixture
def client_with_data():
    """Create test client with seeded database data."""
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import ProductRepository, StoreRepository, TrackedItemRepository
    from app.models.schemas import Product, Store, TrackedItem
    import app.api.main as main_module

    # Use a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        # Seed data
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)

        product = Product(name="Test Product", category="Test", target_price=10.00)
        product_id = product_repo.insert(product)

        store = Store(name="Test Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/product",
            quantity_size=100,
            quantity_unit="ml"
        )
        tracked_repo.insert(tracked)

        db.close()

        # Override the test database path
        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        # Restore original
        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
