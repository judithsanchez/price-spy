"""Tests for the vision module - Gemini price extraction."""

import os
import pytest
from dotenv import load_dotenv

from app.core.browser import capture_screenshot
from app.core.vision import extract_product_info


load_dotenv()


@pytest.fixture
def api_key():
    """Load Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set in environment")
    return key


@pytest.mark.asyncio
async def test_extract_product_info_from_screenshot(api_key):
    """Verify Gemini can extract product name and price from Amazon product page."""
    # Use the same product URL from test_browser
    url = "https://www.amazon.nl/-/en/INSTITUTO-ESPA%C3%91OL-Urea-lotion-dispenser/dp/B015OAQEHI"
    screenshot_bytes = await capture_screenshot(url)

    result = await extract_product_info(screenshot_bytes, api_key)

    assert result is not None, "Should return a result"
    assert len(result) > 0, "Should have some content"

    print(f"\n{'='*50}")
    print(f"Gemini extracted:")
    print(f"{'='*50}")
    print(result)
    print(f"{'='*50}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
