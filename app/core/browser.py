"""Browser module for stealth screenshot capture."""

from playwright.async_api import async_playwright, BrowserContext


# Stealth configuration as per SPECS_EXTRACTION_ENGINE.md
STEALTH_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
    "locale": "nl-NL",
    "timezone_id": "Europe/Amsterdam",
    "geolocation": {"latitude": 52.3676, "longitude": 4.9041},  # Amsterdam
    "permissions": ["geolocation"],
}

# JavaScript to mask automation detection
STEALTH_SCRIPTS = """
    // Mask webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });

    // Mask automation-related properties
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });

    // Mask Chrome-specific properties
    window.chrome = {
        runtime: {},
    };
"""


async def create_stealth_context(playwright) -> BrowserContext:
    """Create a browser context with stealth settings."""
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        viewport=STEALTH_CONFIG["viewport"],
        user_agent=STEALTH_CONFIG["user_agent"],
        locale=STEALTH_CONFIG["locale"],
        timezone_id=STEALTH_CONFIG["timezone_id"],
        geolocation=STEALTH_CONFIG["geolocation"],
        permissions=STEALTH_CONFIG["permissions"],
    )
    return context


async def capture_screenshot(url: str) -> bytes:
    """Navigate to URL and capture screenshot as PNG bytes."""
    async with async_playwright() as p:
        context = await create_stealth_context(p)
        page = await context.new_page()

        # Inject stealth scripts before navigation
        await page.add_init_script(STEALTH_SCRIPTS)

        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Try to dismiss cookie consent popups
        try:
            # Amazon cookie accept button
            accept_btn = page.locator('[data-action="a]').first
            if await accept_btn.is_visible(timeout=2000):
                await accept_btn.click()
        except:
            pass

        try:
            # Generic "Accept" or "Akzeptieren" buttons
            for selector in ['button:has-text("Accept")', 'button:has-text("Accepteren")', '#sp-cc-accept']:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    break
        except:
            pass

        # Wait for page to stabilize
        await page.wait_for_timeout(2000)

        # Capture above-the-fold area (top 1200px as per spec)
        screenshot_bytes = await page.screenshot(
            type="png",
            clip={"x": 0, "y": 0, "width": 1920, "height": 1200}
        )

        await context.browser.close()

        return screenshot_bytes
