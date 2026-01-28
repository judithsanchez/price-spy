import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.api.main import app
from app.api.deps import get_db
from app.models.schemas import UnitResponse

client = TestClient(app)


@pytest.fixture
def mock_db():
    db = MagicMock()
    # Mock context manager behavior if needed, but here it's just passed to repo
    return db


@pytest.fixture
def mock_repo():
    with patch("app.api.routers.units.UnitRepository") as mock:
        yield mock


def test_get_units(mock_repo, mock_db):
    # Setup
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_all.return_value = [
        UnitResponse(id=1, name="ml"),
        UnitResponse(id=2, name="kg"),
    ]

    # Override dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/units")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "ml"

    # Cleanup
    app.dependency_overrides.clear()


def test_create_unit(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_by_name.return_value = None
    mock_repo_inst.insert.return_value = 3
    mock_repo_inst.get_by_id.return_value = UnitResponse(id=3, name="bottle")

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/api/units", json={"name": "bottle"})

    assert response.status_code == 201
    assert response.json()["name"] == "bottle"

    app.dependency_overrides.clear()


def test_delete_unit_success(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_by_id.return_value = UnitResponse(id=1, name="ml")

    # Mock DB executions check usage
    mock_db.execute.return_value.fetchall.return_value = []  # No usage

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.delete("/api/units/1")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_repo_inst.delete.assert_called_once_with(1)

    app.dependency_overrides.clear()


def test_delete_unit_in_use(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_by_id.return_value = UnitResponse(id=1, name="ml")

    # Mock DB execution finding a product using it
    mock_db.execute.return_value.fetchall.side_effect = [[(1,)], []]

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.delete("/api/units/1")

    assert response.status_code == 400
    assert "used by" in response.json()["detail"]

    app.dependency_overrides.clear()
