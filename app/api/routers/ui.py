from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.api.deps import get_db
from app.core.price_calculator import (
    calculate_volume_price,
    normalize_unit,
)
from app.storage.database import Database
from app.storage.repositories import (
    PriceHistoryRepository,
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
)

router = APIRouter(tags=["UI"])

# Templates directory (assuming it's in app/templates)
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

MIN_HISTORY_FOR_TREND = 2


class DashboardItem(BaseModel):
    """View model for dashboard items."""

    id: int
    product_name: str
    store_name: str
    url: str
    price: float | None = None
    currency: str = "EUR"
    target_price: float | None = None
    target_unit: str | None = None
    unit_price: float | None = None
    unit: str | None = None
    is_available: bool | None = None
    notes: str | None = None
    screenshot_path: str | None = None
    last_checked: str | None = None
    original_price: float | None = None
    deal_type: str | None = None
    discount_percentage: float | None = None
    discount_fixed_amount: float | None = None
    deal_description: str | None = None
    is_deal: bool = False
    is_price_drop: bool = False
    is_target_hit: bool = False
    is_best_deal: bool = False


def _get_chart_color(index: int) -> str:
    """Get a color for chart lines based on index."""
    colors = [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
    ]
    return colors[index % len(colors)]


@router.get("/")
async def dashboard(request: Request, db: Annotated[Database, Depends(get_db)]):
    """Render dashboard page."""

    cutoff = datetime.now() - timedelta(days=7)

    try:
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        tracked_items = tracked_repo.get_all()
        products_map: dict[int, dict] = {}
        low_stock_warnings: list[dict] = []
        price_increase_warnings: list[dict] = []
        graph_data: dict[str, list] = {"labels": [], "datasets": []}

        all_timestamps = set()

        for item in tracked_items:
            if not item.is_active:
                continue

            product = product_repo.get_by_id(item.product_id)
            if not product:
                continue

            pid = int(product.id or 0)
            if pid not in products_map:
                products_map[pid] = {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "target_price": product.target_price,
                    "target_unit": product.target_unit,
                    "tracked_items": [],
                }

            store = store_repo.get_by_id(item.store_id)
            latest_price_rec = price_repo.get_latest_by_url(item.url)
            history = price_repo.get_history_since(item.url, cutoff)

            trend = "stable"
            if len(history) >= MIN_HISTORY_FOR_TREND:
                prev_price = history[1].price
                curr_price = history[0].price
                if curr_price and prev_price:
                    if curr_price > prev_price:
                        trend = "up"
                        price_increase_warnings.append(
                            {
                                "product_name": product.name,
                                "store_name": store.name if store else "Unknown",
                                "price": curr_price,
                                "previous_price": prev_price,
                                "currency": latest_price_rec.currency
                                if latest_price_rec
                                else "EUR",
                            }
                        )
                    elif curr_price < prev_price:
                        trend = "down"

            screenshot_path = f"screenshots/{item.id}.png"
            # In a real environment we would check if Path(screenshot_path).exists()
            # But the logic from main.py assumes it can be checked or just passed.
            # I will keep it consistent with main.py.
            has_screenshot = Path(screenshot_path).exists()

            unit_price = None
            unit = None
            if latest_price_rec and latest_price_rec.price:
                unit_price, unit = calculate_volume_price(
                    latest_price_rec.price,
                    item.items_per_lot,
                    item.quantity_size,
                    item.quantity_unit,
                )
                unit_price = round(unit_price, 2)

            price = latest_price_rec.price if latest_price_rec else None
            original_price = (
                latest_price_rec.original_price if latest_price_rec else None
            )
            deal_type = latest_price_rec.deal_type if latest_price_rec else None
            deal_description = (
                latest_price_rec.deal_description if latest_price_rec else None
            )

            is_target_hit = False
            if price is not None and product.target_price is not None:
                if product.target_unit:
                    normalized_target_unit = normalize_unit(product.target_unit)
                    normalized_current_unit = normalize_unit(unit) if unit else None

                    if (
                        unit_price is not None
                        and normalized_target_unit == normalized_current_unit
                    ):
                        is_target_hit = unit_price <= product.target_price
                else:
                    is_target_hit = price <= product.target_price

            is_price_drop = trend == "down"
            is_deal = False
            if price is not None:
                has_original_higher = (
                    original_price is not None and original_price > price
                )
                has_deal_type = deal_type is not None and deal_type.lower() != "none"
                is_deal = has_original_higher or has_deal_type

            pid = int(product.id or 0)
            products_map[pid]["tracked_items"].append(
                {
                    "id": item.id,
                    "store_name": store.name if store else "Unknown",
                    "url": item.url,
                    "price": price,
                    "currency": latest_price_rec.currency
                    if latest_price_rec
                    else "EUR",
                    "unit_price": unit_price,
                    "unit": unit,
                    "target_unit": product.target_unit,
                    "trend": trend,
                    "is_deal": is_deal,
                    "is_price_drop": is_price_drop,
                    "is_target_hit": is_target_hit,
                    "is_best_deal": False,
                    "is_available": latest_price_rec.is_available
                    if latest_price_rec
                    else None,
                    "is_size_matched": latest_price_rec.is_size_matched
                    if latest_price_rec
                    else True,
                    "notes": latest_price_rec.notes if latest_price_rec else None,
                    "screenshot_path": screenshot_path if has_screenshot else None,
                    "original_price": original_price,
                    "deal_type": deal_type,
                    "deal_description": deal_description,
                }
            )

            if latest_price_rec and latest_price_rec.notes:
                notes_lower = latest_price_rec.notes.lower()
                low_stock_keywords = [
                    "low stock",
                    "units left",
                    "stock low",
                    "only",
                    "last units",
                ]
                if any(kw in notes_lower for kw in low_stock_keywords):
                    low_stock_warnings.append(
                        {
                            "product_name": product.name,
                            "store_name": store.name if store else "Unknown",
                            "notes": latest_price_rec.notes,
                        }
                    )

            if history:
                item_label = f"{product.name} ({store.name if store else '?'})"
                dataset: dict[str, Any] = {
                    "label": item_label,
                    "data": [],
                    "borderColor": f"hsl({(int(item.id or 0) * 137) % 360}, 70%, 50%)",
                    "fill": False,
                    "tension": 0.1,
                }
                for h in reversed(history):
                    ts = h.created_at.strftime("%Y-%m-%d %H:%M")
                    all_timestamps.add(ts)
                    dataset["data"].append({"x": ts, "y": h.price})
                graph_data["datasets"].append(dataset)

        sorted_labels = sorted(all_timestamps)
        graph_data["labels"] = sorted_labels
        sorted_products = sorted(products_map.values(), key=lambda p: p["name"])

        for p in sorted_products:
            p["has_best_deal"] = False
            p["has_target_hit"] = any(it["is_target_hit"] for it in p["tracked_items"])
            p["has_deal"] = any(
                it["is_deal"] or it["is_price_drop"] for it in p["tracked_items"]
            )

            valid_items = [
                it
                for it in p["tracked_items"]
                if it["unit_price"] is not None and it["is_available"] is not False
            ]
            if len(valid_items) > 1:
                best_item = min(valid_items, key=lambda x: x["unit_price"])
                for it in p["tracked_items"]:
                    if it["id"] == best_item["id"]:
                        it["is_best_deal"] = True
                        p["has_best_deal"] = True

        sorted_products.sort(
            key=lambda p: (not p["has_target_hit"], not p["has_deal"], p["name"])
        )

        all_deals: list[dict[str, Any]] = []
        for p in sorted_products:
            all_deals.extend(
                {
                    "product_name": p["name"],
                    "price": item["price"],
                    "currency": item["currency"],
                    "unit_price": item["unit_price"],
                    "unit": item["unit"],
                    "target_price": p["target_price"],
                    "target_unit": p["target_unit"],
                    "is_target_hit": item["is_target_hit"],
                }
                for item in p["tracked_items"]
                if item["is_target_hit"] or item["is_deal"]
            )

        # Identify planned but untracked products within 4 weeks

        now = datetime.now()
        four_weeks_later = now + timedelta(days=28)

        all_products = product_repo.get_all()
        untracked_planned_products = []
        for product in all_products:
            if product.planned_date:
                # Format is YYYY-Www, e.g., '2026-W05'
                try:
                    # Parse as the first day of that week
                    planned_dt = datetime.strptime(
                        product.planned_date + "-1", "%G-W%V-%u"
                    )

                    # Only alert if the planned date is within the next 4 weeks
                    # (Also include past dates if they were never tracked)
                    if planned_dt > four_weeks_later:
                        continue
                except (ValueError, TypeError):
                    continue

                active_items = [
                    ti
                    for ti in tracked_repo.get_by_product(int(product.id or 0))
                    if ti.is_active
                ]
                if not active_items:
                    untracked_planned_products.append(
                        {
                            "id": product.id,
                            "name": product.name,
                            "planned_date": product.planned_date,
                        }
                    )

        # Sort by planned_date (YYYY-Www) which is chronological
        untracked_planned_products.sort(key=lambda p: str(p["planned_date"] or ""))

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "products": sorted_products,
                "deals": all_deals,
                "low_stock": low_stock_warnings,
                "price_increases": price_increase_warnings,
                "untracked_planned": untracked_planned_products,
                "graph_data": graph_data,
                "has_any_items": len(tracked_items) > 0,
            },
        )
    finally:
        db.close()


