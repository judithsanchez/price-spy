"""Test data seeder for Price Spy."""

import random
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
    - 20+ products with varying target prices
    - 5 stores
    - 20+ tracked items
    - Price history with various patterns

    Returns:
        Summary of created data
    """
    product_repo = ProductRepository(db)
    store_repo = StoreRepository(db)
    tracked_repo = TrackedItemRepository(db)

    # Check if data already exists (idempotency)
    existing_products = product_repo.get_all()
    if any(p.name.startswith("Test:") for p in existing_products):
        return {"status": "skipped", "reason": "Test data already exists"}

    # Create stores
    stores = [
        Store(name="Test: Amazon.nl", shipping_cost_standard=3.99, free_shipping_threshold=25.00),
        Store(name="Test: Bol.com", shipping_cost_standard=0, notes="Free shipping on all orders"),
        Store(name="Test: Coolblue", shipping_cost_standard=0, notes="Free shipping always"),
        Store(name="Test: MediaMarkt", shipping_cost_standard=4.99, free_shipping_threshold=50.00),
        Store(name="Test: Kruidvat", shipping_cost_standard=2.99, free_shipping_threshold=20.00),
        Store(name="Test: Etos", shipping_cost_standard=0, free_shipping_threshold=20.00, notes="Free shipping above 20 EUR"),
    ]
    store_ids = [store_repo.insert(s) for s in stores]

    # Define products with their price patterns
    # Pattern types: "dropping", "rising", "stable", "volatile", "spike", "dip"
    products_config = [
        # Skincare
        ("Test: Eucerin Urea Lotion 250ml", "Skincare", 15.00, "250ml", 0, "dropping", 18.99, 12.99),
        ("Test: CeraVe Moisturizing Cream", "Skincare", 12.00, "454g", 0, "stable", 14.99, 14.49),
        ("Test: La Roche-Posay Effaclar", "Skincare", 20.00, "200ml", 1, "volatile", 22.99, 19.99),
        ("Test: Nivea Body Lotion 400ml", "Skincare", 5.00, "400ml", 4, "dropping", 6.99, 4.49),

        # Beverages
        ("Test: Coca-Cola 6-pack 330ml", "Beverages", 5.00, "6x330ml", 1, "rising", 5.49, 6.99),
        ("Test: Red Bull 12-pack", "Beverages", 15.00, "12x250ml", 0, "spike", 16.99, 18.99),
        ("Test: Heineken 24-pack", "Beverages", 18.00, "24x330ml", 1, "dip", 22.99, 17.99),
        ("Test: Nespresso Capsules 50pk", "Beverages", 25.00, "50 caps", 0, "stable", 27.99, 27.49),

        # Electronics
        ("Test: Apple AirPods Pro", "Electronics", 220.00, "1 pair", 0, "dropping", 279.00, 229.00),
        ("Test: Samsung Galaxy Buds", "Electronics", 100.00, "1 pair", 2, "volatile", 149.00, 119.00),
        ("Test: Logitech MX Master 3", "Electronics", 80.00, "1 unit", 0, "stable", 99.99, 94.99),
        ("Test: Anker PowerBank 20000mAh", "Electronics", 35.00, "1 unit", 3, "dropping", 49.99, 34.99),

        # Home & Kitchen
        ("Test: Philips Airfryer XL", "Home", 150.00, "1 unit", 2, "dip", 199.00, 159.00),
        ("Test: Nespresso Machine", "Home", 100.00, "1 unit", 0, "dropping", 149.00, 99.00),
        ("Test: KitchenAid Mixer", "Home", 400.00, "1 unit", 0, "stable", 549.00, 529.00),
        ("Test: Dyson V15 Vacuum", "Home", 550.00, "1 unit", 0, "spike", 599.00, 649.00),

        # Health & Supplements
        ("Test: Vitamin D3 180 caps", "Health", 15.00, "180 caps", 4, "dropping", 19.99, 12.99),
        ("Test: Omega-3 Fish Oil", "Health", 20.00, "120 caps", 1, "stable", 24.99, 23.99),
        ("Test: Whey Protein 2kg", "Health", 45.00, "2kg", 1, "volatile", 54.99, 49.99),
        ("Test: Creatine Monohydrate", "Health", 25.00, "500g", 0, "rising", 22.99, 27.99),

        # Baby & Kids
        ("Test: Pampers Size 4 (150pk)", "Baby", 35.00, "150 diapers", 1, "dropping", 44.99, 32.99),
        ("Test: Aptamil Formula 800g", "Baby", 18.00, "800g", 0, "stable", 21.99, 21.49),

        # Pet Supplies
        ("Test: Royal Canin Dog Food 12kg", "Pet", 55.00, "12kg", 0, "volatile", 64.99, 58.99),
        ("Test: Whiskas Cat Food 7kg", "Pet", 30.00, "7kg", 1, "dropping", 38.99, 28.99),

        # Etos Specials (Store index 5)
        ("Test: Andrélon Pink Droogshampoo", "Hair", 3.50, "250ml", 5, "stable", 6.99, 6.99),
        ("Test: Etos Vitamin C 1000mg", "Health", 5.00, "60 tab", 5, "dip", 8.99, 5.99),
    ]

    now = datetime.now()
    products_created = 0
    tracked_created = 0
    price_count = 0

    for name, category, target, size, store_idx, pattern, start_price, end_price in products_config:
        # Create product
        product = Product(
            name=name,
            category=category,
            purchase_type="recurring" if category in ["Skincare", "Beverages", "Health", "Baby", "Pet"] else "one_time",
            target_price=target,
            preferred_unit_size=size
        )
        product_id = product_repo.insert(product)
        products_created += 1

        # Create tracked item
        url_slug = name.lower().replace("test: ", "").replace(" ", "-").replace("(", "").replace(")", "")
        store_name = stores[store_idx].name.replace("Test: ", "")

        # Parse quantity from size string (e.g., "250ml", "6x330ml", "1 unit", "2kg")
        qty_size, qty_unit = _parse_quantity(size)

        # Prepare domain
        domain = store_name.lower().replace(' ', '')
        if not (domain.endswith('.nl') or domain.endswith('.com')):
            domain += '.nl'
            
        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_ids[store_idx],
            url=f"https://www.{domain}/p/{url_slug}",
            item_name_on_site=name.replace("Test: ", ""),
            quantity_size=qty_size,
            quantity_unit=qty_unit,
            items_per_lot=1,
            is_active=True
        )
        tracked_id = tracked_repo.insert(tracked)
        tracked_created += 1

        # Generate price history based on pattern
        prices = _generate_price_history(pattern, start_price, end_price, days=60)

        for price, days_ago in prices:
            db.execute(
                """INSERT INTO price_history
                   (item_id, product_name, price, currency, confidence, url, store_name, created_at,
                    original_price, deal_type, deal_description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    tracked_id, 
                    name.replace("Test: ", ""), 
                    price, 
                    "EUR", 
                    1.0,
                    tracked.url, 
                    store_name, 
                    (now - timedelta(days=days_ago)).isoformat(),
                    start_price if price < start_price else None,
                    "bogo" if "Andrélon" in name and days_ago == 0 else ("discount" if price < start_price else "none"),
                    "1+1 gratis" if "Andrélon" in name and days_ago == 0 else ("Special offer" if price < start_price else None)
                )
            )
            price_count += 1

    db.commit()

    return {
        "status": "success",
        "products_created": products_created,
        "stores_created": len(stores),
        "tracked_items_created": tracked_created,
        "price_records_created": price_count,
    }


