import random
import asyncio
import logging
from playwright.async_api import async_playwright, BrowserContext

logger = logging.getLogger(__name__)


# Stealth configuration as per SPECS_EXTRACTION_ENGINE.md
STEALTH_CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "locale": "nl-NL",
    "timezone_id": "Europe/Amsterdam",
    "geolocation": {"latitude": 52.3676, "longitude": 4.9041},  # Amsterdam
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
    Object.defineProperty(navigator, 'languages', { get: () => ['nl-NL', 'nl', 'en-US', 'en'] });

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


async def create_stealth_context(playwright) -> BrowserContext:
    """Create a browser context with stealth settings."""
    # Standard 1080p viewport is safer than randomized weird dimensions
    width = 1920
    height = 1080
    
    # Pick a random UA profile
    profile = random.choice([
        {
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "platform": '"Windows"',
            "sec_ch_ua_platform": "Windows"
        },
        {
            "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "platform": '"macOS"',
            "sec_ch_ua_platform": "macOS"
        },
        {
            "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "platform": '"Linux"',
            "sec_ch_ua_platform": "Linux"
        }
    ])
    
    # args to disable automation flags
    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-infobars",
        "--window-position=0,0",
        "--ignore-certificate-errors",
        "--disable-extensions",
        f"--user-agent={profile['ua']}"
    ]

    browser = await playwright.chromium.launch(
        headless=True,
        args=launch_args
    )
    
    context = await browser.new_context(
        viewport={"width": width, "height": height},
        user_agent=profile["ua"],
        locale=STEALTH_CONFIG["locale"],
        timezone_id=STEALTH_CONFIG["timezone_id"],
        geolocation=STEALTH_CONFIG["geolocation"],
        permissions=STEALTH_CONFIG["permissions"],
        # Add extra headers for better stealth
        extra_http_headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": profile["platform"],
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
    )
    return context


async def capture_screenshot(url: str) -> bytes:
    """Navigate to URL and capture screenshot as PNG bytes."""
    async with async_playwright() as p:
        context = await create_stealth_context(p)
        page = await context.new_page()

        # Inject manual stealth scripts
        await page.add_init_script(STEALTH_SCRIPTS)

        # Random delay to simulate human timing (1-3 seconds)
        await asyncio.sleep(random.uniform(1, 3))

        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Try to dismiss cookie consent popups
        try:
            selectors = [
                '#sp-cc-accept', '#js-first-screen-accept-all-button', 
                '[data-test="consent-modal-ofc-confirm-btn"]', 'button:has-text("Alles accepteren")',
                '#onetrust-accept-btn-handler', '#onetrust-banner-sdk'
            ]
            
            for _ in range(3):
                clicked_any = False
                for selector in selectors:
                    try:
                        btn = page.locator(selector).first
                        if await btn.is_visible(timeout=500):
                            await btn.click()
                            await page.wait_for_timeout(500)
                            clicked_any = True
                    except:
                        continue
                if not clicked_any:
                    break
        except Exception:
            pass

        # Wait for page to stabilize
        await page.wait_for_timeout(3000)

        # Capture screenshot
        screenshot_bytes = await page.screenshot(
            type="png",
            clip={"x": 0, "y": 0, "width": 1920, "height": 1200}
        )

        await context.browser.close()
        return screenshot_bytes
