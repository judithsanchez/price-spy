from app.models.schemas import Product, Store, TrackedItem

def test_product_schema():
    p = Product(name="Test", category="Cat", target_price=10.0)
    assert p.name == "Test"
    assert p.target_price == 10.0

def test_store_schema():
    s = Store(name="Store", base_url="https://store.com")
    assert s.name == "Store"

def test_tracked_item_schema():
    # quantity_unit and items_per_lot/quantity_size might be required
    ti = TrackedItem(
        product_id=1, 
        store_id=1, 
        url="http://test.com",
        quantity_unit="ml",
        items_per_lot=1,
        quantity_size=1.0
    )
    assert ti.product_id == 1
    assert ti.quantity_unit == "ml"
