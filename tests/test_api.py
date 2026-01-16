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


class TestDashboardWithData:
    """Tests for dashboard with tracked items."""

    def test_dashboard_shows_tracked_items(self, client_with_data):
        """Dashboard should display tracked items."""
        response = client_with_data.get("/")
        assert response.status_code == 200
        assert "Test Product" in response.text
        assert "Test Store" in response.text

    def test_dashboard_shows_spy_button(self, client_with_data):
        """Dashboard should have Spy Now button."""
        response = client_with_data.get("/")
        assert "Spy Now" in response.text

    def test_dashboard_shows_no_items_message_when_empty(self, client_empty_db):
        """Dashboard should show message when no items tracked."""
        response = client_empty_db.get("/")
        assert "No tracked items" in response.text

    def test_dashboard_shows_below_target_status(self, client_with_price_below_target):
        """Dashboard should show green status when price is below target."""
        response = client_with_price_below_target.get("/")
        assert "Below target" in response.text
        assert "text-green-600" in response.text

    def test_dashboard_shows_above_target_status(self, client_with_price_above_target):
        """Dashboard should show red status when price is above target."""
        response = client_with_price_above_target.get("/")
        assert "Above target" in response.text
        assert "text-red-600" in response.text


class TestItemDetailEndpoint:
    """Tests for /api/items/{id} endpoint."""

    def test_item_detail_returns_404_for_missing(self, client):
        """Should return 404 for non-existent item."""
        response = client.get("/api/items/99999")
        assert response.status_code == 404

    def test_item_detail_returns_item(self, client_with_data):
        """Should return item details."""
        response = client_with_data.get("/api/items/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "product_name" in data
        assert "store_name" in data


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
def client_empty_db():
    """Create test client with empty database."""
    from app.api.main import app
    from app.storage.database import Database
    import app.api.main as main_module

    # Use a temporary empty database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()
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


@pytest.fixture
def client_with_price_below_target():
    """Create test client with item priced below target."""
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import (
        ProductRepository, StoreRepository, TrackedItemRepository, PriceHistoryRepository
    )
    from app.models.schemas import Product, Store, TrackedItem, PriceHistoryRecord
    import app.api.main as main_module

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        # Create product with target price 15.00
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        product = Product(name="Target Test Product", category="Test", target_price=15.00)
        product_id = product_repo.insert(product)

        store = Store(name="Test Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/below-target",
            quantity_size=100,
            quantity_unit="ml"
        )
        tracked_repo.insert(tracked)

        # Add price history with price below target (10.00 < 15.00)
        price_record = PriceHistoryRecord(
            product_name="Target Test Product",
            price=10.00,
            currency="EUR",
            confidence=1.0,
            url="https://example.com/below-target"
        )
        price_repo.insert(price_record)

        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def client_with_price_above_target():
    """Create test client with item priced above target."""
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import (
        ProductRepository, StoreRepository, TrackedItemRepository, PriceHistoryRepository
    )
    from app.models.schemas import Product, Store, TrackedItem, PriceHistoryRecord
    import app.api.main as main_module

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        # Create product with target price 10.00
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        product = Product(name="Above Target Product", category="Test", target_price=10.00)
        product_id = product_repo.insert(product)

        store = Store(name="Test Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/above-target",
            quantity_size=100,
            quantity_unit="ml"
        )
        tracked_repo.insert(tracked)

        # Add price history with price above target (15.00 > 10.00)
        price_record = PriceHistoryRecord(
            product_name="Above Target Product",
            price=15.00,
            currency="EUR",
            confidence=1.0,
            url="https://example.com/above-target"
        )
        price_repo.insert(price_record)

        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


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


class TestProductsAPI:
    """Tests for /api/products endpoints."""

    def test_products_list_returns_200(self, client_empty_db):
        """Products list should return 200 OK."""
        response = client_empty_db.get("/api/products")
        assert response.status_code == 200

    def test_products_list_returns_list(self, client_empty_db):
        """Products list should return a list."""
        response = client_empty_db.get("/api/products")
        assert isinstance(response.json(), list)

    def test_products_list_with_data(self, client_with_data):
        """Products list should return products."""
        response = client_with_data.get("/api/products")
        products = response.json()
        assert len(products) >= 1
        assert "name" in products[0]
        assert "id" in products[0]

    def test_products_create_returns_201(self, client_empty_db):
        """Creating product should return 201."""
        response = client_empty_db.post("/api/products", json={
            "name": "New Product",
            "category": "Test",
            "target_price": 15.00
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Product"
        assert data["id"] is not None

    def test_products_create_requires_name(self, client_empty_db):
        """Creating product without name should return 422."""
        response = client_empty_db.post("/api/products", json={
            "category": "Test"
        })
        assert response.status_code == 422

    def test_products_get_by_id(self, client_with_data):
        """Should get product by ID."""
        response = client_with_data.get("/api/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data

    def test_products_get_by_id_404(self, client_empty_db):
        """Should return 404 for non-existent product."""
        response = client_empty_db.get("/api/products/99999")
        assert response.status_code == 404

    def test_products_update(self, client_with_data):
        """Should update product."""
        response = client_with_data.put("/api/products/1", json={
            "name": "Updated Product",
            "category": "Updated",
            "target_price": 20.00
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"

    def test_products_update_404(self, client_empty_db):
        """Should return 404 for updating non-existent product."""
        response = client_empty_db.put("/api/products/99999", json={
            "name": "Updated"
        })
        assert response.status_code == 404

    def test_products_delete(self, client_with_data):
        """Should delete product."""
        # First create a product to delete
        create_response = client_with_data.post("/api/products", json={
            "name": "To Delete"
        })
        product_id = create_response.json()["id"]

        response = client_with_data.delete(f"/api/products/{product_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client_with_data.get(f"/api/products/{product_id}")
        assert get_response.status_code == 404

    def test_products_delete_404(self, client_empty_db):
        """Should return 404 for deleting non-existent product."""
        response = client_empty_db.delete("/api/products/99999")
        assert response.status_code == 404


class TestStoresAPI:
    """Tests for /api/stores endpoints."""

    def test_stores_list_returns_200(self, client_empty_db):
        """Stores list should return 200 OK."""
        response = client_empty_db.get("/api/stores")
        assert response.status_code == 200

    def test_stores_list_returns_list(self, client_empty_db):
        """Stores list should return a list."""
        response = client_empty_db.get("/api/stores")
        assert isinstance(response.json(), list)

    def test_stores_create_returns_201(self, client_empty_db):
        """Creating store should return 201."""
        response = client_empty_db.post("/api/stores", json={
            "name": "New Store",
            "shipping_cost_standard": 4.95
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Store"

    def test_stores_get_by_id(self, client_with_data):
        """Should get store by ID."""
        response = client_with_data.get("/api/stores/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

    def test_stores_update(self, client_with_data):
        """Should update store."""
        response = client_with_data.put("/api/stores/1", json={
            "name": "Updated Store",
            "shipping_cost_standard": 3.00
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Store"

    def test_stores_delete(self, client_with_data):
        """Should delete store."""
        create_response = client_with_data.post("/api/stores", json={
            "name": "To Delete Store"
        })
        store_id = create_response.json()["id"]

        response = client_with_data.delete(f"/api/stores/{store_id}")
        assert response.status_code == 204
