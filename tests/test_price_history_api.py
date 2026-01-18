"""Tests for price history API endpoint."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.api.main import app, get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_db():
    db = get_db()
    db.initialize()
    # Clean up tables for test isolation
    db.execute("DELETE FROM price_history")
    db.execute("DELETE FROM tracked_items")
    db.execute("DELETE FROM products")
    db.execute("DELETE FROM stores")
    db.commit()
    yield db
    db.close()


@pytest.fixture
def sample_tracked_item(test_db):
    """Create a tracked item with price history."""
    # Create product
    cursor = test_db.execute(
        "INSERT INTO products (name, category, target_price) VALUES (?, ?, ?)",
        ("Test Product", "Test", 15.00),
    )
    product_id = cursor.lastrowid

    # Create store
    cursor = test_db.execute(
        "INSERT INTO stores (name) VALUES (?)",
        ("Test Store",),
    )
    store_id = cursor.lastrowid

    # Create tracked item
    cursor = test_db.execute(
        """INSERT INTO tracked_items (product_id, store_id, url, is_active, quantity_size, quantity_unit)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (product_id, store_id, "https://example.com/product", 1, 1.0, "L"),
    )
    item_id = cursor.lastrowid
    test_db.commit()

    return {
        "item_id": item_id,
        "product_id": product_id,
        "store_id": store_id,
        "url": "https://example.com/product",
    }


@pytest.fixture
def item_with_prices(test_db, sample_tracked_item):
    """Create a tracked item with multiple price history entries."""
    url = sample_tracked_item["url"]

    # Insert price history entries over several days
    prices = [
        (18.99, "2026-01-10 10:00:00"),
        (17.50, "2026-01-12 10:00:00"),
        (16.99, "2026-01-15 10:00:00"),
        (15.49, "2026-01-18 10:00:00"),
    ]

    for price, created_at in prices:
        test_db.execute(
            """INSERT INTO price_history
               (product_name, price, currency, confidence, url, store_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("Test Product", price, "EUR", 1.0, url, "Test Store", created_at),
        )
    test_db.commit()

    return sample_tracked_item


class TestPriceHistoryAPI:
    """Tests for GET /api/items/{item_id}/price-history endpoint."""

    def test_get_price_history_returns_prices(self, client, item_with_prices):
        """GET /api/items/{id}/price-history returns price list."""
        item_id = item_with_prices["item_id"]

        response = client.get(f"/api/items/{item_id}/price-history")

        assert response.status_code == 200
        data = response.json()
        assert "prices" in data
        assert len(data["prices"]) == 4
        assert data["prices"][0]["price"] == 18.99
        assert data["prices"][-1]["price"] == 15.49

    def test_get_price_history_calculates_stats(self, client, item_with_prices):
        """Response includes min, max, avg, current stats."""
        item_id = item_with_prices["item_id"]

        response = client.get(f"/api/items/{item_id}/price-history")

        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        stats = data["stats"]
        assert stats["min"] == 15.49
        assert stats["max"] == 18.99
        assert stats["current"] == 15.49
        assert "avg" in stats
        # Average of 18.99, 17.50, 16.99, 15.49 = 17.2425
        assert abs(stats["avg"] - 17.24) < 0.01

    def test_get_price_history_includes_metadata(self, client, item_with_prices):
        """Response includes item metadata."""
        item_id = item_with_prices["item_id"]

        response = client.get(f"/api/items/{item_id}/price-history")

        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == item_id
        assert data["product_name"] == "Test Product"
        assert data["currency"] == "EUR"
        assert data["target_price"] == 15.00

    def test_get_price_history_respects_days_param(self, client, test_db, sample_tracked_item):
        """days parameter limits results to recent prices only."""
        url = sample_tracked_item["url"]
        item_id = sample_tracked_item["item_id"]

        # Insert prices: one from 60 days ago, one from 5 days ago
        now = datetime.now()
        old_date = (now - timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S")
        recent_date = (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")

        test_db.execute(
            """INSERT INTO price_history
               (product_name, price, currency, confidence, url, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("Test Product", 20.00, "EUR", 1.0, url, old_date),
        )
        test_db.execute(
            """INSERT INTO price_history
               (product_name, price, currency, confidence, url, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("Test Product", 18.00, "EUR", 1.0, url, recent_date),
        )
        test_db.commit()

        # Request only last 30 days
        response = client.get(f"/api/items/{item_id}/price-history?days=30")

        assert response.status_code == 200
        data = response.json()
        assert len(data["prices"]) == 1
        assert data["prices"][0]["price"] == 18.00

    def test_get_price_history_item_not_found(self, client, test_db):
        """Returns 404 for non-existent item."""
        response = client.get("/api/items/99999/price-history")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_price_history_no_prices(self, client, sample_tracked_item):
        """Returns empty list when no price history exists."""
        item_id = sample_tracked_item["item_id"]

        response = client.get(f"/api/items/{item_id}/price-history")

        assert response.status_code == 200
        data = response.json()
        assert data["prices"] == []
        assert data["stats"]["min"] is None
        assert data["stats"]["max"] is None
        assert data["stats"]["avg"] is None
        assert data["stats"]["current"] is None

    def test_get_price_history_price_drop_percentage(self, client, item_with_prices):
        """Stats include price drop percentage from max."""
        item_id = item_with_prices["item_id"]

        response = client.get(f"/api/items/{item_id}/price-history")

        assert response.status_code == 200
        stats = response.json()["stats"]
        # Drop from 18.99 to 15.49 = -18.4%
        assert "price_drop_pct" in stats
        assert abs(stats["price_drop_pct"] - (-18.43)) < 0.1

    def test_get_price_history_prices_sorted_by_date(self, client, item_with_prices):
        """Prices are returned in chronological order."""
        item_id = item_with_prices["item_id"]

        response = client.get(f"/api/items/{item_id}/price-history")

        data = response.json()
        dates = [p["date"] for p in data["prices"]]
        assert dates == sorted(dates)
