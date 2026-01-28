from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.api.main import app
from app.models.schemas import PurchaseTypeResponse

client = TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_repo():
    with patch("app.api.routers.purchase_types.PurchaseTypeRepository") as mock:
        yield mock


def test_get_purchase_types(mock_repo, mock_db):
    mock_repo_inst = mock_repo.return_value
    mock_repo_inst.get_all.return_value = [
        PurchaseTypeResponse(id=1, name="recurring"),
        PurchaseTypeResponse(id=2, name="one_time"),
    ]

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/api/purchase-types")

    assert response.status_code == 200
    assert len(response.json()) == 2

    app.dependency_overrides.clear()
