"""Tests for price drop alerts UI."""

import pytest
from fastapi.testclient import TestClient
import tempfile
import os


class TestDealBadge:
    """Tests for DEAL badge on dashboard."""

    def test_dashboard_shows_deal_badge_when_price_at_target(self, client_with_deal):
        """Dashboard should show DEAL badge when price equals target."""
        response = client_with_deal.get("/")
        assert response.status_code == 200
        assert "DEAL" in response.text

    def test_dashboard_shows_deal_badge_when_price_below_target(self, client_with_deal_below):
        """Dashboard should show DEAL badge when price is below target."""
        response = client_with_deal_below.get("/")
        assert response.status_code == 200
        assert "DEAL" in response.text

    def test_dashboard_no_deal_badge_when_price_above_target(self, client_with_price_above):
        """Dashboard should NOT show DEAL badge when price is above target."""
        response = client_with_price_above.get("/")
        assert response.status_code == 200
        assert "DEAL" not in response.text

    def test_dashboard_no_deal_badge_when_no_target(self, client_with_no_target):
        """Dashboard should NOT show DEAL badge when no target price set."""
        response = client_with_no_target.get("/")
        assert response.status_code == 200
        assert "DEAL" not in response.text

    def test_deal_badge_has_green_styling(self, client_with_deal):
        """DEAL badge should have green styling."""
        response = client_with_deal.get("/")
        # Check for green background or text color near DEAL
        assert "bg-green" in response.text or "text-green" in response.text


class TestDealAlert:
    """Tests for deal alert banner at top of dashboard."""

    def test_dashboard_shows_deal_alert_banner(self, client_with_deal):
        """Dashboard should show alert banner when there's a deal."""
        response = client_with_deal.get("/")
        assert response.status_code == 200
        # Check for alert banner class or deal alert text
        assert "deal-alert" in response.text.lower() or "target price" in response.text.lower()


@pytest.fixture
def client_with_deal():
    """Create test client with item at exactly target price."""
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import (
        ProductRepository, StoreRepository, TrackedItemRepository, PriceHistoryRepository
    )
    from app.models.schemas import Product, Store, TrackedItem, PriceHistoryRecord
    import app.api.main as main_module

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        # Create product with target price 15.00
        product = Product(name="Deal Product", category="Test", target_price=15.00)
        product_id = product_repo.insert(product)

        store = Store(name="Deal Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/deal",
            quantity_size=100,
            quantity_unit="ml"
        )
        tracked_repo.insert(tracked)

        # Add price exactly at target (15.00 == 15.00)
        price_record = PriceHistoryRecord(
            product_name="Deal Product",
            price=15.00,
            currency="EUR",
            confidence=1.0,
            url="https://example.com/deal"
        )
        price_repo.insert(price_record)

        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def client_with_deal_below():
    """Create test client with item priced below target (a deal)."""
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import (
        ProductRepository, StoreRepository, TrackedItemRepository, PriceHistoryRepository
    )
    from app.models.schemas import Product, Store, TrackedItem, PriceHistoryRecord
    import app.api.main as main_module

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        product = Product(name="Below Target Deal", category="Test", target_price=20.00)
        product_id = product_repo.insert(product)

        store = Store(name="Deal Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/below-deal",
            quantity_size=100,
            quantity_unit="ml"
        )
        tracked_repo.insert(tracked)

        # Add price below target (12.00 < 20.00)
        price_record = PriceHistoryRecord(
            product_name="Below Target Deal",
            price=12.00,
            currency="EUR",
            confidence=1.0,
            url="https://example.com/below-deal"
        )
        price_repo.insert(price_record)

        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def client_with_price_above():
    """Create test client with item priced above target (no deal)."""
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import (
        ProductRepository, StoreRepository, TrackedItemRepository, PriceHistoryRepository
    )
    from app.models.schemas import Product, Store, TrackedItem, PriceHistoryRecord
    import app.api.main as main_module

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        product = Product(name="Above Target Product", category="Test", target_price=10.00)
        product_id = product_repo.insert(product)

        store = Store(name="Test Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/above",
            quantity_size=100,
            quantity_unit="ml"
        )
        tracked_repo.insert(tracked)

        # Add price above target (15.00 > 10.00)
        price_record = PriceHistoryRecord(
            product_name="Above Target Product",
            price=15.00,
            currency="EUR",
            confidence=1.0,
            url="https://example.com/above"
        )
        price_repo.insert(price_record)

        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def client_with_no_target():
    """Create test client with item that has no target price."""
    from app.api.main import app
    from app.storage.database import Database
    from app.storage.repositories import (
        ProductRepository, StoreRepository, TrackedItemRepository, PriceHistoryRepository
    )
    from app.models.schemas import Product, Store, TrackedItem, PriceHistoryRecord
    import app.api.main as main_module

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()

        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        # Product with NO target price
        product = Product(name="No Target Product", category="Test", target_price=None)
        product_id = product_repo.insert(product)

        store = Store(name="Test Store", shipping_cost_standard=0)
        store_id = store_repo.insert(store)

        tracked = TrackedItem(
            product_id=product_id,
            store_id=store_id,
            url="https://example.com/no-target",
            quantity_size=100,
            quantity_unit="ml"
        )
        tracked_repo.insert(tracked)

        price_record = PriceHistoryRecord(
            product_name="No Target Product",
            price=10.00,
            currency="EUR",
            confidence=1.0,
            url="https://example.com/no-target"
        )
        price_repo.insert(price_record)

        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
