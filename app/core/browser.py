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

    // Aggressive Modal Bypass via MutationObserver
    (function() {
        const hideTags = ['#modalWindow', '.modal', '.cookie-modal', '[data-test="modal-window"]', 'wsp-modal-window', '.consent-modal', '#consent-layer', '[data-type="cookie-modal"]', '[data-type="country-language-modal"]'];
        const hide = () => {
            hideTags.forEach(tag => {
                document.querySelectorAll(tag).forEach(el => {
                    el.style.setProperty('display', 'none', 'important');
                    el.style.setProperty('visibility', 'hidden', 'important');
                    el.style.setProperty('opacity', '0', 'important');
                    el.style.setProperty('pointer-events', 'none', 'important');
                });
            });
            if (document.body) {
                document.body.style.setProperty('overflow', 'auto', 'important');
                document.body.style.setProperty('position', 'static', 'important');
            }
        };
        
        // Initial run
        hide();
        
        // Continuous observer
        const observer = new MutationObserver(hide);
        observer.observe(document.documentElement, { childList: true, subtree: true });
        
        // Final fallback on load
        window.addEventListener('load', hide);
    })();
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
            # Common selectors for Amazon, Bol.com, and others
            # Some sites like Bol.com have stacked modals (Cookie + Language)
            # We use a loop and multiple passes to clear them.
            selectors = [
                '#sp-cc-accept',  # Amazon NL
                '#js-first-screen-accept-all-button',  # Bol.com cookie
                '[data-test="consent-modal-ofc-confirm-btn"]',  # Bol.com alt
                'button:has-text("Alles accepteren")',  # Generic Dutch
                '#js-second-screen-accept-all-button',  # Bol.com 2nd screen
                '[data-test="continue-button"]',  # Bol.com language modal
                'button:has-text("Doorgaan")',  # Bol.com language manual
                'button:has-text("Accept all")',  # Generic English
                'button:has-text("Accepteren")',  # Generic Dutch
                '[data-action="a-cookie-instruction-close"]',  # Amazon close
            ]
            
            # Run up to 3 passes to clear stacked modals
            for _ in range(3):
                clicked_any = False
                for selector in selectors:
                    try:
                        btn = page.locator(selector).first
                        if await btn.is_visible(timeout=2000):
                            await btn.click()
                            await page.wait_for_timeout(1000)
                            clicked_any = True
                    except:
                        continue
                if not clicked_any:
                    break
            
            # Additional surgical bypass: inject CSS again just in case (as a fallback)
            await page.add_style_tag(content="""
                #modalWindow, .modal, .cookie-modal, [data-test="modal-window"], wsp-modal-window {
                    display: none !important;
                }
                body, html {
                    overflow: auto !important;
                    position: static !important;
                }
            """)
        except Exception as e:
            logger.warning(f"Error dismissing modals: {str(e)}")
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
