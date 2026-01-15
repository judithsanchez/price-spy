"""Tests for Pydantic models - data validation."""

import pytest
from pydantic import ValidationError

from app.models.schemas import ProductInfo, ErrorRecord, PriceHistoryRecord


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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
