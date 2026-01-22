
import asyncio
import os
import sys
from app.core.browser import capture_screenshot
from app.core.config import settings

async def diagnose_sites():
    sites = {
        "stradivarius": "https://www.stradivarius.com/nl/silk-eau-de-toilette-no101--100-ml-l00419056?categoryId=1020208533&colorId=310&style=02&pelement=485588125",
        "douglas": "https://www.douglas.nl/nl/p/5010033070"
    }
    
    os.makedirs("diagnostics", exist_ok=True)
    
    for name, url in sites.items():
        print(f"Diagnosing {name}: {url}")
        output_path = f"diagnostics/{name}_check.png"
        try:
            screenshot_bytes = await capture_screenshot(url)
            if screenshot_bytes:
                with open(output_path, "wb") as f:
                    f.write(screenshot_bytes)
                print(f"  [SUCCESS] Screenshot saved to {output_path}")
            else:
                print(f"  [FAILED] Could not capture screenshot for {name}")
        except Exception as e:
            print(f"  [ERROR] {name}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(diagnose_sites())
