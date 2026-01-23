#!/usr/bin/env python3
"""Price Spy CLI - Extract product prices from URLs using visual AI."""

import argparse
import asyncio
import os
import sys
import time
import traceback
from urllib.parse import urlparse

from app.core.config import settings
from app.core.browser import capture_screenshot
from app.core.vision import extract_with_structured_output
from app.core.price_calculator import calculate_volume_price, compare_prices
from app.models.schemas import (
    ErrorRecord,
    PriceHistoryRecord,
    Product,
    Store,
    TrackedItem,
)

from app.storage.database import get_database
from app.storage.repositories import (
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
    PriceHistoryRepository,
    ErrorLogRepository,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)

def validate_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

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

    db = get_database()
    error_repo = ErrorLogRepository(db)
    price_repo = PriceHistoryRepository(db)
    tracked_repo = TrackedItemRepository(db)

    try:
        logger.info("Starting price extraction", extra={"url": args.url})
        print(f"Capturing screenshot from {args.url}...", file=sys.stderr)
        screenshot = await capture_screenshot(args.url)

        print("Extracting product info with Gemini...", file=sys.stderr)
        preferred_model = getattr(args, "model", None)
        result, model_used = await extract_with_structured_output(screenshot, api_key, preferred_model=preferred_model)
        
        # Check for tracked item to get volume info
        tracked = tracked_repo.get_by_url(args.url)

        # Get previous price for comparison
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
            deal_description=result.deal_description,
        )
        record_id = price_repo.insert(record)
        logger.info("Price saved to database", extra={"record_id": record_id})

        # Output structured result
        print(f"\nProduct: {result.product_name}")
        print(f"Price: {result.currency} {result.price}")
        if result.original_price and result.original_price > result.price:
            print(f"Original Price: {result.currency} {result.original_price} (Save {((result.original_price-result.price)/result.original_price)*100:.0f}%)")
        
        if result.deal_type:
            print(f"PROMO: {result.deal_type}")
            if result.deal_description:
                print(f"Details: {result.deal_description}")

        if result.store_name:
            print(f"Store: {result.store_name}")
        print(f"Stock: {'Available' if result.is_available else 'Out of stock'}")
        if result.notes:
            print(f"Notes: {result.notes}")
        print(f"Model used: {model_used}")

        # Show volume price if tracked
        if tracked:
            vol_price, vol_unit = calculate_volume_price(
                result.price,
                tracked.items_per_lot,
                tracked.quantity_size,
                tracked.quantity_unit,
            )
            print(f"Unit price: {result.currency} {vol_price:.2f}/{vol_unit}")

        # Show price comparison
        comparison = compare_prices(
            result.price, 
            previous.price if previous else None,
            original_price=result.original_price,
            deal_type=result.deal_type,
            deal_description=result.deal_description
        )
        
        if previous:
            if comparison.price_change != 0:
                direction = "↓" if comparison.is_price_drop else "↑"
                print(
                    f"Price change: {direction} {abs(comparison.price_change):.2f} "
                    f"({comparison.price_change_percent:+.1f}%)"
                )
            else:
                print("Price unchanged since last check")

        if comparison.is_deal:
            print("\n*** DEAL DETECTED ***")
            if comparison.is_price_drop:
                print(f"-> Price dropped by {abs(comparison.price_change):.2f} {result.currency}")
            if comparison.original_price and comparison.original_price > result.price:
                print(f"-> Promotion: {comparison.currency} {result.price} (was {comparison.original_price})")
            if comparison.deal_type:
                print(f"-> Offer: {comparison.deal_type}")

        return 0

    except Exception as e:
        error_msg = str(e)
        stack = traceback.format_exc()

        logger.error("Price extraction failed", extra={"url": args.url, "error": error_msg})
        error_repo.insert(ErrorRecord(
            error_type="extraction_error",
            message=error_msg[:2000],
            url=args.url,
            stack_trace=stack,
        ))

        print(f"Error: {e}", file=sys.stderr)
        return 1

    finally:
        db.close()


