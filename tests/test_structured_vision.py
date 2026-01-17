"""Tests for structured output vision extraction."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import ValidationError

from app.models.schemas import ExtractionResult


class TestStructuredExtraction:
    """Tests for structured Gemini output parsing."""

    def test_parse_valid_json_response(self):
        """Valid JSON response should parse to ExtractionResult."""
        raw_json = '{"price": 12.99, "currency": "EUR", "is_available": true, "product_name": "Test Product", "store_name": "Amazon"}'
        result = ExtractionResult.model_validate_json(raw_json)

        assert result.price == 12.99
        assert result.currency == "EUR"
        assert result.is_available is True
        assert result.product_name == "Test Product"
        assert result.store_name == "Amazon"

    def test_parse_response_without_store(self):
        """Response without store_name should be valid."""
        raw_json = '{"price": 9.99, "currency": "EUR", "is_available": true, "product_name": "Product"}'
        result = ExtractionResult.model_validate_json(raw_json)

        assert result.store_name is None

    def test_parse_out_of_stock_product(self):
        """Out of stock products should parse with is_available=False."""
        raw_json = '{"price": 19.99, "currency": "EUR", "is_available": false, "product_name": "Sold Out Item"}'
        result = ExtractionResult.model_validate_json(raw_json)

        assert result.is_available is False

    def test_parse_missing_required_field_raises(self):
        """Missing required field should raise ValidationError."""
        raw_json = '{"price": 12.99, "currency": "EUR"}'  # missing is_available, product_name
        with pytest.raises(ValidationError):
            ExtractionResult.model_validate_json(raw_json)

    def test_parse_invalid_price_raises(self):
        """Invalid price should raise ValidationError."""
        raw_json = '{"price": -5, "currency": "EUR", "is_available": true, "product_name": "Test"}'
        with pytest.raises(ValidationError):
            ExtractionResult.model_validate_json(raw_json)

    def test_parse_usd_currency(self):
        """USD currency should be valid."""
        raw_json = '{"price": 15.00, "currency": "USD", "is_available": true, "product_name": "US Product"}'
        result = ExtractionResult.model_validate_json(raw_json)

        assert result.currency == "USD"

    def test_parse_gbp_currency(self):
        """GBP currency should be valid."""
        raw_json = '{"price": 12.50, "currency": "GBP", "is_available": true, "product_name": "UK Product"}'
        result = ExtractionResult.model_validate_json(raw_json)

        assert result.currency == "GBP"


class TestStructuredVisionAPI:
    """Tests for the structured vision API call."""

    @pytest.mark.asyncio
    async def test_extract_with_structured_output_success(self):
        """Successful API call should return ExtractionResult."""
        from app.core.vision import extract_with_structured_output

        mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": '{"price": 13.44, "currency": "EUR", "is_available": true, "product_name": "INSTITUTO ESPAÑOL Urea lotion 950ml", "store_name": "Amazon.nl"}'
                    }]
                }
            }]
        }

        with patch('app.core.vision.aiohttp.ClientSession') as mock_session_class:
            # Create mock response
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 200
            mock_response_obj.json = AsyncMock(return_value=mock_response)

            # Create mock session with proper context manager support
            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            # Mock post to return response with context manager
            mock_post_cm = MagicMock()
            mock_post_cm.__aenter__ = AsyncMock(return_value=mock_response_obj)
            mock_post_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = MagicMock(return_value=mock_post_cm)

            mock_session_class.return_value = mock_session

            result, model_used = await extract_with_structured_output(b"fake_image_bytes", "fake_api_key")

            assert isinstance(result, ExtractionResult)
            assert result.price == 13.44
            assert result.is_available is True
            assert result.product_name == "INSTITUTO ESPAÑOL Urea lotion 950ml"
            assert model_used == "gemini-2.5-flash"

    @pytest.mark.asyncio
    async def test_extract_with_structured_output_invalid_json(self):
        """Invalid JSON should raise exception."""
        from app.core.vision import extract_with_structured_output

        mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": 'not valid json'
                    }]
                }
            }]
        }

        with patch('app.core.vision.aiohttp.ClientSession') as mock_session_class:
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 200
            mock_response_obj.json = AsyncMock(return_value=mock_response)

            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_post_cm = MagicMock()
            mock_post_cm.__aenter__ = AsyncMock(return_value=mock_response_obj)
            mock_post_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = MagicMock(return_value=mock_post_cm)

            mock_session_class.return_value = mock_session

            with pytest.raises(Exception):
                await extract_with_structured_output(b"fake_image_bytes", "fake_api_key")

    @pytest.mark.asyncio
    async def test_extract_with_structured_output_api_error(self):
        """API error should raise exception."""
        from app.core.vision import extract_with_structured_output

        with patch('app.core.vision.aiohttp.ClientSession') as mock_session_class:
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 500
            mock_response_obj.text = AsyncMock(return_value="Internal Server Error")

            mock_session = MagicMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_post_cm = MagicMock()
            mock_post_cm.__aenter__ = AsyncMock(return_value=mock_response_obj)
            mock_post_cm.__aexit__ = AsyncMock(return_value=None)
            mock_session.post = MagicMock(return_value=mock_post_cm)

            mock_session_class.return_value = mock_session

            with pytest.raises(Exception) as exc_info:
                await extract_with_structured_output(b"fake_image_bytes", "fake_api_key")

            assert "500" in str(exc_info.value)
