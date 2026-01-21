"""Tests for Pydantic models - data validation."""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    ProductInfo,
    ErrorRecord,
    PriceHistoryRecord,
    Product,
    Store,
    TrackedItem,
    PriceComparison,
    ExtractionResult,
)


class TestProductInfo:
    """Tests for ProductInfo model."""

    def test_valid_product_info(self):
        """Valid data should parse correctly."""
        data = {
            "product_name": "Test Product",
            "price": 19.99,
            "currency": "EUR",
            "store_name": "Amazon.nl",
            "page_type": "single_product",
            "confidence_score": 0.95
        }
        info = ProductInfo(**data)

        assert info.product_name == "Test Product"
        assert info.price == 19.99
        assert info.currency == "EUR"
        assert info.confidence == 0.95  # Note: alias maps confidence_score -> confidence

    def test_price_must_be_positive(self):
        """Negative price should raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductInfo(
                product_name="Test",
                price=-10.0,
                page_type="single_product",
                confidence_score=0.5
            )

    def test_price_zero_invalid(self):
        """Zero price should raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductInfo(
                product_name="Test",
                price=0,
                page_type="single_product",
                confidence_score=0.5
            )

    def test_confidence_must_be_0_to_1(self):
        """Confidence > 1.0 should raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductInfo(
                product_name="Test",
                price=10.0,
                page_type="single_product",
                confidence_score=1.5
            )

    def test_confidence_negative_invalid(self):
        """Negative confidence should raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductInfo(
                product_name="Test",
                price=10.0,
                page_type="single_product",
                confidence_score=-0.1
            )

    def test_currency_must_be_3_letters(self):
        """Currency must be exactly 3 uppercase letters."""
        with pytest.raises(ValidationError):
            ProductInfo(
                product_name="Test",
                price=10.0,
                currency="EURO",  # 4 letters - invalid
                page_type="single_product",
                confidence_score=0.5
            )

    def test_page_type_must_be_valid(self):
        """Page type must be 'single_product' or 'search_results'."""
        with pytest.raises(ValidationError):
            ProductInfo(
                product_name="Test",
                price=10.0,
                page_type="invalid_type",
                confidence_score=0.5
            )

    def test_store_name_optional(self):
        """Store name should be optional."""
        info = ProductInfo(
            product_name="Test",
            price=10.0,
            page_type="single_product",
            confidence_score=0.5
        )
        assert info.store_name is None

    def test_price_rounded_to_2_decimals(self):
        """Price should be rounded to 2 decimal places."""
        info = ProductInfo(
            product_name="Test",
            price=19.999,
            page_type="single_product",
            confidence_score=0.5
        )
        assert info.price == 20.0


class TestErrorRecord:
    """Tests for ErrorRecord model."""

    def test_valid_error_record(self):
        """Valid error record should parse correctly."""
        record = ErrorRecord(
            error_type="api_error",
            message="Rate limit exceeded",
            url="https://example.com"
        )
        assert record.error_type == "api_error"
        assert record.message == "Rate limit exceeded"

    def test_error_type_required(self):
        """Error type is required."""
        with pytest.raises(ValidationError):
            ErrorRecord(message="Some error")

    def test_screenshot_path_optional(self):
        """Screenshot path should be optional."""
        record = ErrorRecord(
            error_type="timeout",
            message="Connection timeout"
        )
        assert record.screenshot_path is None


class TestPriceHistoryRecord:
    """Tests for PriceHistoryRecord model."""

    def test_valid_price_history(self):
        """Valid price history should parse correctly."""
        record = PriceHistoryRecord(
            product_name="Test Product",
            price=29.99,
            currency="EUR",
            confidence=0.9,
            url="https://amazon.nl/product"
        )
        assert record.product_name == "Test Product"
        assert record.price == 29.99
        assert record.created_at is not None


