from app.models.schemas import Category, Label, Product, TrackedItem
from app.storage.database import Database
from app.storage.repositories import (
    CategoryRepository,
    LabelRepository,
    ProductRepository,
    PurchaseTypeRepository,
    TrackedItemRepository,
    UnitRepository,
)


def test_metadata_repositories(test_db):
    db = Database(test_db)
    db.initialize()  # Ensure tables exist and seeding happens

    # Test Units (Seeded)
    unit_repo = UnitRepository(db)
    # Don't insert seeded ones, or use INSERT OR IGNORE (repo.insert might not use it)
    # Let's just verify seeded ones exist
    units = unit_repo.get_all()
    assert any(u.name == "kg" for u in units)  # 'kg' is seeded

    # Test Purchase Types (Seeded)
    pt_repo = PurchaseTypeRepository(db)
    types = pt_repo.get_all()
    assert any(t.name == "recurring" for t in types)

    # Test Categories (Seeded + Custom)
    cat_repo = CategoryRepository(db)
    custom_cat = "TestUniqueCategory"
    cat_repo.insert(Category(name=custom_cat, is_size_sensitive=True))
    cats = cat_repo.get_all()
    assert any(c.name == custom_cat for c in cats)
    assert any(c.name == "Electronics" for c in cats)  # Verify seeded also there

    # Test Labels (Seeded + Custom)
    label_repo = LabelRepository(db)
    custom_label = "TestUniqueLabel"
    label_id = label_repo.insert(Label(name=custom_label))
    labels = label_repo.get_all()
    assert any(label.name == custom_label for label in labels)
    assert any(label.name == "Eco-friendly" for label in labels)  # Verify seeded
    found_label = label_repo.get_by_id(label_id)
    assert found_label is not None
    assert found_label.name == custom_label


def test_product_repository(test_db):
    db = Database(test_db)
    db.initialize()
    repo = ProductRepository(db)

    # Test insert and get_by_id
    prod = Product(
        name="Test Shirt",
        category="Clothing",
        purchase_type="one_time",
        target_price=25.0,
        target_unit="item",
    )
    prod_id = repo.insert(prod)
    found = repo.get_by_id(prod_id)
    assert found is not None
    assert found.name == "Test Shirt"
    assert found.target_price == 25.0  # noqa: PLR2004

    # Test search
    results = repo.search("Shirt")
    assert len(results) >= 1
    assert results[0].name == "Test Shirt"

    # Test update
    found.target_price = 20.0
    repo.update(prod_id, found)
    updated = repo.get_by_id(prod_id)
    assert updated is not None
    assert updated.target_price == 20.0  # noqa: PLR2004

    # Test delete
    repo.delete(prod_id)
    assert repo.get_by_id(prod_id) is None


def test_tracked_item_repository(test_db):
    db = Database(test_db)
    db.initialize()
    repo = TrackedItemRepository(db)

    # Test insert and get_by_id
    item = TrackedItem(
        product_id=1,
        store_id=1,
        url="https://example.com/item",
        quantity_size=1.0,
        quantity_unit="item",
    )
    item_id = repo.insert(item)
    found = repo.get_by_id(item_id)
    assert found is not None
    assert found.url == "https://example.com/item"

    # Test set/get labels
    label_repo = LabelRepository(db)
    l1 = label_repo.insert(Label(name="L1"))
    l2 = label_repo.insert(Label(name="L2"))

    repo.set_labels(item_id, [l1, l2])
    labels = repo.get_labels(item_id)
    assert len(labels) == 2  # noqa: PLR2004
    assert any(label.name == "L1" for label in labels)

    # Test get_due_for_check
    due = repo.get_due_for_check()
    assert any(i.id == item_id for i in due)

    # Test set_last_checked
    repo.set_last_checked(item_id)
    updated = repo.get_by_id(item_id)
    assert updated is not None
    assert updated.last_checked_at is not None
