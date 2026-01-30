import asyncio
import logging
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path.cwd()))

from app.core.browser import capture_screenshot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = (
    "https://www.levi.com/NL/nl_NL/kleding/dames/jeans/"
    "xl-lightweight-overall/p/001V00000"
)
OUTPUT_FILE = "debug_levis.png"


async def main():
    logger.info("Attempting to screenshot: %s", URL)
    try:
        screenshot_data = await capture_screenshot(URL)

        # Use async file writing
        await asyncio.to_thread(Path(OUTPUT_FILE).write_bytes, screenshot_data)

        logger.info("Screenshot saved to %s", OUTPUT_FILE)
        logger.info("Size: %d bytes", len(screenshot_data))

    except Exception:
        logger.exception("Failed to capture screenshot")


if __name__ == "__main__":
    asyncio.run(main())