class TestProduct:
    """Tests for Product model (master product concept)."""

    def test_valid_product(self):
        """Valid product should parse correctly."""
        product = Product(
            name="Campina Slagroom",
            category="Dairy",
            purchase_type="recurring",
            target_price=2.50,
            preferred_unit_size="250ml"
        )
        assert product.name == "Campina Slagroom"
        assert product.category == "Dairy"
        assert product.current_stock == 0

    def test_product_name_required(self):
        """Product name is required."""
        with pytest.raises(ValidationError):
            Product(category="Dairy")

    def test_product_target_price_must_be_positive(self):
        """Target price must be positive if provided."""
        with pytest.raises(ValidationError):
            Product(name="Test", target_price=-5.0)

    def test_product_purchase_type_valid_values(self):
        """Purchase type must be 'recurring' or 'one_time'."""
        with pytest.raises(ValidationError):
            Product(name="Test", purchase_type="invalid")

    def test_product_stock_cannot_be_negative(self):
        """Current stock cannot be negative."""
        with pytest.raises(ValidationError):
            Product(name="Test", current_stock=-1)


class TestStore:
    """Tests for Store model."""

    def test_valid_store(self):
        """Valid store should parse correctly."""
        store = Store(
            name="Amazon.nl",
            shipping_cost_standard=4.95,
            free_shipping_threshold=50.0,
            notes="Usually fast delivery"
        )
        assert store.name == "Amazon.nl"
        assert store.shipping_cost_standard == 4.95
        assert store.free_shipping_threshold == 50.0

    def test_store_name_required(self):
        """Store name is required."""
        with pytest.raises(ValidationError):
            Store(shipping_cost_standard=4.95)

    def test_store_shipping_cost_default_zero(self):
        """Shipping cost defaults to 0."""
        store = Store(name="Free Store")
        assert store.shipping_cost_standard == 0

    def test_store_shipping_cannot_be_negative(self):
        """Shipping cost cannot be negative."""
        with pytest.raises(ValidationError):
            Store(name="Test", shipping_cost_standard=-1.0)


class TestTrackedItem:
    """Tests for TrackedItem model (URL to track)."""

    def test_valid_tracked_item(self):
        """Valid tracked item should parse correctly."""
        item = TrackedItem(
            product_id=1,
            store_id=1,
            url="https://amazon.nl/dp/B12345",
            quantity_size=250,
            quantity_unit="ml",
            items_per_lot=1
        )
        assert item.url == "https://amazon.nl/dp/B12345"
        assert item.quantity_size == 250
        assert item.is_active is True
        assert item.alerts_enabled is True

    def test_tracked_item_multipack(self):
        """Multipack items should have items_per_lot > 1."""
        item = TrackedItem(
            product_id=1,
            store_id=1,
            url="https://amazon.nl/dp/B12345",
            quantity_size=330,
            quantity_unit="ml",
            items_per_lot=6
        )
        assert item.items_per_lot == 6

    def test_tracked_item_quantity_must_be_positive(self):
        """Quantity size must be positive."""
        with pytest.raises(ValidationError):
            TrackedItem(
                product_id=1,
                store_id=1,
                url="https://example.com",
                quantity_size=0,
                quantity_unit="ml"
            )

    def test_tracked_item_items_per_lot_minimum_one(self):
        """Items per lot must be at least 1."""
        with pytest.raises(ValidationError):
            TrackedItem(
                product_id=1,
                store_id=1,
                url="https://example.com",
                quantity_size=100,
                quantity_unit="ml",
                items_per_lot=0
            )

    def test_tracked_item_with_preferred_model(self):
        """TrackedItem should support an optional preferred_model."""
        item = TrackedItem(
            product_id=1,
            store_id=1,
            url="https://example.com",
            quantity_size=100,
            quantity_unit="ml",
            preferred_model="gemini-2.5-flash-lite"
        )
        assert item.preferred_model == "gemini-2.5-flash-lite"

    def test_tracked_item_requires_product_and_store(self):
        """Product ID and Store ID are required."""
        with pytest.raises(ValidationError):
            TrackedItem(
                url="https://example.com",
                quantity_size=100,
                quantity_unit="ml"
            )


