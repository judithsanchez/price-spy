#!/usr/bin/env python3
"""Price Spy CLI - Extract product prices from URLs using visual AI."""

import argparse
import asyncio
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

from app.core.browser import capture_screenshot
from app.core.vision import extract_product_info


load_dotenv()


def validate_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


async def main(url: str) -> int:
    """Main entry point."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment", file=sys.stderr)
        return 1

    if not validate_url(url):
        print(f"Error: Invalid URL '{url}'", file=sys.stderr)
        return 1

    try:
        print(f"Capturing screenshot from {url}...", file=sys.stderr)
        screenshot = await capture_screenshot(url)

        print("Extracting product info with Gemini...", file=sys.stderr)
        result = await extract_product_info(screenshot, api_key)

        print(result)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract product prices from URLs using visual AI"
    )
    parser.add_argument("url", nargs="?", help="Product page URL to analyze")

    args = parser.parse_args()

    if not args.url:
        parser.print_usage(sys.stderr)
        print("Error: URL is required", file=sys.stderr)
        sys.exit(1)

    exit_code = asyncio.run(main(args.url))
    sys.exit(exit_code)
