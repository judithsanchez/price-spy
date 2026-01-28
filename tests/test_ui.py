import pytest
from fastapi.testclient import TestClient

# --- UI Pages (Integration) ---

def test_dashboard_loads(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.text or "Price Spy" in response.text

def test_admin_page_loads(client: TestClient):
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Admin Hub" in response.text

def test_products_page_loads(client: TestClient):
    response = client.get("/products")
    assert response.status_code == 200
    assert "Products" in response.text

def test_timeline_page_loads(client: TestClient):
    response = client.get("/timeline")
    # Timeline might depend on DB data but should load empty state fine
    assert response.status_code == 200
    assert "Timeline" in response.text

def test_tracked_items_page_loads(client: TestClient):
    response = client.get("/tracked-items")
    assert response.status_code == 200
    assert "Tracked Items" in response.text

# --- API Endpoints (Integration) ---

def test_health_api(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_products_list(client: TestClient):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_stores_list(client: TestClient):
    response = client.get("/api/stores")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_categories_list(client: TestClient):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_labels_list(client: TestClient):
    response = client.get("/api/labels")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_purchase_types_list(client: TestClient):
    response = client.get("/api/purchase-types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
