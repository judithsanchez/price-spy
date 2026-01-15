"""Tests for the vision module - Gemini price extraction."""

import os
import pytest
from dotenv import load_dotenv

from app.core.browser import capture_screenshot
from app.core.vision import extract_price_data


load_dotenv()


@pytest.fixture
def api_key():
    """Load Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set in environment")
    return key


@pytest.mark.asyncio
async def test_extract_price_from_search_page(api_key):
    """Verify Gemini can extract price data from Amazon search results."""
    # Capture a search page with products
    url = "https://www.amazon.nl/s?k=headphones"
    screenshot_bytes = await capture_screenshot(url)

    result = await extract_price_data(screenshot_bytes, api_key)

    assert result is not None, "Should return a result"
    assert "product_name" in result, "Should have product_name"
    assert "price" in result, "Should have price"
    assert "currency" in result, "Should have currency"
    assert "confidence_score" in result, "Should have confidence_score"
    assert result["price"] > 0, "Price should be positive"
    assert 0 <= result["confidence_score"] <= 1, "Confidence should be 0-1"

    print(f"\nExtracted data: {result}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