class TestPriceComparison:
    """Tests for PriceComparison model."""

    def test_price_drop(self):
        """Price drop should be detected."""
        comparison = PriceComparison(
            current_price=8.99,
            previous_price=10.99,
            price_change=-2.0,
            price_change_percent=-18.2,
            is_price_drop=True
        )
        assert comparison.is_price_drop is True
        assert comparison.price_change == -2.0

    def test_price_increase(self):
        """Price increase should not be flagged as drop."""
        comparison = PriceComparison(
            current_price=12.99,
            previous_price=10.99,
            price_change=2.0,
            price_change_percent=18.2,
            is_price_drop=False
        )
        assert comparison.is_price_drop is False

    def test_no_previous_price(self):
        """First check has no previous price."""
        comparison = PriceComparison(
            current_price=10.99,
            previous_price=None,
            is_price_drop=False
        )
        assert comparison.previous_price is None
        assert comparison.price_change is None

    def test_with_volume_price(self):
        """Volume price should be included when available."""
        comparison = PriceComparison(
            current_price=6.00,
            previous_price=6.50,
            price_change=-0.50,
            price_change_percent=-7.7,
            volume_price=3.03,
            volume_unit="L",
            is_price_drop=True
        )
        assert comparison.volume_price == 3.03
        assert comparison.volume_unit == "L"


class TestExtractionResult:
    """Tests for ExtractionResult model (structured Gemini output)."""

    def test_valid_extraction_result(self):
        """Valid extraction result should parse correctly."""
        result = ExtractionResult(
            price=12.99,
            currency="EUR",
            is_available=True,
            product_name="Test Product",
            store_name="Amazon.nl"
        )
        assert result.price == 12.99
        assert result.currency == "EUR"
        assert result.is_available is True
        assert result.product_name == "Test Product"
        assert result.detected_at is not None

    def test_extraction_result_from_json(self):
        """Should parse from JSON string (Gemini response)."""
        json_str = '{"price": 19.99, "currency": "EUR", "is_available": true, "product_name": "Lotion 950ml"}'
        result = ExtractionResult.model_validate_json(json_str)
        assert result.price == 19.99
        assert result.is_available is True

    def test_extraction_result_price_must_be_positive(self):
        """Price must be positive."""
        with pytest.raises(ValidationError):
            ExtractionResult(
                price=-5.0,
                currency="EUR",
                is_available=True,
                product_name="Test"
            )

    def test_extraction_result_price_zero_invalid(self):
        """Zero price should raise ValidationError."""
        with pytest.raises(ValidationError):
            ExtractionResult(
                price=0,
                currency="EUR",
                is_available=True,
                product_name="Test"
            )

    def test_extraction_result_currency_pattern(self):
        """Currency must be 3 uppercase letters."""
        with pytest.raises(ValidationError):
            ExtractionResult(
                price=10.0,
                currency="euro",  # lowercase - invalid
                is_available=True,
                product_name="Test"
            )

    def test_extraction_result_is_available_required(self):
        """is_available field is required."""
        with pytest.raises(ValidationError):
            ExtractionResult(
                price=10.0,
                currency="EUR",
                product_name="Test"
            )

    def test_extraction_result_product_name_required(self):
        """product_name is required."""
        with pytest.raises(ValidationError):
            ExtractionResult(
                price=10.0,
                currency="EUR",
                is_available=True
            )

    def test_extraction_result_store_name_optional(self):
        """store_name should be optional."""
        result = ExtractionResult(
            price=10.0,
            currency="EUR",
            is_available=True,
            product_name="Test"
        )
        assert result.store_name is None

    def test_extraction_result_out_of_stock(self):
        """Should handle out of stock items."""
        result = ExtractionResult(
            price=15.99,
            currency="EUR",
            is_available=False,
            product_name="Out of Stock Item"
        )
        assert result.is_available is False

    def test_extraction_result_price_rounded(self):
        """Price should be rounded to 2 decimal places."""
        result = ExtractionResult(
            price=12.999,
            currency="EUR",
            is_available=True,
            product_name="Test"
        )
        assert result.price == 13.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
