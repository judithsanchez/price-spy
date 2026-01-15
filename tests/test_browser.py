"""Tests for the browser module - screenshot capture functionality."""

import pytest

from app.core.browser import capture_screenshot


PNG_MAGIC = b'\x89PNG\r\n\x1a\n'


@pytest.mark.asyncio
async def test_capture_screenshot_returns_png_bytes():
    """Verify that capturing a screenshot returns valid PNG bytes."""
    url = "https://www.amazon.nl"

    screenshot_bytes = await capture_screenshot(url)

    assert screenshot_bytes is not None, "Screenshot should not be None"
    assert len(screenshot_bytes) > 0, "Screenshot should not be empty"
    assert screenshot_bytes[:8] == PNG_MAGIC, "Screenshot should be valid PNG format"


@pytest.mark.asyncio
async def test_capture_product_page_screenshot():
    """Verify we can capture a specific Amazon product page without CAPTCHA."""
    # Popular product URL (Echo Dot)
    url = "https://www.amazon.nl/dp/B09B8V1LZ3"

    screenshot_bytes = await capture_screenshot(url)

    assert screenshot_bytes is not None, "Screenshot should not be None"
    assert len(screenshot_bytes) > 1000, "Screenshot should have substantial content"
    assert screenshot_bytes[:8] == PNG_MAGIC, "Screenshot should be valid PNG format"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
