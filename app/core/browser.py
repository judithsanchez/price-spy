import asyncio
import logging
import random

from playwright.async_api import BrowserContext, async_playwright

logger = logging.getLogger(__name__)


# Stealth configuration as per SPECS_EXTRACTION_ENGINE.md
STEALTH_CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "locale": "nl-NL",
    "timezone_id": "Europe/Amsterdam",
    "geolocation": {
        "latitude": 52.3676,
        "longitude": 4.9041,
    },  # Amsterdam
    "permissions": ["geolocation"],
}

# JavaScript to mask automation detection
# Advanced JavaScript to mask automation detection (Akamai/EdgeSuite bypass)
STEALTH_SCRIPTS = """
(lambda) => {
    // Pass the Webdriver Test
    Object.defineProperty(navigator, 'webdriver', { get: () => false });

    // Pass the Plugins Length Test
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

    // Pass the Languages Test
    Object.defineProperty(
        navigator,
        'languages',
        { get: () => ['nl-NL', 'nl', 'en-US', 'en'] }
    );

    // Mock Chrome runtime
    window.chrome = { runtime: {} };

    // Overwrite the 'notification' permission
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
};
"""


def _get_random_ua_profile():
    """Pick a random UA profile."""
    return random.choice(  # noqa: S311 # nosec B311
        [
            {
                "ua": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                "platform": '"Windows"',
                "sec_ch_ua_platform": "Windows",
            },
            {
                "ua": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "platform": '"macOS"',
                "sec_ch_ua_platform": "macOS",
            },
            {
                "ua": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                "platform": '"Linux"',
                "sec_ch_ua_platform": "Linux",
            },
        ]
    )


async def create_stealth_context(playwright) -> BrowserContext:
    """Create a browser context with stealth settings."""
    # Standard 1080p viewport is safer than randomized weird dimensions
    width = 1920

    # Pick a random UA profile
    profile = _get_random_ua_profile()

    # args to disable automation flags
    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-infobars",
        "--window-position=0,0",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--disable-gpu",  # Often helps on ARM/Raspberry Pi
        f"--user-agent={profile['ua']}",
    ]

    browser = await playwright.chromium.launch(headless=True, args=launch_args)

    # Use a taller viewport by default to avoid clipping issues
    return await browser.new_context(
        viewport={"width": width, "height": 1200},
        user_agent=profile["ua"],
        locale=STEALTH_CONFIG["locale"],
        timezone_id=STEALTH_CONFIG["timezone_id"],
        geolocation=STEALTH_CONFIG["geolocation"],
        permissions=STEALTH_CONFIG["permissions"],
        # Add extra headers for better stealth
        extra_http_headers={
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            ),
            "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Ch-Ua": (
                '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            ),
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": profile["platform"],
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        },
    )


async def _find_zalando_size_button(page):
    """Find and click the Zalando size picker button."""
    selectors = [
        'button[data-testid="pdp-size-picker-trigger"]',
        'button[data-testid="pdp-size-selector-trigger"]',
        'button:has-text("Maat kiezen")',
        'button:has-text("Select size")',
        'button:has-text("Maat selecteren")',
    ]

    for selector in selectors:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=3000):
                await btn.scroll_into_view_if_needed()
                await btn.click()
                logger.info("Clicked Zalando size dropdown")
                await page.wait_for_timeout(1000)
                return True
        except Exception:
            logger.debug("Selector %s not found on Zalando", selector)
            continue
    return False


async def _select_zalando_size(page, target_size: str):
    """Try to find and click the specific target size."""
    size_selectors = [
        f'button[data-testid="pdp-size-selector-item"]:has-text("{target_size}")',
        f'button[data-testid="pdp-size-picker-item"]:has-text("{target_size}")',
        (f'li[data-testid="pdp-size-selector-item"] button:has-text("{target_size}")'),
        f'button:has-text("{target_size}")',
    ]

    for selector in size_selectors:
        try:
            opt = page.locator(selector).first
            if await opt.is_visible(timeout=2000):
                await opt.click()
                logger.info("Clicked Zalando size option: %s", target_size)
                await page.wait_for_timeout(2000)
                return True
        except Exception:  # noqa: S112 # nosec B112
            continue
    return False


async def handle_zalando_interaction(page, target_size: str | None = None):
    """Specilized interaction for Zalando to handle size selection."""
    if "zalando" not in page.url:
        return

    logger.info("Handling Zalando interaction (target_size: %s)", target_size)
    try:
        # 1. Look for the "Maat kiezen" button
        button_clicked = await _find_zalando_size_button(page)

        if button_clicked and target_size:
            # 2. Try to click the specific size
            size_selected = await _select_zalando_size(page, target_size)
            if not size_selected:
                logger.warning("Zalando size option '%s' not found", target_size)
        elif not button_clicked:
            logger.warning("Zalando size button not found")
    except Exception:
        logger.exception("Error during Zalando interaction")


async def _dismiss_cookie_consent(page):
    """Try to dismiss cookie consent popups."""
    selectors = [
        "#sp-cc-accept",
        "#js-first-screen-accept-all-button",
        '[data-test="consent-modal-ofc-confirm-btn"]',
        'button:has-text("Alles accepteren")',
        "#onetrust-accept-btn-handler",
        "#onetrust-banner-sdk",
        'button:has-text("Accepteren")',
        'button:has-text("Accept All")',
        ".uc-btn-accept",
    ]

    try:
        for _ in range(3):
            clicked_any = False
            for selector in selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.is_visible(timeout=500):
                        await btn.click()
                        await page.wait_for_timeout(1000)
                        clicked_any = True
                except Exception:  # noqa: S112 # nosec B112
                    continue
            if not clicked_any:
                break
    except Exception as e:
        logger.debug("Cookie consent handling failed: %s", e)


async def _scroll_to_product(page):
    """Try to find a product image or main title to scroll to and center it."""
    product_selectors = [
        "h1",
        "h2",  # Added h2 as fallback
        'img[data-testid="pdp-main-image"]',
        'img[alt*="product"]',  # Generic fallback
        ".product-title",
        ".pdp-info",
        "#productTitle",
        ".pdp__name",
        ".pdp__price",
    ]
    try:
        for selector in product_selectors:
            el = page.locator(selector).first
            if await el.is_visible(timeout=2000):
                # Try to center the element in the viewport
                await el.scroll_into_view_if_needed()
                # Subtle adjustment to pull it slightly up if it's a big element
                await page.mouse.wheel(0, -100)
                break
    except Exception as e:
        logger.debug("Scrolling to product failed: %s", e)


async def capture_screenshot(url: str, target_size: str | None = None) -> bytes:
    """Navigate to URL and capture screenshot as PNG bytes."""
    async with async_playwright() as p:
        context = await create_stealth_context(p)
        page = await context.new_page()

        await page.add_init_script(STEALTH_SCRIPTS)
        await asyncio.sleep(random.uniform(1, 4))  # noqa: S311 # nosec B311

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            logger.warning("Networkidle failed for %s, falling back: %s", url, e)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception:
                logger.exception("Failed to navigate to %s", url)
                raise

        # Try to dismiss cookie consent popups
        await _dismiss_cookie_consent(page)

        # Handle Zalando specifically if needed
        if "zalando" in url:
            await handle_zalando_interaction(page, target_size)

        # Try to find a product image or main title to scroll to
        await _scroll_to_product(page)

        # Wait for page to stabilize
        await page.wait_for_timeout(3000)

        # Capture screenshot (removed hardcoded clip to use full viewport)
        screenshot_bytes = await page.screenshot(type="png")

        if context.browser:
            await context.browser.close()
        return screenshot_bytes
