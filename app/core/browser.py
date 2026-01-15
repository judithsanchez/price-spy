"""Browser module for stealth screenshot capture."""

from playwright.async_api import async_playwright


async def capture_screenshot(url: str) -> bytes:
    """Navigate to URL and capture screenshot as PNG bytes."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="nl-NL",
            timezone_id="Europe/Amsterdam",
        )

        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        # Wait for page to stabilize
        await page.wait_for_timeout(3000)

        screenshot_bytes = await page.screenshot(type="png")

        await browser.close()

        return screenshot_bytes
