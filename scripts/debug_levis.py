import asyncio
import logging
import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.core.browser import capture_screenshot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = "https://www.levi.com/NL/nl_NL/kleding/dames/jeans/xl-lightweight-overall/p/001V00000"
OUTPUT_FILE = "debug_levis.png"

async def main():
    logger.info(f"Attempting to screenshot: {URL}")
    try:
        screenshot_data = await capture_screenshot(URL)
        
        with open(OUTPUT_FILE, "wb") as f:
            f.write(screenshot_data)
        
        logger.info(f"Screenshot saved to {OUTPUT_FILE}")
        logger.info(f"Size: {len(screenshot_data)} bytes")
        
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
