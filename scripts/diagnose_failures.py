import asyncio
from pathlib import Path

from app.core.browser import capture_screenshot


async def diagnose_sites():
    sites = {
        "stradivarius": "https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125",
        "douglas": "https://www.douglas.nl/nl/p/5010033070",
    }

    Path("diagnostics").mkdir(exist_ok=True)

    for name, url in sites.items():
        print(f"Diagnosing {name}: {url}")
        output_path = Path(f"diagnostics/{name}_check.png")
        try:
            screenshot_bytes = await capture_screenshot(url)
            if screenshot_bytes:
                await asyncio.to_thread(output_path.write_bytes, screenshot_bytes)
                print(f"  [SUCCESS] Screenshot saved to {output_path}")
            else:
                print(f"  [FAILED] Could not capture screenshot for {name}")
        except Exception as e:
            print(f"  [ERROR] {name}: {e!s}")


if __name__ == "__main__":
    asyncio.run(diagnose_sites())
