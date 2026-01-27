import random
import asyncio
import logging
from typing import Optional
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
        "--disable-gpu",  # Often helps on ARM/Raspberry Pi
        f"--user-agent={profile['ua']}"
    ]

    browser = await playwright.chromium.launch(
        headless=True,
        args=launch_args
    )
    
    # Use a taller viewport by default to avoid clipping issues
    context = await browser.new_context(
        viewport={"width": width, "height": 1200},
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


async def handle_zalando_interaction(page, target_size: Optional[str] = None):
    """Specilized interaction for Zalando to handle size selection."""
    if "zalando" not in page.url:
        return

    logger.info(f"Handling Zalando interaction (target_size: {target_size})")
    try:
        # 1. Look for the "Maat kiezen" button
        # Try both role-based and testid-based selectors
        selectors = [
            'button[data-testid="pdp-size-picker-trigger"]',
            'button[data-testid="pdp-size-selector-trigger"]',
            'button:has-text("Maat kiezen")',
            'button:has-text("Select size")',
            'button:has-text("Maat selecteren")'
        ]
        
        size_button = None
        for selector in selectors:
            try:
                btn = page.locator(selector).first
                if await btn.is_visible(timeout=3000):
                    size_button = btn
                    break
            except:
                continue

        if size_button:
            await size_button.scroll_into_view_if_needed()
            await size_button.click()
            logger.info("Clicked Zalando size dropdown")
            await page.wait_for_timeout(1000)
            
            # 2. If target_size provided, try to click it
            if target_size:
                # Zalando sizes are often in a list or grid
                # Try specific data-testid first, then generic buttons
                size_selectors = [
                    f'button[data-testid="pdp-size-selector-item"]:has-text("{target_size}")',
                    f'button[data-testid="pdp-size-picker-item"]:has-text("{target_size}")',
                    f'li[data-testid="pdp-size-selector-item"] button:has-text("{target_size}")',
                    f'button:has-text("{target_size}")'
                ]
                
                size_option = None
                for selector in size_selectors:
                    try:
                        opt = page.locator(selector).first
                        if await opt.is_visible(timeout=2000):
                            size_option = opt
                            break
                    except:
                        continue

                if size_option:
                    await size_option.click()
                    logger.info(f"Clicked Zalando size option: {target_size}")
                    await page.wait_for_timeout(2000) # Wait for price update
                else:
                    logger.warning(f"Zalando size option '{target_size}' not found or not visible")
        else:
            logger.warning("Zalando size button not found")
    except Exception as e:
        logger.error(f"Error during Zalando interaction: {e}")


async def capture_screenshot(url: str, target_size: Optional[str] = None) -> bytes:
    """Navigate to URL and capture screenshot as PNG bytes."""
    async with async_playwright() as p:
        context = await create_stealth_context(p)
        page = await context.new_page()

        # Inject manual stealth scripts
        await page.add_init_script(STEALTH_SCRIPTS)

        # Random delay to simulate human timing (1-3 seconds)
        await asyncio.sleep(random.uniform(1, 4))

        try:
            # Use 'networkidle' to ensure images/styles are loaded
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            logger.warning(f"Networkidle failed for {url}, falling back to domcontentloaded: {e}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e2:
                logger.error(f"Failed to navigate to {url}: {e2}")
                await context.browser.close()
                raise

        # Try to dismiss cookie consent popups
        try:
            selectors = [
                '#sp-cc-accept', '#js-first-screen-accept-all-button', 
                '[data-test="consent-modal-ofc-confirm-btn"]', 'button:has-text("Alles accepteren")',
                '#onetrust-accept-btn-handler', '#onetrust-banner-sdk',
                'button:has-text("Accepteren")', 'button:has-text("Accept All")',
                '.uc-btn-accept'
            ]
            
            for _ in range(3):
                clicked_any = False
                for selector in selectors:
                    try:
                        btn = page.locator(selector).first
                        if await btn.is_visible(timeout=500):
                            await btn.click()
                            await page.wait_for_timeout(1000) # Give it time to disappear
                            clicked_any = True
                    except:
                        continue
                if not clicked_any:
                    break
        except Exception:
            pass

        # Handle Zalando specifically if needed
        if "zalando" in url:
            await handle_zalando_interaction(page, target_size)

        # Try to find a product image or main title to scroll to
        try:
            product_selectors = [
                'h1', 'img[data-testid="pdp-main-image"]', 
                '.product-title', '.pdp-info', '#productTitle',
                '.pdp__name', '.pdp__price'
            ]
            for selector in product_selectors:
                el = page.locator(selector).first
                if await el.is_visible(timeout=2000):
                    await el.scroll_into_view_if_needed()
                    # Scroll a bit more up to show context
                    await page.mouse.wheel(0, -150)
                    break
        except:
            pass

        # Wait for page to stabilize
        await page.wait_for_timeout(3000)

        # Capture screenshot - using 1280x960 to get a better thumbnail aspect ratio
        screenshot_bytes = await page.screenshot(
            type="png",
            clip={"x": 0, "y": 0, "width": 1280, "height": 960}
        )

        await context.browser.close()
        return screenshot_bytes
