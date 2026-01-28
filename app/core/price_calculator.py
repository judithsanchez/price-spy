"""Price calculation and comparison logic."""

from typing import Optional, Tuple

from app.models.schemas import PriceComparison

# Unit conversion constants
UNIT_CONVERSIONS = {
    "ml": ("L", 1000),  # 1000ml = 1L
    "cl": ("L", 100),  # 100cl = 1L
    "g": ("kg", 1000),  # 1000g = 1kg
    "L": ("L", 1),  # Already in L
    "kg": ("kg", 1),  # Already in kg
}


def normalize_unit(unit: str) -> str:
    """Normalize unit string to match standard units (e.g., 'KG' -> 'kg')."""
    if not unit:
        return ""
    unit = unit.lower().strip()
    if unit in UNIT_CONVERSIONS:
        return UNIT_CONVERSIONS[unit][0]
    return unit


def calculate_volume_price(
    page_price: float, items_per_lot: int, quantity_size: float, quantity_unit: str
) -> Tuple[float, str]:
    """
    Calculate price per standard unit.

    Args:
        page_price: Total price shown on page (e.g., €6.00 for a 6-pack)
        items_per_lot: Number of items in the lot (e.g., 6 for a 6-pack)
        quantity_size: Size of one atomic unit (e.g., 330 for 330ml)
        quantity_unit: Unit of measurement (e.g., "ml", "g", "L", "kg")

    Returns:
        Tuple of (price_per_unit, standard_unit)

    Example:
        6-pack of 330ml cans at €6.00:
        - Price per can: €6.00 / 6 = €1.00
        - Total volume: 330ml * 6 = 1980ml = 1.98L
        - Price per L: €6.00 / 1.98L = €3.03/L
    """
    # Get conversion factor
    if quantity_unit in UNIT_CONVERSIONS:
        standard_unit, factor = UNIT_CONVERSIONS[quantity_unit]
    else:
        # Unknown unit - treat as atomic (e.g., "piece", "stuks")
        standard_unit = quantity_unit
        factor = 1

    # Calculate total quantity in standard units
    if factor > 1:
        # Convert to standard unit (e.g., ml to L)
        total_quantity = (quantity_size * items_per_lot) / factor
    else:
        # Already in standard unit or atomic
        total_quantity = quantity_size * items_per_lot

    # Calculate price per standard unit
    volume_price = page_price / total_quantity

    return volume_price, standard_unit


def compare_prices(
    current: float,
    previous: Optional[float],
    original_price: Optional[float] = None,
    deal_type: Optional[str] = None,
    discount_percentage: Optional[float] = None,
    discount_fixed_amount: Optional[float] = None,
    deal_description: Optional[str] = None,
) -> PriceComparison:
    """
    Compare current price with previous price and evaluate deals.

    Args:
        current: Current price
        previous: Previous price (None if first check)
        original_price: Original price before any discount
        deal_type: Type of promotion detected (e.g., '1+1 gratis')
        discount_percentage: Percentage off
        discount_fixed_amount: Fixed amount off
        deal_description: Explanation of the deal
    """
    is_deal = False
    if original_price and original_price > current:
        is_deal = True
    elif deal_type and deal_type.lower() != "none":
        is_deal = True

    if previous is None:
        return PriceComparison(
            current_price=current,
            previous_price=None,
            price_change=None,
            price_change_percent=None,
            is_price_drop=False,
            is_deal=is_deal,
            original_price=original_price,
            deal_type=deal_type,
            discount_percentage=discount_percentage,
            discount_fixed_amount=discount_fixed_amount,
            deal_description=deal_description,
        )

    price_change = round(current - previous, 2)
    price_change_percent = (
        round((price_change / previous) * 100, 2) if previous > 0 else 0
    )
    is_price_drop = price_change < 0

    return PriceComparison(
        current_price=current,
        previous_price=previous,
        price_change=price_change,
        price_change_percent=price_change_percent,
        is_price_drop=is_price_drop,
        is_deal=is_deal or is_price_drop,
        original_price=original_price,
        deal_type=deal_type,
        discount_percentage=discount_percentage,
        discount_fixed_amount=discount_fixed_amount,
        deal_description=deal_description,
    )


def is_size_available(target_size: str, available_sizes: list[str]) -> bool:
    """
    Check if a target size is present in the list of available sizes.
    Performs case-insensitive matching and strips whitespace.
    """
    if not target_size or not available_sizes:
        return False

    target = target_size.lower().strip()
    return any(s.lower().strip() == target for s in available_sizes)


def determine_effective_availability(
    is_size_sensitive: bool,
    raw_is_available: bool,
    available_sizes_json: Optional[str],
    target_size: Optional[str],
) -> bool:
    """
    Determine the effective availability of an item.
    If category is size-sensitive and we have a target size,
    availability depends on that size being in stock.
    Otherwise, it uses the raw availability from the page.
    """
    if not raw_is_available:
        return False

    if not is_size_sensitive:
        return raw_is_available

    if not target_size or not available_sizes_json:
        # Sensitive but no target or no sizes extracted, fall back to raw
        return raw_is_available

    import json

    try:
        extracted_sizes = json.loads(available_sizes_json)
        if not isinstance(extracted_sizes, list):
            return raw_is_available
        return is_size_available(target_size, extracted_sizes)
    except Exception:
        return raw_is_available
