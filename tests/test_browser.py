"""Tests for the browser module - screenshot capture functionality."""

import os
import pytest

from app.core.browser import capture_screenshot


@pytest.mark.asyncio
async def test_capture_screenshot_returns_png_bytes():
    """Verify that capturing a screenshot returns valid PNG bytes."""
    url = "https://www.amazon.nl"

    screenshot_bytes = await capture_screenshot(url)

    # PNG files start with these magic bytes
    PNG_MAGIC = b'\x89PNG\r\n\x1a\n'

    assert screenshot_bytes is not None, "Screenshot should not be None"
    assert len(screenshot_bytes) > 0, "Screenshot should not be empty"
    assert screenshot_bytes[:8] == PNG_MAGIC, "Screenshot should be valid PNG format"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
