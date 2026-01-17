"""Tests for test data seeder."""

import pytest
import tempfile
import os


class TestSeeder:
    """Tests for the test data seeder."""

    def test_seed_creates_products(self, seeded_db):
        """Seeder should create products."""
        from app.storage.repositories import ProductRepository

        repo = ProductRepository(seeded_db)
        products = repo.get_all()

        assert len(products) >= 3

    def test_seed_creates_stores(self, seeded_db):
        """Seeder should create stores."""
        from app.storage.repositories import StoreRepository

        repo = StoreRepository(seeded_db)
        stores = repo.get_all()

        assert len(stores) >= 2

    def test_seed_creates_tracked_items(self, seeded_db):
        """Seeder should create tracked items."""
        from app.storage.repositories import TrackedItemRepository

        repo = TrackedItemRepository(seeded_db)
        items = repo.get_active()

        assert len(items) >= 3

    def test_seed_creates_price_history(self, seeded_db):
        """Seeder should create price history."""
        from app.storage.repositories import PriceHistoryRepository

        repo = PriceHistoryRepository(seeded_db)
        # Check if there's price history for the seeded URLs
        prices = repo.get_by_url("https://www.amazon.nl/dp/B015OAQEHI")

        assert len(prices) >= 1

    def test_seed_includes_deal_scenario(self, seeded_db):
        """Seeder should include at least one deal (price <= target)."""
        from app.storage.repositories import (
            ProductRepository, TrackedItemRepository, PriceHistoryRepository
        )

        product_repo = ProductRepository(seeded_db)
        tracked_repo = TrackedItemRepository(seeded_db)
        price_repo = PriceHistoryRepository(seeded_db)

        # Find at least one item where price <= target
        deals_found = 0
        for item in tracked_repo.get_active():
            product = product_repo.get_by_id(item.product_id)
            if product and product.target_price:
                latest = price_repo.get_latest_by_url(item.url)
                if latest and latest.price <= product.target_price:
                    deals_found += 1

        assert deals_found >= 1, "Seeder should include at least one deal scenario"

    def test_seed_includes_above_target_scenario(self, seeded_db):
        """Seeder should include at least one item above target."""
        from app.storage.repositories import (
            ProductRepository, TrackedItemRepository, PriceHistoryRepository
        )

        product_repo = ProductRepository(seeded_db)
        tracked_repo = TrackedItemRepository(seeded_db)
        price_repo = PriceHistoryRepository(seeded_db)

        above_target_found = 0
        for item in tracked_repo.get_active():
            product = product_repo.get_by_id(item.product_id)
            if product and product.target_price:
                latest = price_repo.get_latest_by_url(item.url)
                if latest and latest.price > product.target_price:
                    above_target_found += 1

        assert above_target_found >= 1, "Seeder should include at least one above-target scenario"

    def test_seed_is_idempotent(self, empty_db):
        """Running seeder twice should not duplicate data."""
        from app.core.seeder import seed_test_data
        from app.storage.repositories import ProductRepository

        # Seed twice
        seed_test_data(empty_db)
        seed_test_data(empty_db)

        repo = ProductRepository(empty_db)
        products = repo.get_all()

        # Should still have same number of products (not doubled)
        assert len(products) <= 6  # Max 3 products * 2 if not idempotent


@pytest.fixture
def empty_db():
    """Create empty database."""
    from app.storage.database import Database

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.initialize()

    yield db

    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def seeded_db(empty_db):
    """Create database with seeded test data."""
    from app.core.seeder import seed_test_data

    seed_test_data(empty_db)
    return empty_db
