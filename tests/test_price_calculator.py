from app.core.price_calculator import (
    calculate_volume_price,
    compare_prices,
    determine_effective_availability,
    is_size_available,
    normalize_unit,
)


def test_normalize_unit():
    assert normalize_unit("ML") == "L"
    assert normalize_unit("  kg  ") == "kg"
    assert normalize_unit("stuks") == "stuks"
    assert normalize_unit(None) == ""


def test_calculate_volume_price_basic():
    # 6-pack of 330ml cans at €6.00
    # Total volume: 6 * 330 = 1980ml = 1.98L
    # Price per L: 6.00 / 1.98 = 3.0303...
    price, unit = calculate_volume_price(6.0, 6, 330, "ml")
    assert round(price, 2) == 3.03  # noqa: PLR2004
    assert unit == "L"


def test_calculate_volume_price_kg():
    # 2kg pack for €10.00
    price, unit = calculate_volume_price(10.0, 1, 2, "kg")
    assert price == 5.0  # noqa: PLR2004
    assert unit == "kg"


def test_compare_prices_drop():
    current = 5.0
    previous = 10.0
    comparison = compare_prices(current, previous)
    assert comparison.price_change == -5.0  # noqa: PLR2004
    assert comparison.price_change_percent == -50.0  # noqa: PLR2004
    assert comparison.is_price_drop is True
    assert comparison.is_deal is True


def test_compare_prices_increase():
    current = 12.0
    previous = 10.0
    comparison = compare_prices(current, previous)
    assert comparison.price_change == 2.0  # noqa: PLR2004
    assert comparison.price_change_percent == 20.0  # noqa: PLR2004
    assert comparison.is_price_drop is False


def test_is_size_available():
    available = [" S ", "M", "L"]
    assert is_size_available("s", available) is True
    assert is_size_available("XL", available) is False
    assert is_size_available(None, available) is False


def test_determine_effective_availability_basic():
    # Not sensitive, just returns raw
    assert determine_effective_availability(False, True, None, None) is True
    assert determine_effective_availability(False, False, None, None) is False

    # Sensitive but no sizes extracted, falls back to raw
    assert determine_effective_availability(True, True, None, "M") is True

    # Sensitive, size found
    sizes_json = '["S", "M", "L"]'
    assert determine_effective_availability(True, True, sizes_json, "M") is True

    # Sensitive, size not found
    assert determine_effective_availability(True, True, sizes_json, "XL") is False


def test_compare_prices_no_previous():
    # First check, no previous price
    comparison = compare_prices(10.0, None)
    assert comparison.current_price == 10.0  # noqa: PLR2004
    assert comparison.previous_price is None
    assert comparison.price_change is None