def _parse_quantity(size: str) -> tuple:
    """Parse quantity size and unit from a string like '250ml', '6x330ml', '2kg', '1 unit'."""
    import re

    # Handle formats like "6x330ml" -> (330, "ml")
    if "x" in size.lower():
        parts = size.lower().split("x")
        if len(parts) == 2:
            match = re.match(r'(\d+\.?\d*)\s*(\w+)', parts[1])
            if match:
                return float(match.group(1)), match.group(2)

    # Handle formats like "250ml", "2kg", "454g"
    match = re.match(r'(\d+\.?\d*)\s*(\w+)', size)
    if match:
        return float(match.group(1)), match.group(2)

    # Handle formats like "1 unit", "180 caps"
    parts = size.split()
    if len(parts) >= 2 and parts[0].replace(".", "").isdigit():
        return float(parts[0]), parts[-1]

    return 1.0, "unit"


def _generate_price_history(pattern: str, start_price: float, end_price: float, days: int = 60) -> list:
    """Generate price history data points based on pattern type."""
    prices = []
    num_points = random.randint(8, 15)

    # Generate day intervals
    day_intervals = sorted(random.sample(range(1, days), num_points - 1)) + [0]
    day_intervals = [days] + day_intervals
    day_intervals.sort(reverse=True)

    if pattern == "dropping":
        # Gradual decrease with occasional plateaus
        for i, day in enumerate(day_intervals):
            progress = i / (len(day_intervals) - 1)
            price = start_price - (start_price - end_price) * progress
            price += random.uniform(-0.5, 0.5)  # Small noise
            prices.append((round(max(end_price * 0.95, price), 2), day))

    elif pattern == "rising":
        # Gradual increase
        for i, day in enumerate(day_intervals):
            progress = i / (len(day_intervals) - 1)
            price = start_price + (end_price - start_price) * progress
            price += random.uniform(-0.5, 0.5)
            prices.append((round(price, 2), day))

    elif pattern == "stable":
        # Mostly flat with tiny variations
        avg_price = (start_price + end_price) / 2
        for day in day_intervals:
            price = avg_price + random.uniform(-1, 1)
            prices.append((round(price, 2), day))

    elif pattern == "volatile":
        # Up and down swings
        for i, day in enumerate(day_intervals):
            swing = random.choice([-1, 1]) * random.uniform(2, 5)
            base = (start_price + end_price) / 2
            price = base + swing
            prices.append((round(price, 2), day))
        # Ensure end price is close to target
        prices[-1] = (end_price, 0)

    elif pattern == "spike":
        # Normal then sudden spike
        spike_point = len(day_intervals) // 2
        for i, day in enumerate(day_intervals):
            if i < spike_point:
                price = start_price + random.uniform(-1, 1)
            else:
                progress = (i - spike_point) / (len(day_intervals) - spike_point - 1)
                price = start_price + (end_price - start_price) * progress
            prices.append((round(price, 2), day))

    elif pattern == "dip":
        # Normal, dip down, then recover
        dip_start = len(day_intervals) // 3
        dip_end = 2 * len(day_intervals) // 3
        dip_price = min(start_price, end_price) * 0.85

        for i, day in enumerate(day_intervals):
            if i < dip_start:
                price = start_price + random.uniform(-1, 1)
            elif i < dip_end:
                price = dip_price + random.uniform(-1, 1)
            else:
                price = end_price + random.uniform(-1, 1)
            prices.append((round(price, 2), day))

    return prices
