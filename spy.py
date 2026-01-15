#!/usr/bin/env python3
"""Price Spy CLI - Extract product prices from URLs using visual AI."""

import argparse
import asyncio
import os
import sys
import traceback
from urllib.parse import urlparse

from dotenv import load_dotenv

from app.core.browser import capture_screenshot
from app.core.vision import extract_product_info
from app.models.schemas import ProductInfo, ErrorRecord, PriceHistoryRecord
from app.storage.database import Database
from app.storage.repositories import PriceHistoryRepository, ErrorLogRepository
from app.utils.logging import get_logger


load_dotenv()

logger = get_logger(__name__)


def validate_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def get_database() -> Database:
    """Initialize and return database connection."""
    db = Database("data/pricespy.db")
    db.initialize()
    return db


async def main(url: str) -> int:
    """Main entry point."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set in environment")
        print("Error: GEMINI_API_KEY not set in environment", file=sys.stderr)
        return 1

    if not validate_url(url):
        logger.error("Invalid URL provided", extra={"url": url})
        print(f"Error: Invalid URL '{url}'", file=sys.stderr)
        return 1

    db = get_database()
    error_repo = ErrorLogRepository(db)
    price_repo = PriceHistoryRepository(db)

    try:
        logger.info("Starting price extraction", extra={"url": url})
        print(f"Capturing screenshot from {url}...", file=sys.stderr)
        screenshot = await capture_screenshot(url)

        print("Extracting product info with Gemini...", file=sys.stderr)
        result = await extract_product_info(screenshot, api_key)

        # Handle structured result
        if isinstance(result, ProductInfo):
            # Save to database
            record = PriceHistoryRecord(
                product_name=result.product_name,
                price=result.price,
                currency=result.currency,
                confidence=result.confidence,
                url=url,
                store_name=result.store_name,
                page_type=result.page_type,
            )
            record_id = price_repo.insert(record)
            logger.info("Price saved to database", extra={"record_id": record_id})

            # Output structured result
            print(f"Product: {result.product_name}")
            print(f"Price: {result.currency} {result.price}")
            if result.store_name:
                print(f"Store: {result.store_name}")
            print(f"Confidence: {result.confidence:.0%}")
        else:
            # Fallback to raw text output
            print(result)

        return 0

    except Exception as e:
        error_msg = str(e)
        stack = traceback.format_exc()

        # Log and save error
        logger.error("Price extraction failed", extra={"url": url, "error": error_msg})
        error_repo.insert(ErrorRecord(
            error_type="extraction_error",
            message=error_msg[:2000],
            url=url,
            stack_trace=stack,
        ))

        print(f"Error: {e}", file=sys.stderr)
        return 1

    finally:
        db.close()


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
