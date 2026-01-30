import asyncio
import logging
import sys

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check input args to decide mode
HEADFUL = True

try:
    from pyvirtualdisplay import Display
except ImportError:
    Display = None


async def main():
    """Debug fingerprint generation for a given URL."""
    logger.info("Starting Fingerprint Diagnostic (Headful=%s)...", HEADFUL)

    # We use the diagnostic site that checks for common bot leaks
    url = "https://bot.sannysoft.com/"

    async with async_playwright() as p:
        # Replicate the Exact startup logic from browser.py (Headful mode)
        profile = {
            "ua": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "platform": '"Linux"',
        }

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--start-maximized",
            f"--user-agent={profile['ua']}",
        ]

        if HEADFUL and sys.platform.startswith("linux") and Display:
            try:
                display = Display(visible=0, size=(1920, 1080))
                display.start()
                logger.info("Virtual Display Started")
            except Exception:
                logger.warning("No Xvfb?")

        logger.info("Launching Browser...")
        browser = await p.chromium.launch(
            headless=False,  # The magic key
            args=launch_args,
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=profile["ua"],
            locale="en-US",
            timezone_id="Europe/Amsterdam",
        )

        page = await context.new_page()

        # Apply Stealth
        stealth = Stealth()
        await stealth.apply_stealth_async(page)

        logger.info("Navigating to %s...", url)
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Take screenshot
        output_file = "debug_fingerprint.png"
        await page.screenshot(path=output_file, full_page=True)
        logger.info("Fingerprint report saved to %s", output_file)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
