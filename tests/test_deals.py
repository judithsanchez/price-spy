import pytest
from unittest.mock import MagicMock
from app.models.schemas import ExtractionResult, PriceHistoryRecord
from app.core.price_calculator import compare_prices
from app.storage.repositories import PriceHistoryRepository
from app.storage.database import get_database

def test_deal_comparison_logic():
    # Scenario 1: Price drop triggers deal
    comparison = compare_prices(
        current=10.0,
        previous=15.0,
        original_price=None,
        deal_type=None,
        deal_description=None
    )
    assert comparison.is_deal is True

    # Scenario 2: Active promo triggers deal even without price drop from previous
    comparison = compare_prices(
        current=10.0,
        previous=10.0,
        original_price=None,
        deal_type="bogo",
        deal_description="1+1 gratis"
    )
    assert comparison.is_deal is True
    assert comparison.deal_type == "bogo"

    # Scenario 3: Original price > current price triggers deal
    comparison = compare_prices(
        current=10.0,
        previous=None,
        original_price=12.50,
        deal_type=None,
        deal_description=None
    )
    assert comparison.is_deal is True
    assert comparison.original_price == 12.50

def test_database_persistence():
    db = get_database()
    db.initialize()
    repo = PriceHistoryRepository(db)
    
    record = PriceHistoryRecord(
        item_id=999,
        product_name="Test Product",
        price=9.99,
        currency="EUR",
        confidence=1.0,
        url="https://test.com",
        store_name="Test Store",
        original_price=14.99,
        deal_type="multibuy",
        deal_description="Buy 3 for 25"
    )
    
    repo.insert(record)
    
    # Retrieve and verify
    latest = repo.get_latest_by_url("https://test.com")
    assert latest.original_price == 14.99
    assert latest.deal_type == "multibuy"
    assert latest.deal_description == "Buy 3 for 25"
    
    db.close()

def test_extraction_result_parsing():
    # Verify that ExtractionResult accepts the new fields
    result = ExtractionResult(
        product_name="Test",
        price=5.0,
        currency="EUR",
        is_available=True,
        original_price=10.0,
        deal_type="discount",
        deal_description="50% OFF"
    )
    assert result.original_price == 10.0
    assert result.deal_type == "discount"
