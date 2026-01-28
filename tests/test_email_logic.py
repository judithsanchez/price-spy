from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.core.email_report import generate_report_data, render_html_email
from app.models.schemas import PriceHistoryRecord


@pytest.fixture
def mock_db():
    return MagicMock()


def test_generate_report_data_mocked(mock_db):
    with (
        patch("app.core.email_report.ProductRepository"),
        patch("app.core.email_report.TrackedItemRepository"),
        patch("app.core.email_report.PriceHistoryRepository") as mock_price_repo,
        patch("app.core.email_report.StoreRepository"),
        patch("app.core.email_report.get_item_details") as mock_get_details,
    ):
        # Setup mock details
        mock_get_details.return_value = {
            "product_name": "Test Product",
            "store_name": "Test Store",
            "target_price": 10.0,
            "target_unit": "kg",
            "items_per_lot": 1,
            "quantity_size": 1.0,
            "quantity_unit": "kg",
            "url": "http://test.com",
        }

        # Setup mock history
        price = PriceHistoryRecord(
            id=1,
            url="http://test.com",
            price=9.0,
            currency="EUR",
            is_available=True,
            confidence=1.0,
            product_name="Test Product",
            created_at=datetime.now(UTC),
        )
        mock_price_repo.return_value.get_by_url.return_value = [price]

        # result passed to generate_report_data
        results = [{"item_id": 1, "status": "success", "price": 9.0, "currency": "EUR"}]

        # Testing core logic
        report_data = generate_report_data(results, mock_db)

        assert "deals" in report_data
        assert len(report_data["deals"]) > 0
        assert report_data["deals"][0]["product_name"] == "Test Product"
        assert report_data["deals"][0]["is_target_hit"]


def test_render_html_email_mocked():
    report_data = {
        "deals": [
            {
                "product_name": "Test Product",
                "price": 9.0,
                "currency": "EUR",
                "is_target_hit": True,
            }
        ],
        "low_stock": [],
        "price_increases": [],
        "untracked_planned": [],
        "has_items": True,
        "date": "January 01, 2026",
        "total": 1,
        "success_count": 1,
        "error_count": 0,
        "deals_count": 1,
        "items": [],
        "errors": [],
        "next_run": "Tomorrow",
    }
    config = {"APP_URL": "http://localhost:8000"}

    html = render_html_email(report_data, config)
    assert "Price Spy" in html
    assert "Test Product" in html
