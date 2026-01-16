"""Tests for SQLite database layer."""

import tempfile
import os
import pytest

from app.storage.database import Database
from app.storage.repositories import (
    PriceHistoryRepository,
    ErrorLogRepository,
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
)
from app.models.schemas import (
    PriceHistoryRecord,
    ErrorRecord,
    Product,
    Store,
    TrackedItem,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


class TestDatabase:
    """Tests for Database class."""

    def test_creates_tables(self, temp_db):
        """Database should create all required tables."""
        db = Database(temp_db)
        db.initialize()

        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]

        # Original tables
        assert "price_history" in table_names
        assert "error_log" in table_names
        # New Slice 2 tables
        assert "products" in table_names
        assert "stores" in table_names
        assert "tracked_items" in table_names

    def test_connection_closes(self, temp_db):
        """Database connection should close properly."""
        db = Database(temp_db)
        db.initialize()
        db.close()

        # Should be able to create a new connection
        db2 = Database(temp_db)
        db2.initialize()
        db2.close()


class TestPriceHistoryRepository:
    """Tests for PriceHistoryRepository."""

    def test_insert_and_retrieve(self, temp_db):
        """Should insert and retrieve price history records."""
        db = Database(temp_db)
        db.initialize()
        repo = PriceHistoryRepository(db)

        record = PriceHistoryRecord(
            product_name="Test Product",
            price=19.99,
            currency="EUR",
            confidence=0.95,
            url="https://example.com/product"
        )

        record_id = repo.insert(record)
        retrieved = repo.get_by_id(record_id)

        assert retrieved is not None
        assert retrieved.product_name == "Test Product"
        assert retrieved.price == 19.99
        assert retrieved.confidence == 0.95

    def test_get_by_url(self, temp_db):
        """Should retrieve all records for a URL."""
        db = Database(temp_db)
        db.initialize()
        repo = PriceHistoryRepository(db)

        url = "https://example.com/product"

        # Insert two records for same URL
        repo.insert(PriceHistoryRecord(
            product_name="Product", price=10.0, confidence=0.9, url=url
        ))
        repo.insert(PriceHistoryRecord(
            product_name="Product", price=9.50, confidence=0.9, url=url
        ))

        records = repo.get_by_url(url)
        assert len(records) == 2

    def test_get_latest_by_url(self, temp_db):
        """Should get the most recent record for a URL (by ID when timestamps match)."""
        db = Database(temp_db)
        db.initialize()
        repo = PriceHistoryRepository(db)

        url = "https://example.com/product"

        repo.insert(PriceHistoryRecord(
            product_name="Product", price=10.0, confidence=0.9, url=url
        ))
        repo.insert(PriceHistoryRecord(
            product_name="Product", price=8.99, confidence=0.9, url=url
        ))

        # Get latest - should be the one with higher ID
        records = repo.get_by_url(url)
        assert len(records) == 2
        # Most recent by created_at DESC, id DESC
        latest = repo.get_latest_by_url(url)
        assert latest is not None


class TestErrorLogRepository:
    """Tests for ErrorLogRepository."""

    def test_insert_error(self, temp_db):
        """Should insert error records."""
        db = Database(temp_db)
        db.initialize()
        repo = ErrorLogRepository(db)

        error = ErrorRecord(
            error_type="api_error",
            message="Rate limit exceeded",
            url="https://example.com"
        )

        error_id = repo.insert(error)
        assert error_id > 0

    def test_get_recent_errors(self, temp_db):
        """Should retrieve recent errors."""
        db = Database(temp_db)
        db.initialize()
        repo = ErrorLogRepository(db)

        repo.insert(ErrorRecord(error_type="timeout", message="Connection timeout"))
        repo.insert(ErrorRecord(error_type="api_error", message="Rate limited"))

        errors = repo.get_recent(limit=10)
        assert len(errors) == 2


class TestProductRepository:
    """Tests for ProductRepository."""

    def test_insert_and_retrieve(self, temp_db):
        """Should insert and retrieve product records."""
        db = Database(temp_db)
        db.initialize()
        repo = ProductRepository(db)

        product = Product(
            name="Campina Slagroom",
            category="Dairy",
            purchase_type="recurring",
            target_price=2.50
        )

        product_id = repo.insert(product)
        retrieved = repo.get_by_id(product_id)

        assert retrieved is not None
        assert retrieved.name == "Campina Slagroom"
        assert retrieved.category == "Dairy"
        assert retrieved.target_price == 2.50

    def test_get_all(self, temp_db):
        """Should retrieve all products."""
        db = Database(temp_db)
        db.initialize()
        repo = ProductRepository(db)

        repo.insert(Product(name="Product 1"))
        repo.insert(Product(name="Product 2"))

        products = repo.get_all()
        assert len(products) == 2

    def test_update_stock(self, temp_db):
        """Should update product stock."""
        db = Database(temp_db)
        db.initialize()
        repo = ProductRepository(db)

        product_id = repo.insert(Product(name="Test", current_stock=5))
        repo.update_stock(product_id, delta=3)

        updated = repo.get_by_id(product_id)
        assert updated.current_stock == 8


class TestStoreRepository:
    """Tests for StoreRepository."""

    def test_insert_and_retrieve(self, temp_db):
        """Should insert and retrieve store records."""
        db = Database(temp_db)
        db.initialize()
        repo = StoreRepository(db)

        store = Store(
            name="Amazon.nl",
            shipping_cost_standard=4.95,
            free_shipping_threshold=50.0
        )

        store_id = repo.insert(store)
        retrieved = repo.get_by_id(store_id)

        assert retrieved is not None
        assert retrieved.name == "Amazon.nl"
        assert retrieved.shipping_cost_standard == 4.95

    def test_get_by_name(self, temp_db):
        """Should find store by name."""
        db = Database(temp_db)
        db.initialize()
        repo = StoreRepository(db)

        repo.insert(Store(name="Amazon.nl"))
        repo.insert(Store(name="Bol.com"))

        amazon = repo.get_by_name("Amazon.nl")
        assert amazon is not None
        assert amazon.name == "Amazon.nl"


class TestTrackedItemRepository:
    """Tests for TrackedItemRepository."""

    def test_insert_and_retrieve(self, temp_db):
        """Should insert and retrieve tracked item records."""
        db = Database(temp_db)
        db.initialize()

        # First create a product and store
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)

        product_id = product_repo.insert(Product(name="Test Product"))
        store_id = store_repo.insert(Store(name="Test Store"))

        item = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/product",
            quantity_size=250,
            quantity_unit="ml"
        )

        item_id = item_repo.insert(item)
        retrieved = item_repo.get_by_id(item_id)

        assert retrieved is not None
        assert retrieved.url == "https://example.com/product"
        assert retrieved.quantity_size == 250

    def test_get_by_url(self, temp_db):
        """Should find tracked item by URL."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Test Store"))

        url = "https://amazon.nl/dp/B12345"
        item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url=url,
            quantity_size=330,
            quantity_unit="ml"
        ))

        found = item_repo.get_by_url(url)
        assert found is not None
        assert found.url == url

    def test_get_active_items(self, temp_db):
        """Should retrieve only active tracked items."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Test Store"))

        # Insert active item
        item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/active",
            quantity_size=100,
            quantity_unit="ml",
            is_active=True
        ))

        # Insert inactive item
        item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/inactive",
            quantity_size=100,
            quantity_unit="ml",
            is_active=False
        ))

        active = item_repo.get_active()
        assert len(active) == 1
        assert active[0].url == "https://example.com/active"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
