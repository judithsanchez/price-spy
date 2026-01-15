"""Demo script to capture and save a screenshot from Amazon.nl"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.core.browser import capture_screenshot


async def main():
    url = "https://www.amazon.nl"
    print(f"Capturing screenshot from {url}...")

    screenshot_bytes = await capture_screenshot(url)

    output_path = "demo_screenshot.png"
    with open(output_path, "wb") as f:
        f.write(screenshot_bytes)

    print(f"Screenshot saved to {output_path} ({len(screenshot_bytes):,} bytes)")
    print("Open the file to see the captured page!")


if __name__ == "__main__":
    asyncio.run(main())
