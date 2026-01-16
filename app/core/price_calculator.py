"""Price calculation and comparison logic."""

from typing import Optional, Tuple

from app.models.schemas import PriceComparison


# Unit conversion constants
UNIT_CONVERSIONS = {
    "ml": ("L", 1000),      # 1000ml = 1L
    "cl": ("L", 100),       # 100cl = 1L
    "g": ("kg", 1000),      # 1000g = 1kg
    "L": ("L", 1),          # Already in L
    "kg": ("kg", 1),        # Already in kg
}


def calculate_volume_price(
    page_price: float,
    items_per_lot: int,
    quantity_size: float,
    quantity_unit: str
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
    previous: Optional[float]
) -> PriceComparison:
    """
    Compare current price with previous price.

    Args:
        current: Current price
        previous: Previous price (None if first check)

    Returns:
        PriceComparison with change details
    """
    if previous is None:
        return PriceComparison(
            current_price=current,
            previous_price=None,
            price_change=None,
            price_change_percent=None,
            is_price_drop=False
        )

    price_change = round(current - previous, 2)
    price_change_percent = round((price_change / previous) * 100, 2)
    is_price_drop = price_change < 0

    return PriceComparison(
        current_price=current,
        previous_price=previous,
        price_change=price_change,
        price_change_percent=price_change_percent,
        is_price_drop=is_price_drop
    )
