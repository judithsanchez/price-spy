#!/usr/bin/env python3
"""Price Spy CLI - Extract product prices from URLs using visual AI."""

import argparse
import asyncio
import json
import logging
import sys
import time
import traceback
from pathlib import Path
from urllib.parse import urlparse

from app.core.browser import capture_screenshot
from app.core.config import settings
from app.core.price_calculator import calculate_volume_price, compare_prices
from app.core.vision import extract_with_structured_output
from app.models.schemas import (
    ErrorRecord,
    PriceHistoryRecord,
    Product,
    Store,
    TrackedItem,
)
from app.storage.database import get_database
from app.storage.repositories import (
    ErrorLogRepository,
    PriceHistoryRepository,
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


def validate_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def init_repositories():
    """Initialize database repositories."""
    db = get_database()
    return (
        db,
        ErrorLogRepository(db),
        PriceHistoryRepository(db),
        TrackedItemRepository(db),
    )


async def perform_extraction(url: str, api_key: str):
    """Capture screenshot and extract product info."""
    logger.info("Starting price extraction", extra={"url": url})
    print(f"Capturing screenshot from {url}...", file=sys.stderr)
    screenshot = await capture_screenshot(url)
    print("Extracting product info with Gemini...", file=sys.stderr)
    return await extract_with_structured_output(screenshot, api_key)


def _print_product_details(result, model_used):
    """Print basic product and price details."""
    print(f"\nProduct: {result.product_name}")
    print(f"Price: {result.currency} {result.price}")
    if result.original_price and result.original_price > result.price:
        savings = (result.original_price - result.price) / result.original_price * 100
        print(
            f"Original Price: {result.currency} {result.original_price} "
            f"(Save {savings:.0f}%)"
        )

    if result.deal_type and result.deal_type != "none":
        print(f"PROMO: {result.deal_type}")
        if result.discount_percentage:
            print(f"  Discount: {result.discount_percentage}% off")
        if result.discount_fixed_amount:
            print(f"  Discount: {result.currency} {result.discount_fixed_amount} off")
        if result.deal_description:
            print(f"  Details: {result.deal_description}")

    if result.store_name:
        print(f"Store: {result.store_name}")
    print(f"Stock: {'Available' if result.is_available else 'Out of stock'}")
    if result.notes:
        print(f"Notes: {result.notes}")
    if result.available_sizes:
        print(f"Detected sizes: {', '.join(result.available_sizes)}")
    print(f"Model used: {model_used}")


def _print_tracked_info(result, tracked):
    """Print volume price if tracked."""
    if tracked:
        vol_price, vol_unit = calculate_volume_price(
            result.price,
            tracked.items_per_lot,
            tracked.quantity_size,
            tracked.quantity_unit,
        )
        print(f"Unit price: {result.currency} {vol_price:.2f}/{vol_unit}")


def _print_comparison_info(result, previous, comparison):
    """Print price comparison and deal detection."""
    if previous:
        if comparison.price_change != 0:
            direction = "↓" if comparison.is_price_drop else "↑"
            change_val = abs(float(comparison.price_change or 0))
            change_pct = comparison.price_change_percent or 0
            print(f"Price change: {direction} {change_val:.2f} ({change_pct:+.1f}%)")
        else:
            print("Price unchanged since last check")

    if comparison.is_deal:
        print("\n*** DEAL DETECTED ***")
        if comparison.is_price_drop:
            change_val = abs(float(comparison.price_change or 0))
            print(f"-> Price dropped by {change_val:.2f} {result.currency}")
        if comparison.original_price and comparison.original_price > result.price:
            print(
                f"-> Promotion: {result.currency} {result.price} "
                f"(was {comparison.original_price})"
            )
        if comparison.deal_type:
            print(f"-> Offer: {comparison.deal_type}")


async def cmd_extract(args) -> int:
    """Extract price from URL."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.error("GEMINI_API_KEY not set in environment")
        print("Error: GEMINI_API_KEY not set in environment", file=sys.stderr)
        return 1

    if not validate_url(args.url):
        logger.error("Invalid URL provided", extra={"url": args.url})
        print(f"Error: Invalid URL '{args.url}'", file=sys.stderr)
        return 1

    db = None
    try:
        db, _, price_repo, tracked_repo = init_repositories()
        result, model_used = await perform_extraction(args.url, api_key)

        # Check for tracked item and previous price
        tracked = tracked_repo.get_by_url(args.url)
        previous = price_repo.get_latest_by_url(args.url)

        # Save to database
        record = PriceHistoryRecord(
            product_name=result.product_name,
            price=result.price,
            currency=result.currency,
            is_available=result.is_available,
            confidence=1.0,
            url=args.url,
            store_name=result.store_name,
            page_type="single_product",
            notes=result.notes,
            original_price=result.original_price,
            deal_type=result.deal_type,
            discount_percentage=result.discount_percentage,
            discount_fixed_amount=result.discount_fixed_amount,
            deal_description=result.deal_description,
            available_sizes=(
                json.dumps(result.available_sizes) if result.available_sizes else None
            ),
        )
        record_id = price_repo.insert(record)
        logger.info("Price saved to database", extra={"record_id": record_id})
    except Exception as e:
        logger.exception("Price extraction failed", extra={"url": args.url})
        if db:
            ErrorLogRepository(db).insert(
                ErrorRecord(
                    error_type="extraction_error",
                    message=str(e)[:2000],
                    url=args.url,
                    stack_trace=traceback.format_exc(),
                )
            )
        print(f"Error: {e}", file=sys.stderr)
        return 1
    else:
        _print_product_details(result, model_used)
        _print_tracked_info(result, tracked)

        comparison = compare_prices(
            result.price,
            previous.price if previous else None,
            original_price=result.original_price,
            deal_info={
                "deal_type": result.deal_type,
                "discount_percentage": result.discount_percentage,
                "discount_fixed_amount": result.discount_fixed_amount,
                "deal_description": result.deal_description,
            },
        )
        _print_comparison_info(result, previous, comparison)
        return 0
    finally:
        if db:
            db.close()


def _ensure_api_key() -> bool:
    if not settings.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set in environment", file=sys.stderr)
        return False
    return True


def _build_output_path(url: str) -> Path:
    diag_dir = Path("diagnostics")
    diag_dir.mkdir(parents=True, exist_ok=True)
    domain = urlparse(url).netloc.replace(".", "_")
    timestamp = int(time.time())
    return diag_dir / f"check_{domain}_{timestamp}.png"


async def _capture_screenshot_to_file(url: str, output_path: Path) -> bytes:
    print(f"Checking URL: {url}")
    print("Capturing screenshot...")
    screenshot = await capture_screenshot(url)

    # Run blocking file I/O in executor
    await asyncio.to_thread(output_path.write_bytes, screenshot)

    print(f"Screenshot saved to: {output_path}")
    return screenshot


def _print_diagnostic_results(result, model_used):
    """Print diagnostic results from AI analysis."""
    print("\n--- Diagnostic Results ---")
    print(f"Detection Status: {'BLOCKED' if result.is_blocked else 'CLEAR'}")
    if result.is_blocked:
        print("WARN: Site blocked by cookie modal/overlay (detection may be partial).")

    print(f"Store Detected: {result.store_name if result.store_name else 'Unknown'}")
    print(
        f"Product Detected: {result.product_name if result.product_name else 'Unknown'}"
    )
    print(
        f"Price Found: {result.currency} {result.price if result.price > 0 else 'N/A'}"
    )
    if result.original_price:
        print(f"Original Price: {result.currency} {result.original_price}")

    if result.deal_type and result.deal_type != "none":
        print(f"Deal Type: {result.deal_type}")
        if result.discount_percentage:
            print(f"Discount Percentage: {result.discount_percentage}%")
        if result.discount_fixed_amount:
            print(
                f"Discount Fixed Amount: {result.currency} "
                f"{result.discount_fixed_amount}"
            )

    if result.deal_description:
        print(f"Deal Description: {result.deal_description}")

    print(f"Model Used: {model_used}")
    print("--------------------------")

    if not result.is_blocked and result.price > 0:
        print("\nSuccess: This URL is likely compatible with Price Spy.")
    elif result.is_blocked:
        print("\nWarning: This site is detecting the bot or has persistent modals.")
    else:
        print(
            "\nInconclusive: Screenshot captured, but AI couldn't find clear "
            "product data."
        )


async def cmd_check(args) -> int:
    """Check if a URL is accessible and visible to the AI."""
    if not _ensure_api_key():
        return 1

    if not validate_url(args.url):
        print(f"Error: Invalid URL '{args.url}'", file=sys.stderr)
        return 1

    try:
        output_path = _build_output_path(args.url)
        screenshot = await _capture_screenshot_to_file(args.url, output_path)
        print("Analyzing with AI...")
        result, model_used = await extract_with_structured_output(
            screenshot, settings.GEMINI_API_KEY
        )
    except Exception as e:
        print(f"Error during check: {e}", file=sys.stderr)
        return 1

    _print_diagnostic_results(result, model_used)
    return 0


def cmd_add_product(args) -> int:
    """Add a new product."""
    db = None
    try:
        db = get_database()
        repo = ProductRepository(db)
        product = Product(
            name=args.name,
            category=args.category,
            target_price=args.target_price,
            target_unit=args.unit_size,
        )
        product_id = repo.insert(product)
    except Exception:
        logging.exception("Error adding product")
        return 1
    else:
        print(f"Product added with ID: {product_id}")
        print(f"  Name: {args.name}")
        if args.category:
            print(f"  Category: {args.category}")
        if args.target_price:
            print(f"  Target price: {args.target_price}")
        return 0
    finally:
        if db:
            db.close()


def cmd_add_store(args) -> int:
    """Add a new store."""
    db = None
    try:
        db = get_database()
        repo = StoreRepository(db)
        store = Store(
            name=args.name,
        )
        store_id = repo.insert(store)
    except Exception:
        logging.exception("Error adding store")
        return 1
    else:
        print(f"Store added with ID: {store_id}")
        print(f"  Name: {args.name}")
        if args.shipping:
            print(f"  Shipping: {args.shipping}")
        if args.free_threshold:
            print(f"  Free shipping above: {args.free_threshold}")
        return 0
    finally:
        if db:
            db.close()


def cmd_track(args) -> int:
    """Track a URL."""
    if not validate_url(args.url):
        print(f"Error: Invalid URL '{args.url}'", file=sys.stderr)
        return 1

    db = None
    try:
        db = get_database()
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)

        # Verify product exists
        product = product_repo.get_by_id(args.product_id)
        if not product:
            print(
                f"Error: Product with ID {args.product_id} not found", file=sys.stderr
            )
            return 1

        # Verify store exists
        store = store_repo.get_by_id(args.store_id)
        if not store:
            print(f"Error: Store with ID {args.store_id} not found", file=sys.stderr)
            return 1

        # Check if URL already tracked
        existing = tracked_repo.get_by_url(args.url)
        if existing:
            print(f"Error: URL is already tracked (ID: {existing.id})", file=sys.stderr)
            return 1

        item = TrackedItem(
            product_id=args.product_id,
            store_id=args.store_id,
            url=args.url,
            quantity_size=args.size,
            quantity_unit=args.unit,
            items_per_lot=args.lot or 1,
        )
        item_id = tracked_repo.insert(item)

    except Exception:
        logging.exception("Error tracking URL")
        return 1
    else:
        print(f"Tracking URL with ID: {item_id}")
        print(f"  Product: {product.name}")
        print(f"  Store: {store.name}")
        print(f"  Size: {args.size}{args.unit}")
        if args.lot and args.lot > 1:
            print(f"  Items per lot: {args.lot}")
        return 0
    finally:
        if db:
            db.close()


def _list_products(repo):
    """List products from repository."""
    products = repo.get_all()
    if not products:
        print("No products found.")
        return
    print(f"{'ID':<4} {'Name':<30} {'Category':<15} {'Target':<10}")
    print("-" * 60)
    for p in products:
        target = f"{p.target_price:.2f}" if p.target_price else "-"
        cat = p.category or "-"
        print(f"{p.id:<4} {p.name[:30]:<30} {cat[:15]:<15} {target:<10}")


def _list_stores(repo):
    """List stores from repository."""
    stores = repo.get_all()
    if not stores:
        print("No stores found.")
        return
    print(f"{'ID':<4} {'Name':<25}")
    print("-" * 30)
    for s in stores:
        print(f"{s.id:<4} {s.name[:25]:<25}")


def _list_tracked(tracked_repo, product_repo, store_repo):
    """List tracked items from repository."""
    items = tracked_repo.get_active()
    if not items:
        print("No tracked items found.")
        return
    print(f"{'ID':<4} {'Product':<20} {'Store':<15} {'Size':<12} {'URL':<40}")
    print("-" * 95)
    for item in items:
        product = product_repo.get_by_id(item.product_id)
        store = store_repo.get_by_id(item.store_id)
        size_str = f"{item.quantity_size}{item.quantity_unit}"
        if item.items_per_lot > 1:
            size_str += f" x{item.items_per_lot}"
        pname = product.name[:20] if product else "?"
        sname = store.name[:15] if store else "?"
        print(f"{item.id:<4} {pname:<20} {sname:<15} {size_str:<12} {item.url[:40]}")


def cmd_list(args) -> int:
    """List tracked items, products, or stores."""
    db = None
    try:
        db = get_database()
        if args.what == "products":
            _list_products(ProductRepository(db))
        elif args.what == "stores":
            _list_stores(StoreRepository(db))
        else:  # tracked items (default)
            _list_tracked(
                TrackedItemRepository(db),
                ProductRepository(db),
                StoreRepository(db),
            )
    except Exception:
        logging.exception("Error listing items")
        return 1
    else:
        return 0
    finally:
        if db:
            db.close()


def main():
    """Main entry point with subcommands."""
    parser = argparse.ArgumentParser(
        description="Price Spy - Extract and track product prices using visual AI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract price from URL")
    extract_parser.add_argument("url", help="Product page URL to analyze")
    extract_parser.add_argument(
        "--model", "-m", help="Gemini model to use (e.g., 'gemini-2.0-flash-lite')"
    )

    # Add product command
    product_parser = subparsers.add_parser("add-product", help="Add a new product")
    product_parser.add_argument("name", help="Product name")
    product_parser.add_argument("--category", "-c", help="Product category")
    product_parser.add_argument(
        "--target-price", "-t", type=float, help="Target price for alerts"
    )
    product_parser.add_argument(
        "--unit-size", "-u", help="Preferred unit size (e.g., '250ml')"
    )

    # Add store command
    store_parser = subparsers.add_parser("add-store", help="Add a new store")
    store_parser.add_argument("name", help="Store name")
    store_parser.add_argument(
        "--shipping", "-s", type=float, help="Standard shipping cost"
    )
    store_parser.add_argument(
        "--free-threshold", "-f", type=float, help="Free shipping threshold"
    )

    # Track command
    track_parser = subparsers.add_parser("track", help="Track a URL")
    track_parser.add_argument("url", help="URL to track")
    track_parser.add_argument(
        "--product-id", "-p", type=int, required=True, help="Product ID"
    )
    track_parser.add_argument(
        "--store-id", "-s", type=int, required=True, help="Store ID"
    )
    track_parser.add_argument(
        "--size", type=float, required=True, help="Quantity size (e.g., 250)"
    )
    track_parser.add_argument(
        "--unit", "-u", required=True, help="Unit (e.g., 'ml', 'g', 'L')"
    )
    track_parser.add_argument(
        "--lot", "-l", type=int, help="Items per lot (default: 1)"
    )
    track_parser.add_argument(
        "--model", "-m", help="Preferred Gemini model for this item"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List items")
    list_parser.add_argument(
        "what",
        nargs="?",
        default="tracked",
        choices=["tracked", "products", "stores"],
        help="What to list (default: tracked)",
    )

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Test a new URL for compatibility"
    )
    check_parser.add_argument("url", help="URL to test")

    args = parser.parse_args()

    if args.command is None:
        if len(sys.argv) > 1 and validate_url(sys.argv[1]):
            args.command = "extract"
            args.url = sys.argv[1]
        else:
            parser.print_help()
            return 1

    # Route to appropriate command
    cmd_map = {
        "extract": lambda: asyncio.run(cmd_extract(args)),
        "add-product": lambda: cmd_add_product(args),
        "add-store": lambda: cmd_add_store(args),
        "track": lambda: cmd_track(args),
        "list": lambda: cmd_list(args),
        "check": lambda: asyncio.run(cmd_check(args)),
    }

    handler = cmd_map.get(args.command)
    if handler:
        return handler()

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
