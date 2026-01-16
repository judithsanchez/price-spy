"""Tests for price calculator module."""

import pytest

from app.core.price_calculator import calculate_volume_price, compare_prices


class TestVolumePrice:
    """Tests for volume price calculation."""

    def test_single_item_liters(self):
        """Single 1L item: price = price/L."""
        volume_price, unit = calculate_volume_price(
            page_price=5.00,
            items_per_lot=1,
            quantity_size=1.0,
            quantity_unit="L"
        )
        assert volume_price == 5.00
        assert unit == "L"

    def test_multipack_calculation(self):
        """6-pack of 330ml cans: €6.00 / 6 / 0.33L = €3.03/L."""
        volume_price, unit = calculate_volume_price(
            page_price=6.00,
            items_per_lot=6,
            quantity_size=330,
            quantity_unit="ml"
        )
        assert round(volume_price, 2) == 3.03
        assert unit == "L"

    def test_ml_converts_to_liters(self):
        """250ml should convert to L for price calculation."""
        volume_price, unit = calculate_volume_price(
            page_price=2.50,
            items_per_lot=1,
            quantity_size=250,
            quantity_unit="ml"
        )
        assert volume_price == 10.00  # 2.50 / 0.25L = 10.00/L
        assert unit == "L"

    def test_grams_convert_to_kg(self):
        """500g should convert to kg for price calculation."""
        volume_price, unit = calculate_volume_price(
            page_price=4.00,
            items_per_lot=1,
            quantity_size=500,
            quantity_unit="g"
        )
        assert volume_price == 8.00  # 4.00 / 0.5kg = 8.00/kg
        assert unit == "kg"

    def test_kg_stays_kg(self):
        """1kg stays as kg."""
        volume_price, unit = calculate_volume_price(
            page_price=10.00,
            items_per_lot=1,
            quantity_size=1.0,
            quantity_unit="kg"
        )
        assert volume_price == 10.00
        assert unit == "kg"

    def test_unit_items(self):
        """Items sold as units (e.g., 'piece', 'stuks')."""
        volume_price, unit = calculate_volume_price(
            page_price=15.00,
            items_per_lot=3,
            quantity_size=1,
            quantity_unit="piece"
        )
        assert volume_price == 5.00  # 15 / 3 = 5.00/piece
        assert unit == "piece"


class TestPriceComparison:
    """Tests for price comparison logic."""

    def test_price_drop_detected(self):
        """Price drop should be flagged."""
        comparison = compare_prices(current=8.99, previous=10.99)

        assert comparison.is_price_drop is True
        assert comparison.price_change == -2.0
        assert round(comparison.price_change_percent, 1) == -18.2

    def test_price_increase_not_flagged(self):
        """Price increase should not be flagged as drop."""
        comparison = compare_prices(current=12.99, previous=10.99)

        assert comparison.is_price_drop is False
        assert comparison.price_change == 2.0
        assert comparison.price_change_percent > 0

    def test_no_previous_price(self):
        """First check has no previous price."""
        comparison = compare_prices(current=10.99, previous=None)

        assert comparison.previous_price is None
        assert comparison.price_change is None
        assert comparison.price_change_percent is None
        assert comparison.is_price_drop is False

    def test_same_price(self):
        """Same price should not be flagged as drop."""
        comparison = compare_prices(current=10.99, previous=10.99)

        assert comparison.is_price_drop is False
        assert comparison.price_change == 0
        assert comparison.price_change_percent == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