@router.get("/admin")
async def admin_page(request: Request):
    """Render admin hub page."""
    return templates.TemplateResponse(request, "admin.html", {})


@router.get("/products")
async def products_page(request: Request):
    """Render products management page."""
    return templates.TemplateResponse(request, "products.html", {})


@router.get("/timeline")
async def timeline_page(request: Request, db: Annotated[Database, Depends(get_db)]):
    """Render the vertical wishlist timeline."""

    product_repo = ProductRepository(db)
    price_repo = PriceHistoryRepository(db)

    products = product_repo.get_all()
    timeline_data: dict[int, dict[int, list[dict]]] = defaultdict(
        lambda: defaultdict(list)
    )

    # Filter products that have a planned date
    planned_products = [p for p in products if p.planned_date]

    for p in planned_products:
        # planned_date is '2026-W05'
        try:
            if not p.planned_date:
                continue
            year_str, week_str = p.planned_date.split("-W")
            year = int(year_str)
            week = int(week_str)

            # Get latest price for the product (best deal among its tracked items)

            tracked_item_repo = TrackedItemRepository(db)
            tracked_items = tracked_item_repo.get_by_product(int(p.id or 0))

            best_price = None
            best_currency = "EUR"

            for item in tracked_items:
                latest = price_repo.get_latest_by_url(item.url)
                if (
                    latest
                    and latest.price
                    and (best_price is None or latest.price < best_price)
                ):
                    best_price = latest.price
                    best_currency = latest.currency

            product_card = {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "target_price": p.target_price,
                "planned_date": p.planned_date,
                "best_price": best_price,
                "currency": best_currency,
                "tracked_count": len(tracked_items),
            }

            cast(list, timeline_data[year][week]).append(product_card)
        except (ValueError, AttributeError):
            continue

    # Sort years descending, weeks ascending
    sorted_timeline = []
    for year in sorted(timeline_data.keys(), reverse=True):
        year_data: dict[str, Any] = {"year": year, "weeks": []}
        for week in sorted(timeline_data[year].keys()):
            year_data["weeks"].append(
                {"week": week, "products": timeline_data[year][week]}
            )
        sorted_timeline.append(year_data)

    return templates.TemplateResponse(
        request, "timeline.html", {"timeline": sorted_timeline}
    )


@router.get("/tracked-items")
async def tracked_items_page(request: Request):
    """Render tracked items management page."""
    return templates.TemplateResponse(request, "tracked-items.html", {})
