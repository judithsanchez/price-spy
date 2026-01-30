from fastapi.testclient import TestClient

from app.api import deps
from app.models.schemas import PriceHistoryRecord, Product, Store, TrackedItem
from app.storage.database import Database
from app.storage.repositories import (
    PriceHistoryRepository,
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
)

HTTP_OK = 200


def test_dashboard_unbound_local_error(client: TestClient):
    # Setup: Create a scenario where is_target_hit is not calculated

    # We need to access the DB used by the client.
    # Since client uses the overridden test db path, we can connect to it.
    db_path = deps.DatabaseConfig.get_path()
    assert db_path == deps.settings.DATABASE_PATH or db_path.endswith(".db")
    db = Database(db_path)
    db.initialize()

    try:
        # 1. Product with target price and unit
        product_repo = ProductRepository(db)
        p_id = product_repo.insert(
            Product(
                name="Buggy Product",
                category="Test",
                target_price=10.0,
                target_unit="kg",
            )
        )

        # 2. Store
        store_repo = StoreRepository(db)
        s_id = store_repo.insert(Store(name="Test Store"))

        # 3. Tracked Item with DIFFERENT unit (e.g. L vs kg)
        # This ensures 'normalized_target_unit != normalized_current_unit'
        tracked_repo = TrackedItemRepository(db)
        tracked_repo.insert(
            TrackedItem(
                product_id=p_id,
                store_id=s_id,
                url="http://example.com/bug",
                quantity_size=1.0,
                quantity_unit="L",  # Mismatch with kg
                items_per_lot=1,
                is_active=True,
            )
        )

        # 4. Price History (Latest)
        price_repo = PriceHistoryRepository(db)
        price_repo.insert(
            PriceHistoryRecord(
                product_name="Buggy Product",
                price=12.0,
                currency="EUR",
                is_available=True,
                url="http://example.com/bug",
                store_name="Test Store",
                confidence=1.0,
            )
        )

        # Act: Load Dashboard
        response = client.get("/")

        # Assert: Expect 500 (Fail) initially, then 200 (Pass) after fix
        assert response.status_code == HTTP_OK

    finally:
        db.close()
