from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.api.main import app
from app.models.schemas import (
    PriceHistoryRecord,
    ProductResponse,
    StoreResponse,
    TrackedItemResponse,
)

HTTP_OK = 200

client = TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock()


def test_dashboard_full_rendering(mock_db):
    with (
        patch("app.api.routers.ui.ProductRepository") as mock_prod_repo,
        patch("app.api.routers.ui.StoreRepository") as mock_store_repo,
        patch("app.api.routers.ui.TrackedItemRepository") as mock_tracked_repo,
        patch("app.api.routers.ui.PriceHistoryRepository") as mock_price_repo,
    ):
        # Mock a tracked item
        item = TrackedItemResponse(
            id=1,
            product_id=1,
            store_id=1,
            url="http://example.com/p1",
            items_per_lot=1,
            quantity_size=100.0,
            quantity_unit="ml",
            is_active=True,
            alerts_enabled=True,
            labels=[],
        )
        mock_tracked_repo.return_value.get_all.return_value = [item]

        # Mock product
        product = ProductResponse(
            id=1,
            name="Test Product",
            category="Dairy",
            target_price=2.0,
            target_unit="ml",
            planned_date="2026-W05",
            created_at=datetime.now(UTC),
        )
        mock_prod_repo.return_value.get_by_id.return_value = product
        mock_prod_repo.return_value.get_all.return_value = [product]

        # Mock store
        store = StoreResponse(id=1, name="Test Store")
        mock_store_repo.return_value.get_by_id.return_value = store

        # Mock price history (a drop)
        now = datetime.now(UTC)
        history = [
            PriceHistoryRecord(
                id=1,
                url=item.url,
                price=1.5,
                currency="EUR",
                is_available=True,
                confidence=0.9,
                product_name="Test Product",
                created_at=now,
            ),
            PriceHistoryRecord(
                id=2,
                url=item.url,
                price=2.5,
                currency="EUR",
                is_available=True,
                confidence=0.9,
                product_name="Test Product",
                created_at=now - timedelta(days=1),
            ),
        ]
        mock_price_repo.return_value.get_latest_by_url.return_value = history[0]
        mock_price_repo.return_value.get_history_since.return_value = history

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/")
        assert response.status_code == HTTP_OK
        assert "Test Product" in response.text
        assert "Test Store" in response.text

        app.dependency_overrides.clear()


def test_admin_page():
    response = client.get("/admin")
    assert response.status_code == HTTP_OK
    assert "Admin" in response.text


def test_products_page():
    response = client.get("/products")
    assert response.status_code == HTTP_OK
    assert "Products" in response.text


def test_timeline_page_full(mock_db):
    with (
        patch("app.api.routers.ui.ProductRepository") as mock_prod_repo,
        patch("app.api.routers.ui.PriceHistoryRepository"),
        patch("app.api.routers.ui.TrackedItemRepository") as mock_tracked_repo,
    ):
        product = ProductResponse(
            id=1,
            name="Timed Product",
            category="Dairy",
            target_price=2.0,
            planned_date="2026-W05",
            created_at=datetime.now(UTC),
        )
        mock_prod_repo.return_value.get_all.return_value = [product]
        mock_tracked_repo.return_value.get_by_product.return_value = []

        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/timeline")
        assert response.status_code == HTTP_OK
        assert "Timeline" in response.text
        assert "2026" in response.text
        assert "W5" in response.text or "W05" in response.text
        app.dependency_overrides.clear()


def test_tracked_items_page():
    response = client.get("/tracked-items")
    assert response.status_code == HTTP_OK
    assert "Tracked Items" in response.text
