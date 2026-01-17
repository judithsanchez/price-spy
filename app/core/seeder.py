"""Test data seeder for Price Spy."""

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

    # Create price history
    # Product 1: Price BELOW target (DEAL) - 12.99 < 15.00
    price1 = PriceHistoryRecord(
        product_name="Eucerin UreaRepair PLUS 5% Urea Body Lotion",
        price=12.99,
        currency="EUR",
        confidence=1.0,
        url="https://www.amazon.nl/dp/B015OAQEHI",
        store_name="Amazon.nl"
    )
    price_repo.insert(price1)

    # Product 2: Price ABOVE target - 6.49 > 5.00
    price2 = PriceHistoryRecord(
        product_name="Coca-Cola Original 6x330ml",
        price=6.49,
        currency="EUR",
        confidence=1.0,
        url="https://www.bol.com/nl/p/coca-cola-6pack",
        store_name="Bol.com"
    )
    price_repo.insert(price2)

    # Product 3: Has price but no target
    price3 = PriceHistoryRecord(
        product_name="Kitchen Gadget Pro 3000",
        price=29.99,
        currency="EUR",
        confidence=1.0,
        url="https://www.amazon.nl/dp/BXXXXXXX",
        store_name="Amazon.nl"
    )
    price_repo.insert(price3)

    return {
        "status": "success",
        "products_created": 3,
        "stores_created": 2,
        "tracked_items_created": 3,
        "price_records_created": 3,
        "deals": 1,
        "above_target": 1,
        "no_target": 1
    }
