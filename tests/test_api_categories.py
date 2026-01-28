import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.api.main import app
from app.api.deps import get_db
from app.models.schemas import CategoryResponse
from datetime import datetime, timezone

client = TestClient(app)

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_repo():
    with patch("app.api.routers.categories.CategoryRepository") as mock:
        yield mock

def test_get_categories(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_all.return_value = [
        CategoryResponse(id=1, name="Dairy", is_size_sensitive=False, created_at=datetime.now(timezone.utc))
    ]
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert len(response.json()) == 1
    app.dependency_overrides.clear()

def test_search_categories(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.search.return_value = [
        CategoryResponse(id=1, name="Dairy", is_size_sensitive=False, created_at=datetime.now(timezone.utc))
    ]
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.get("/api/categories/search?q=dai")
    assert response.status_code == 200
    assert len(response.json()) == 1
    app.dependency_overrides.clear()

def test_create_category(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.normalize_name.return_value = "Electronics"
    mock_repo_inst.get_by_name.return_value = None
    mock_repo_inst.insert.return_value = 1
    # Router calls get_by_name at the end
    mock_repo_inst.get_by_name.side_effect = [None, CategoryResponse(id=1, name="Electronics", created_at=datetime.now(timezone.utc))]
    
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.post("/api/categories", json={"name": "Electronics", "is_size_sensitive": False})
    assert response.status_code == 201
    assert response.json()["name"] == "Electronics"
    app.dependency_overrides.clear()

def test_update_category(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_by_id.return_value = CategoryResponse(id=1, name="Old", created_at=datetime.now(timezone.utc))
    mock_repo_inst.normalize_name.return_value = "New"
    mock_repo_inst.get_by_id.side_effect = [
        CategoryResponse(id=1, name="Old", created_at=datetime.now(timezone.utc)),
        CategoryResponse(id=1, name="New", created_at=datetime.now(timezone.utc))
    ]
    
    app.dependency_overrides[get_db] = lambda: mock_db
    response = client.put("/api/categories/1", json={"name": "New", "is_size_sensitive": True})
    assert response.status_code == 200
    assert response.json()["name"] == "New"
    app.dependency_overrides.clear()

def test_delete_category_success(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_by_id.return_value = CategoryResponse(id=1, name="Dairy", created_at=datetime.now(timezone.utc))
    
    with patch("app.api.routers.categories.ProductRepository") as mock_prod_repo:
        mock_prod_repo.return_value.get_by_category.return_value = []
        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.delete("/api/categories/1")
        assert response.status_code == 200
        mock_repo_inst.delete.assert_called_once_with(1)
        app.dependency_overrides.clear()

def test_delete_category_in_use(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_by_id.return_value = CategoryResponse(id=1, name="Dairy", created_at=datetime.now(timezone.utc))
    
    with patch("app.api.routers.categories.ProductRepository") as mock_prod_repo:
        mock_prod_repo.return_value.get_by_category.return_value = [{"id": 1}]
        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.delete("/api/categories/1")
        assert response.status_code == 400
        assert "assigned to" in response.json()["detail"]
        app.dependency_overrides.clear()
