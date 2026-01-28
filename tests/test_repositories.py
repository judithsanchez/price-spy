from app.storage.database import Database
from app.storage.repositories import (
    UnitRepository,
    PurchaseTypeRepository,
    CategoryRepository,
    LabelRepository,
)
from app.models.schemas import Category, Label


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
    assert label_repo.get_by_id(label_id).name == custom_label
