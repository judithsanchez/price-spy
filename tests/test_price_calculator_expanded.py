from app.core.price_calculator import (
    normalize_unit,
    calculate_volume_price,
    compare_prices,
    is_size_available,
    determine_effective_availability,
)


def test_normalize_unit_edge_cases():
    assert normalize_unit("") == ""
    assert normalize_unit(None) == ""
    assert normalize_unit("kg") == "kg"
    assert normalize_unit("UNKNOWN") == "unknown"


def test_calculate_volume_price_unknown_unit():
    # Unknown unit should use factor 1
    price, unit = calculate_volume_price(10.0, 1, 10.0, "pieces")
    assert price == 1.0
    assert unit == "pieces"


def test_compare_prices_no_deal():
    comp = compare_prices(10.0, 10.0, original_price=None, deal_type="None")
    assert comp.is_deal is False
    assert comp.price_change == 0.0


def test_is_size_available_edge_cases():
    assert is_size_available("", ["m"]) is False
    assert is_size_available("s", []) is False


def test_determine_effective_availability_scenarios():
    # Raw unavailable
    assert determine_effective_availability(True, False, None, "M") is False
    # Not size sensitive
    assert determine_effective_availability(False, True, None, "M") is True
    # Sensitive but missing data
    assert determine_effective_availability(True, True, None, "M") is True
    # Invalid JSON
    assert determine_effective_availability(True, True, "invalid", "M") is True
    # Non-list JSON
    assert determine_effective_availability(True, True, '{"size": "M"}', "M") is True
    # Success scenario
    assert determine_effective_availability(True, True, '["S", "M"]', "M") is True
    assert determine_effective_availability(True, True, '["S", "M"]', "L") is False
