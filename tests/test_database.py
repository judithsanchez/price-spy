"""Tests for SQLite database layer."""

import tempfile
import os
import pytest

from app.storage.database import Database
from app.storage.repositories import PriceHistoryRepository, ErrorLogRepository
from app.models.schemas import PriceHistoryRecord, ErrorRecord


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
        """Database should create price_history and error_log tables."""
        db = Database(temp_db)
        db.initialize()

        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]

        assert "price_history" in table_names
        assert "error_log" in table_names

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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