async def cmd_check(args) -> int:
    """Check if a URL is accessible and visible to the AI."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("Error: GEMINI_API_KEY not set in environment", file=sys.stderr)
        return 1

    if not validate_url(args.url):
        print(f"Error: Invalid URL '{args.url}'", file=sys.stderr)
        return 1

    try:
        os.makedirs("diagnostics", exist_ok=True)
        domain = urlparse(args.url).netloc.replace(".", "_")
        timestamp = int(time.time())
        output_path = f"diagnostics/check_{domain}_{timestamp}.png"

        print(f"Checking URL: {args.url}")
        print(f"Capturing screenshot...")
        screenshot = await capture_screenshot(args.url)
        
        with open(output_path, "wb") as f:
            f.write(screenshot)
        print(f"Screenshot saved to: {output_path}")

        print("Analyzing with AI...")
        result, model_used = await extract_with_structured_output(screenshot, api_key)
        
        print("\n--- Diagnostic Results ---")
        print(f"Detection Status: {'BLOCKED' if result.is_blocked else 'CLEAR'}")
        if result.is_blocked:
            print("Page appears to be blocked by a modal, captcha, or WAF.")
        
        print(f"Store Detected: {result.store_name if result.store_name else 'Unknown'}")
        print(f"Product Detected: {result.product_name if result.product_name else 'Unknown'}")
        print(f"Price Found: {result.currency} {result.price if result.price > 0 else 'N/A'}")
        if result.original_price:
            print(f"Original Price: {result.currency} {result.original_price}")
        if result.deal_type and result.deal_type != 'none':
            print(f"Deal Type: {result.deal_type}")
        if result.deal_description:
            print(f"Deal Description: {result.deal_description}")
        print(f"Model Used: {model_used}")
        print("--------------------------")
        
        if not result.is_blocked and result.price > 0:
            print("\nSuccess: This URL is likely compatible with Price Spy.")
        elif result.is_blocked:
            print("\nWarning: This site is detecting the bot or has persistent modals.")
        else:
            print("\nInconclusive: Screenshot captured, but AI couldn't find clear product data.")

        return 0
    except Exception as e:
        print(f"Error during check: {e}", file=sys.stderr)
        return 1


def cmd_add_product(args) -> int:
    """Add a new product."""
    db = get_database()
    repo = ProductRepository(db)

    try:
        product = Product(
            name=args.name,
            category=args.category,
            target_price=args.target_price,
            preferred_unit_size=args.unit_size,
        )
        product_id = repo.insert(product)
        print(f"Product added with ID: {product_id}")
        print(f"  Name: {args.name}")
        if args.category:
            print(f"  Category: {args.category}")
        if args.target_price:
            print(f"  Target price: {args.target_price}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


def cmd_add_store(args) -> int:
    """Add a new store."""
    db = get_database()
    repo = StoreRepository(db)

    try:
        store = Store(
            name=args.name,
            shipping_cost_standard=args.shipping or 0,
            free_shipping_threshold=args.free_threshold,
        )
        store_id = repo.insert(store)
        print(f"Store added with ID: {store_id}")
        print(f"  Name: {args.name}")
        if args.shipping:
            print(f"  Shipping: {args.shipping}")
        if args.free_threshold:
            print(f"  Free shipping above: {args.free_threshold}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


def cmd_track(args) -> int:
    """Track a URL."""
    if not validate_url(args.url):
        print(f"Error: Invalid URL '{args.url}'", file=sys.stderr)
        return 1

    db = get_database()
    product_repo = ProductRepository(db)
    store_repo = StoreRepository(db)
    tracked_repo = TrackedItemRepository(db)

    try:
        # Verify product exists
        product = product_repo.get_by_id(args.product_id)
        if not product:
            print(f"Error: Product with ID {args.product_id} not found", file=sys.stderr)
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
            preferred_model=getattr(args, "model", None)
        )
        item_id = tracked_repo.insert(item)

        print(f"Tracking URL with ID: {item_id}")
        print(f"  Product: {product.name}")
        print(f"  Store: {store.name}")
        print(f"  Size: {args.size}{args.unit}")
        if args.lot and args.lot > 1:
            print(f"  Items per lot: {args.lot}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


def cmd_list(args) -> int:
    """List tracked items, products, or stores."""
    db = get_database()
    product_repo = ProductRepository(db)
    store_repo = StoreRepository(db)
    tracked_repo = TrackedItemRepository(db)

    try:
        if args.what == "products":
            products = product_repo.get_all()
            if not products:
                print("No products found.")
                return 0
            print(f"{'ID':<4} {'Name':<30} {'Category':<15} {'Target':<10} {'Stock':<6}")
            print("-" * 70)
            for p in products:
                target = f"{p.target_price:.2f}" if p.target_price else "-"
                cat = p.category or "-"
                print(f"{p.id:<4} {p.name[:30]:<30} {cat[:15]:<15} {target:<10} {p.current_stock:<6}")

        elif args.what == "stores":
            stores = store_repo.get_all()
            if not stores:
                print("No stores found.")
                return 0
            print(f"{'ID':<4} {'Name':<25} {'Shipping':<10} {'Free Above':<12}")
            print("-" * 55)
            for s in stores:
                free = f"{s.free_shipping_threshold:.2f}" if s.free_shipping_threshold else "-"
                print(f"{s.id:<4} {s.name[:25]:<25} {s.shipping_cost_standard:<10.2f} {free:<12}")

        else:  # tracked items (default)
            items = tracked_repo.get_active()
            if not items:
                print("No tracked items found.")
                return 0
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

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


def main():
    """Main entry point with subcommands."""
    parser = argparse.ArgumentParser(
        description="Price Spy - Extract and track product prices using visual AI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command (also default if URL given directly)
    extract_parser = subparsers.add_parser("extract", help="Extract price from URL")
    extract_parser.add_argument("url", help="Product page URL to analyze")
    extract_parser.add_argument("--model", "-m", help="Gemini model to use (e.g., 'gemini-2.5-flash-lite')")

    # Add product command
    product_parser = subparsers.add_parser("add-product", help="Add a new product")
    product_parser.add_argument("name", help="Product name")
    product_parser.add_argument("--category", "-c", help="Product category")
    product_parser.add_argument("--target-price", "-t", type=float, help="Target price for alerts")
    product_parser.add_argument("--unit-size", "-u", help="Preferred unit size (e.g., '250ml')")

    # Add store command
    store_parser = subparsers.add_parser("add-store", help="Add a new store")
    store_parser.add_argument("name", help="Store name")
    store_parser.add_argument("--shipping", "-s", type=float, help="Standard shipping cost")
    store_parser.add_argument("--free-threshold", "-f", type=float, help="Free shipping threshold")

    # Track command
    track_parser = subparsers.add_parser("track", help="Track a URL")
    track_parser.add_argument("url", help="URL to track")
    track_parser.add_argument("--product-id", "-p", type=int, required=True, help="Product ID")
    track_parser.add_argument("--store-id", "-s", type=int, required=True, help="Store ID")
    track_parser.add_argument("--size", type=float, required=True, help="Quantity size (e.g., 250)")
    track_parser.add_argument("--unit", "-u", required=True, help="Unit (e.g., 'ml', 'g', 'L')")
    track_parser.add_argument("--lot", "-l", type=int, help="Items per lot (default: 1)")
    track_parser.add_argument("--model", "-m", help="Preferred Gemini model for this item")

    # List command
    list_parser = subparsers.add_parser("list", help="List items")
    list_parser.add_argument(
        "what",
        nargs="?",
        default="tracked",
        choices=["tracked", "products", "stores"],
        help="What to list (default: tracked)"
    )

    # Check command
    check_parser = subparsers.add_parser("check", help="Test a new URL for compatibility")
    check_parser.add_argument("url", help="URL to test")


    args = parser.parse_args()

    # Handle legacy usage: spy.py <URL> (without subcommand)
    if args.command is None:
        # Check if there's a positional argument that looks like a URL
        if len(sys.argv) > 1 and validate_url(sys.argv[1]):
            args.command = "extract"
            args.url = sys.argv[1]
        else:
            parser.print_help()
            return 1

    # Route to appropriate command
    if args.command == "extract":
        return asyncio.run(cmd_extract(args))
    elif args.command == "add-product":
        return cmd_add_product(args)
    elif args.command == "add-store":
        return cmd_add_store(args)
    elif args.command == "track":
        return cmd_track(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "check":
        return asyncio.run(cmd_check(args))
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
