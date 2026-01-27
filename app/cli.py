"""CLI commands for Price Spy."""

import argparse
import asyncio
import sys

from app.storage.database import Database


def seed_test_data_command(db_path: str = "data/pricespy.db"):
    """Seed the database with test data."""
    from app.core.seeder import seed_test_data

    db = Database(db_path)
    db.initialize()

    try:
        result = seed_test_data(db)
        if result["status"] == "skipped":
            print(f"Skipped: {result['reason']}")
        else:
            print("Test data seeded successfully:")
            print(f"  - Products: {result['products_created']}")
            print(f"  - Stores: {result['stores_created']}")
            print(f"  - Tracked Items: {result['tracked_items_created']}")
            print(f"  - Price Records: {result['price_records_created']}")
            print(f"  - Deals (price <= target): {result['deals']}")
            print(f"  - Above target: {result['above_target']}")
    finally:
        db.close()


def extract_all_command(db_path: str = "data/pricespy.db", delay: float = 5.0):
    """Extract prices for all active tracked items."""
    from app.core.batch_extraction import extract_all_items, get_batch_summary

    db = Database(db_path)
    db.initialize()

    try:
        print(f"Starting batch extraction (delay: {delay}s between items)...")
        results = asyncio.run(extract_all_items(db, delay_seconds=delay))
        summary = get_batch_summary(results)

        print("\nBatch extraction complete:")
        print(f"  - Total items: {summary['total']}")
        print(f"  - Successful: {summary['success_count']}")
        print(f"  - Errors: {summary['error_count']}")

        if summary['error_count'] > 0:
            print("\nErrors:")
            for r in summary['results']:
                if r.get('status') == 'error':
                    print(f"  - Item {r['item_id']}: {r.get('error', 'Unknown error')}")
    finally:
        db.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Price Spy CLI",
        prog="python -m app.cli"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # seed-test-data command
    seed_parser = subparsers.add_parser(
        "seed-test-data",
        help="Seed database with test data for UI testing"
    )
    seed_parser.add_argument(
        "--db-path",
        default="data/pricespy.db",
        help="Path to database file (default: data/pricespy.db)"
    )

    # extract-all command
    extract_parser = subparsers.add_parser(
        "extract-all",
        help="Extract prices for all active tracked items"
    )
    extract_parser.add_argument(
        "--db-path",
        default="data/pricespy.db",
        help="Path to database file (default: data/pricespy.db)"
    )
    extract_parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Delay between extractions in seconds (default: 5.0)"
    )

    args = parser.parse_args()

    if args.command == "seed-test-data":
        seed_test_data_command(args.db_path)
    elif args.command == "extract-all":
        extract_all_command(args.db_path, args.delay)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
