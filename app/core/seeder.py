"""Test data seeder for Price Spy."""

from datetime import datetime, timedelta
from app.storage.database import Database
from app.storage.repositories import (
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
    PriceHistoryRepository,
)
from app.models.schemas import Product, Store, TrackedItem, PriceHistoryRecord


def seed_test_data(db: Database) -> dict:
    """
    Seed the database with test data for UI testing.

    Creates:
    - 3 products with varying target prices
    - 2 stores
    - 3 tracked items
    - Price history including deal and non-deal scenarios

    Returns:
        Summary of created data
    """
    product_repo = ProductRepository(db)
    store_repo = StoreRepository(db)
    tracked_repo = TrackedItemRepository(db)
    price_repo = PriceHistoryRepository(db)

    # Check if data already exists (idempotency)
    existing_products = product_repo.get_all()
    if any(p.name.startswith("Test:") for p in existing_products):
        return {"status": "skipped", "reason": "Test data already exists"}

    # Create stores
    store1 = Store(name="Test: Amazon.nl", shipping_cost_standard=3.99, free_shipping_threshold=25.00)
    store1_id = store_repo.insert(store1)

    store2 = Store(name="Test: Bol.com", shipping_cost_standard=0, notes="Free shipping on all orders")
    store2_id = store_repo.insert(store2)

    # Create products with different scenarios
    # Product 1: Will be a DEAL (price below target)
    product1 = Product(
        name="Test: Eucerin Urea Lotion 250ml",
        category="Skincare",
        purchase_type="recurring",
        target_price=15.00,
        preferred_unit_size="250ml"
    )
    product1_id = product_repo.insert(product1)

    # Product 2: Above target price
    product2 = Product(
        name="Test: Coca-Cola 6-pack 330ml",
        category="Beverages",
        purchase_type="recurring",
        target_price=5.00,
        preferred_unit_size="6x330ml"
    )
    product2_id = product_repo.insert(product2)

    # Product 3: No target price set
    product3 = Product(
        name="Test: Random Kitchen Gadget",
        category="Home",
        purchase_type="one_time",
        target_price=None
    )
    product3_id = product_repo.insert(product3)

    # Create tracked items
    tracked1 = TrackedItem(
        product_id=product1_id,
        store_id=store1_id,
        url="https://www.amazon.nl/dp/B015OAQEHI",
        item_name_on_site="Eucerin UreaRepair PLUS 5% Urea Body Lotion",
        quantity_size=250,
        quantity_unit="ml",
        items_per_lot=1,
        is_active=True
    )
    tracked1_id = tracked_repo.insert(tracked1)

    tracked2 = TrackedItem(
        product_id=product2_id,
        store_id=store2_id,
        url="https://www.bol.com/nl/p/coca-cola-6pack",
        item_name_on_site="Coca-Cola Original 6x330ml",
        quantity_size=330,
        quantity_unit="ml",
        items_per_lot=6,
        is_active=True
    )
    tracked2_id = tracked_repo.insert(tracked2)

    tracked3 = TrackedItem(
        product_id=product3_id,
        store_id=store1_id,
        url="https://www.amazon.nl/dp/BXXXXXXX",
        item_name_on_site="Kitchen Gadget Pro 3000",
        quantity_size=1,
        quantity_unit="piece",
        items_per_lot=1,
        is_active=True
    )
    tracked3_id = tracked_repo.insert(tracked3)

    # Create price history with multiple data points for graphs
    now = datetime.now()
    price_count = 0

    # Product 1: Eucerin - Price dropping over time (DEAL scenario)
    # Started at 18.99, dropped to 12.99 (below target of 15.00)
    eucerin_prices = [
        (18.99, 30),  # 30 days ago
        (17.49, 25),  # 25 days ago
        (17.49, 20),  # 20 days ago
        (16.99, 15),  # 15 days ago
        (15.99, 10),  # 10 days ago
        (14.49, 7),   # 7 days ago
        (13.99, 4),   # 4 days ago
        (12.99, 1),   # 1 day ago (current - DEAL!)
    ]
    for price, days_ago in eucerin_prices:
        record = PriceHistoryRecord(
            product_name="Eucerin UreaRepair PLUS 5% Urea Body Lotion",
            price=price,
            currency="EUR",
            confidence=1.0,
            url="https://www.amazon.nl/dp/B015OAQEHI",
            store_name="Amazon.nl"
        )
        # Insert with custom date
        db.execute(
            """INSERT INTO price_history
               (product_name, price, currency, confidence, url, store_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (record.product_name, record.price, record.currency, record.confidence,
             record.url, record.store_name, (now - timedelta(days=days_ago)).isoformat())
        )
        price_count += 1

    # Product 2: Coca-Cola - Price fluctuating (above target)
    # Target is 5.00, prices hover around 6-7
    cola_prices = [
        (6.99, 28),
        (6.49, 21),
        (7.29, 14),  # Price spike
        (6.99, 10),
        (6.49, 7),
        (6.49, 3),
        (6.49, 0),   # Current
    ]
    for price, days_ago in cola_prices:
        record = PriceHistoryRecord(
            product_name="Coca-Cola Original 6x330ml",
            price=price,
            currency="EUR",
            confidence=1.0,
            url="https://www.bol.com/nl/p/coca-cola-6pack",
            store_name="Bol.com"
        )
        db.execute(
            """INSERT INTO price_history
               (product_name, price, currency, confidence, url, store_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (record.product_name, record.price, record.currency, record.confidence,
             record.url, record.store_name, (now - timedelta(days=days_ago)).isoformat())
        )
        price_count += 1

    # Product 3: Kitchen Gadget - Stable price (no target)
    gadget_prices = [
        (34.99, 21),
        (34.99, 14),
        (29.99, 7),   # Price drop
        (29.99, 2),
        (29.99, 0),   # Current
    ]
    for price, days_ago in gadget_prices:
        record = PriceHistoryRecord(
            product_name="Kitchen Gadget Pro 3000",
            price=price,
            currency="EUR",
            confidence=1.0,
            url="https://www.amazon.nl/dp/BXXXXXXX",
            store_name="Amazon.nl"
        )
        db.execute(
            """INSERT INTO price_history
               (product_name, price, currency, confidence, url, store_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (record.product_name, record.price, record.currency, record.confidence,
             record.url, record.store_name, (now - timedelta(days=days_ago)).isoformat())
        )
        price_count += 1

    db.commit()

    return {
        "status": "success",
        "products_created": 3,
        "stores_created": 2,
        "tracked_items_created": 3,
        "price_records_created": price_count,
        "deals": 1,
        "above_target": 1,
        "no_target": 1
    }
