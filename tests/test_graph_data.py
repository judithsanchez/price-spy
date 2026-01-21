"""Tests for price history graph data stability."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
import os
import tempfile
from app.api.main import app, get_db, _test_db_path as main_test_db_path

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    # Create a temporary database file
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    # Set the test database path in the app module
    import app.api.main
    original_path = app.api.main._test_db_path
    app.api.main._test_db_path = path
    
    db = get_db()
    db.initialize()
    yield db
    db.close()
    
    # Restore original path and cleanup
    app.api.main._test_db_path = original_path
    if os.path.exists(path):
        os.remove(path)

def test_all_price_history_returns_item_id(client, test_db):
    """Test that /api/price-history/all returns item_id for each product."""
    # Setup: Create product, store, tracked item and price history
    cursor = test_db.execute("INSERT INTO products (name) VALUES (?)", ("Test Product",))
    product_id = cursor.lastrowid
    
    cursor = test_db.execute("INSERT INTO stores (name) VALUES (?)", ("Test Store",))
    store_id = cursor.lastrowid
    
    cursor = test_db.execute(
        "INSERT INTO tracked_items (product_id, store_id, url, quantity_size, quantity_unit) VALUES (?, ?, ?, ?, ?)",
        (product_id, store_id, "https://example.com/p1", 1.0, "L")
    )
    item_id = cursor.lastrowid
    
    test_db.execute(
        "INSERT INTO price_history (product_name, price, currency, url, created_at, confidence, store_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("Test Product", 10.0, "EUR", "https://example.com/p1", "2026-01-20 10:00:00", 1.0, "Test Store")
    )
    test_db.commit()
    
    response = client.get("/api/price-history/all?days=30")
    assert response.status_code == 200
    data = response.json()
    
    assert "products" in data
    assert len(data["products"]) == 1
    product_data = data["products"][0]
    assert product_data["item_id"] == item_id
    assert "color" in product_data
    assert len(product_data["prices"]) == 1
