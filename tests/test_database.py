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
    ExtractionLogRepository,
)
from app.models.schemas import (
    PriceHistoryRecord,
    ErrorRecord,
    Product,
    Store,
    TrackedItem,
    ExtractionLog,
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
        # Logging tables
        assert "extraction_logs" in table_names
        assert "api_usage" in table_names

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

    def test_update(self, temp_db):
        """Should update product fields."""
        db = Database(temp_db)
        db.initialize()
        repo = ProductRepository(db)

        product_id = repo.insert(Product(name="Original", category="Old"))
        repo.update(product_id, Product(
            name="Updated",
            category="New",
            target_price=15.00
        ))

        updated = repo.get_by_id(product_id)
        assert updated.name == "Updated"
        assert updated.category == "New"
        assert updated.target_price == 15.00

    def test_delete(self, temp_db):
        """Should delete product."""
        db = Database(temp_db)
        db.initialize()
        repo = ProductRepository(db)

        product_id = repo.insert(Product(name="To Delete"))
        assert repo.get_by_id(product_id) is not None

        repo.delete(product_id)
        assert repo.get_by_id(product_id) is None


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

    def test_update(self, temp_db):
        """Should update store fields."""
        db = Database(temp_db)
        db.initialize()
        repo = StoreRepository(db)

        store_id = repo.insert(Store(name="Old Store", shipping_cost_standard=5.0))
        repo.update(store_id, Store(
            name="New Store",
            shipping_cost_standard=3.0,
            free_shipping_threshold=25.0
        ))

        updated = repo.get_by_id(store_id)
        assert updated.name == "New Store"
        assert updated.shipping_cost_standard == 3.0
        assert updated.free_shipping_threshold == 25.0

    def test_delete(self, temp_db):
        """Should delete store."""
        db = Database(temp_db)
        db.initialize()
        repo = StoreRepository(db)

        store_id = repo.insert(Store(name="To Delete"))
        assert repo.get_by_id(store_id) is not None

        repo.delete(store_id)
        assert repo.get_by_id(store_id) is None


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

    def test_update(self, temp_db):
        """Should update tracked item fields."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Test Store"))

        item_id = item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/old",
            quantity_size=100,
            quantity_unit="ml"
        ))

        item_repo.update(item_id, TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/new",
            quantity_size=500,
            quantity_unit="ml",
            items_per_lot=2
        ))

        updated = item_repo.get_by_id(item_id)
        assert updated.url == "https://example.com/new"
        assert updated.quantity_size == 500
        assert updated.items_per_lot == 2

    def test_delete(self, temp_db):
        """Should delete tracked item."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Test Store"))

        item_id = item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/delete",
            quantity_size=100,
            quantity_unit="ml"
        ))

        assert item_repo.get_by_id(item_id) is not None
        item_repo.delete(item_id)
        assert item_repo.get_by_id(item_id) is None

    def test_get_by_product(self, temp_db):
        """Should get all tracked items for a product."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)

        product_id = product_repo.insert(Product(name="Test Product"))
        other_product_id = product_repo.insert(Product(name="Other Product"))
        store_id = store_repo.insert(Store(name="Store"))

        # Add two items for test product
        item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://store1.com/product",
            quantity_size=100,
            quantity_unit="ml"
        ))
        item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://store2.com/product",
            quantity_size=200,
            quantity_unit="ml"
        ))

        # Add one for other product
        item_repo.insert(TrackedItem(
            product_id=other_product_id,
            store_id=store_id,
            url="https://store1.com/other",
            quantity_size=50,
            quantity_unit="g"
        ))

        items = item_repo.get_by_product(product_id)
        assert len(items) == 2


class TestExtractionLogRepository:
    """Tests for ExtractionLogRepository."""

    def test_insert_success_log(self, temp_db):
        """Should insert a successful extraction log."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)
        log_repo = ExtractionLogRepository(db)

        product_id = product_repo.insert(Product(name="Test Product"))
        store_id = store_repo.insert(Store(name="Test Store"))
        item_id = item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/product",
            quantity_size=100,
            quantity_unit="ml"
        ))

        log = ExtractionLog(
            tracked_item_id=item_id,
            status="success",
            model_used="gemini-2.5-flash",
            price=19.99,
            currency="EUR",
            duration_ms=1500
        )

        log_id = log_repo.insert(log)
        retrieved = log_repo.get_by_id(log_id)

        assert retrieved is not None
        assert retrieved.status == "success"
        assert retrieved.price == 19.99
        assert retrieved.model_used == "gemini-2.5-flash"

    def test_insert_error_log(self, temp_db):
        """Should insert an error extraction log."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)
        log_repo = ExtractionLogRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Store"))
        item_id = item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com",
            quantity_size=1,
            quantity_unit="piece"
        ))

        log = ExtractionLog(
            tracked_item_id=item_id,
            status="error",
            model_used="gemini-2.5-flash",
            error_message="Rate limit exceeded (429)"
        )

        log_id = log_repo.insert(log)
        retrieved = log_repo.get_by_id(log_id)

        assert retrieved is not None
        assert retrieved.status == "error"
        assert "429" in retrieved.error_message

    def test_get_recent(self, temp_db):
        """Should get recent extraction logs."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)
        log_repo = ExtractionLogRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Store"))
        item_id = item_repo.insert(TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com",
            quantity_size=1,
            quantity_unit="piece"
        ))

        log_repo.insert(ExtractionLog(tracked_item_id=item_id, status="success", price=10.0, currency="EUR"))
        log_repo.insert(ExtractionLog(tracked_item_id=item_id, status="error", error_message="Timeout"))
        log_repo.insert(ExtractionLog(tracked_item_id=item_id, status="success", price=9.99, currency="EUR"))

        logs = log_repo.get_recent(limit=10)
        assert len(logs) == 3

    def test_get_by_item(self, temp_db):
        """Should get logs for a specific tracked item."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)
        log_repo = ExtractionLogRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Store"))
        item1_id = item_repo.insert(TrackedItem(
            product_id=product_id, store_id=store_id,
            url="https://example.com/1", quantity_size=1, quantity_unit="piece"
        ))
        item2_id = item_repo.insert(TrackedItem(
            product_id=product_id, store_id=store_id,
            url="https://example.com/2", quantity_size=1, quantity_unit="piece"
        ))

        log_repo.insert(ExtractionLog(tracked_item_id=item1_id, status="success", price=10.0, currency="EUR"))
        log_repo.insert(ExtractionLog(tracked_item_id=item1_id, status="success", price=9.0, currency="EUR"))
        log_repo.insert(ExtractionLog(tracked_item_id=item2_id, status="success", price=20.0, currency="EUR"))

        item1_logs = log_repo.get_by_item(item1_id)
        assert len(item1_logs) == 2

    def test_get_stats(self, temp_db):
        """Should get extraction statistics for today."""
        db = Database(temp_db)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        item_repo = TrackedItemRepository(db)
        log_repo = ExtractionLogRepository(db)

        product_id = product_repo.insert(Product(name="Test"))
        store_id = store_repo.insert(Store(name="Store"))
        item_id = item_repo.insert(TrackedItem(
            product_id=product_id, store_id=store_id,
            url="https://example.com", quantity_size=1, quantity_unit="piece"
        ))

        log_repo.insert(ExtractionLog(
            tracked_item_id=item_id, status="success",
            price=10.0, currency="EUR", duration_ms=1000
        ))
        log_repo.insert(ExtractionLog(
            tracked_item_id=item_id, status="success",
            price=9.0, currency="EUR", duration_ms=2000
        ))
        log_repo.insert(ExtractionLog(
            tracked_item_id=item_id, status="error",
            error_message="Rate limit"
        ))

        stats = log_repo.get_stats()
        assert stats["total_today"] == 3
        assert stats["success_count"] == 2
        assert stats["error_count"] == 1
        assert stats["avg_duration_ms"] == 1500  # (1000 + 2000) / 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
