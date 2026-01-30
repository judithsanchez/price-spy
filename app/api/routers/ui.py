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
from app.models.schemas import PriceHistoryRecord, TrackedItem
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


def _calculate_trend(
    history: list[Any],
    product_name: str,
    store_name: str,
    latest_currency: str,
) -> tuple[str, dict[str, Any] | None]:
    """Calculate price trend and return trend string and warning if any."""
    trend = "stable"
    warning = None
    if len(history) >= MIN_HISTORY_FOR_TREND:
        prev_price = history[1].price
        curr_price = history[0].price
        if curr_price and prev_price:
            if curr_price > prev_price:
                trend = "up"
                warning = {
                    "product_name": product_name,
                    "store_name": store_name,
                    "price": curr_price,
                    "previous_price": prev_price,
                    "currency": latest_currency,
                }
            elif curr_price < prev_price:
                trend = "down"
    return trend, warning


def _check_target_hit(
    price: float | None,
    unit_price: float | None,
    unit: str | None,
    product: Any,
) -> bool:
    """Check if the target price condition is met."""
    if price is None or product.target_price is None:
        return False

    if product.target_unit:
        normalized_target = normalize_unit(product.target_unit)
        normalized_current = normalize_unit(unit) if unit else None
        if unit_price is not None and normalized_target == normalized_current:
            return unit_price <= product.target_price
    else:
        return price <= product.target_price
    return False


def _check_stock_warnings(
    latest_price_rec: Any, product_name: str, store_name: str
) -> dict[str, Any] | None:
    """Check for low stock keywords in notes."""
    if not latest_price_rec or not latest_price_rec.notes:
        return None

    notes_lower = latest_price_rec.notes.lower()
    low_stock_keywords = [
        "low stock",
        "units left",
        "stock low",
        "only",
        "last units",
    ]

    if any(kw in notes_lower for kw in low_stock_keywords):
        return {
            "product_name": product_name,
            "store_name": store_name,
            "notes": latest_price_rec.notes,
        }
    return None


def _build_graph_dataset(
    history: list[Any],
    product_name: str,
    store_name: str,
    item_id: int,
) -> tuple[dict[str, Any], list[str]] | None:
    """Build graph dataset from history."""
    if not history:
        return None

    item_label = f"{product_name} ({store_name})"
    dataset: dict[str, Any] = {
        "label": item_label,
        "data": [],
        "borderColor": f"hsl({(int(item_id or 0) * 137) % 360}, 70%, 50%)",
        "fill": False,
        "tension": 0.1,
    }
    timestamps = []
    for h in reversed(history):
        ts = h.created_at.strftime("%Y-%m-%d %H:%M")
        timestamps.append(ts)
        dataset["data"].append({"x": ts, "y": h.price})

    return dataset, timestamps


def _ensure_product_in_map(product: Any, products_map: dict[int, dict]) -> int:
    """Ensure product exists in the map and return its ID."""
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
    return pid


def _build_item_dict(
    item: TrackedItem,
    store_name: str,
    latest_price_rec: Any,
    metrics: dict,
    product: Any,
    screenshot_path: str,
) -> dict[str, Any]:
    """Build the dictionary representation of a tracked item."""
    price = metrics["price"]
    original_price = metrics["original_price"]
    deal_type = metrics["deal_type"]

    # Deal Logic
    is_price_drop = metrics["trend"] == "down"
    is_deal = False
    if price is not None:
        has_original_higher = original_price is not None and original_price > price
        has_deal_type = deal_type is not None and deal_type.lower() != "none"
        is_deal = has_original_higher or has_deal_type

    has_screenshot = Path(screenshot_path).exists()

    return {
        "id": item.id,
        "store_name": store_name,
        "url": item.url,
        "price": price,
        "currency": metrics["currency"],
        "unit_price": metrics["unit_price"],
        "unit": metrics["unit"],
        "target_unit": product.target_unit,
        "trend": metrics["trend"],
        "is_deal": is_deal,
        "is_price_drop": is_price_drop,
        "is_target_hit": metrics["is_target_hit"],
        "is_best_deal": False,
        "is_available": latest_price_rec.is_available if latest_price_rec else None,
        "is_size_matched": latest_price_rec.is_size_matched
        if latest_price_rec
        else True,
        "notes": latest_price_rec.notes if latest_price_rec else None,
        "screenshot_path": screenshot_path if has_screenshot else None,
        "original_price": original_price,
        "deal_type": deal_type,
        "deal_description": latest_price_rec.deal_description
        if latest_price_rec
        else None,
    }


def _calculate_item_metrics(
    item: TrackedItem,
    product: Any,
    store_name: str,
    latest_price_rec: Any,
    history: list[PriceHistoryRecord],
    warnings_list: list[dict],
) -> dict[str, Any]:
    """Calculate price metrics, trend, and target hit status."""
    current_currency = latest_price_rec.currency if latest_price_rec else "EUR"
    trend, warning = _calculate_trend(
        history, str(product.name), store_name, current_currency
    )

    if warning:
        warnings_list.append(warning)

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

    # Check Target Hit
    is_target_hit = _check_target_hit(price, unit_price, unit, product)

    return {
        "trend": trend,
        "currency": current_currency,
        "unit_price": unit_price,
        "unit": unit,
        "price": price,
        "original_price": latest_price_rec.original_price if latest_price_rec else None,
        "deal_type": latest_price_rec.deal_type if latest_price_rec else None,
        "is_target_hit": is_target_hit,
    }


def _process_dashboard_item(
    item: TrackedItem,
    product_repo: ProductRepository,
    store_repo: StoreRepository,
    price_repo: PriceHistoryRepository,
    products_map: dict[int, dict],
    low_stock_warnings: list[dict],
    price_increase_warnings: list[dict],
    graph_data: dict[str, list],
    all_timestamps: set[str],
    cutoff: datetime,
) -> None:
    """Process a single tracked item for the dashboard."""
    if not item.is_active:
        return

    product = product_repo.get_by_id(item.product_id)
    if not product:
        return

    pid = _ensure_product_in_map(product, products_map)

    store = store_repo.get_by_id(item.store_id)
    latest_price_rec = price_repo.get_latest_by_url(item.url)
    history = price_repo.get_history_since(item.url, cutoff)
    store_name = store.name if store else "Unknown"

    # Calculate metrics & Trend
    metrics = _calculate_item_metrics(
        item,
        product,
        store_name,
        latest_price_rec,
        history,
        price_increase_warnings,
    )

    # Screenshot Path
    screenshot_path = f"screenshots/{item.id}.png"

    # Add to Map
    item_dict = _build_item_dict(
        item, store_name, latest_price_rec, metrics, product, screenshot_path
    )
    products_map[pid]["tracked_items"].append(item_dict)

    # Check Stock Warnings
    stock_warning = _check_stock_warnings(
        latest_price_rec, str(product.name), store_name
    )
    if stock_warning:
        low_stock_warnings.append(stock_warning)

    # Build Graph Data
    graph_res = _build_graph_dataset(
        history, str(product.name), store_name, int(item.id or 0)
    )
    if graph_res:
        dataset, timestamps = graph_res
        graph_data["datasets"].append(dataset)
        all_timestamps.update(timestamps)


def _apply_best_deal_logic(sorted_products: list[dict]) -> None:
    """Identify and mark the best deal for each product."""
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


def _get_untracked_planned_products(
    product_repo: ProductRepository, tracked_repo: TrackedItemRepository
) -> list[dict]:
    """Identify planned but untracked products within the next 4 weeks."""
    now = datetime.now()
    four_weeks_later = now + timedelta(days=28)

    all_products = product_repo.get_all()
    untracked_planned_products = []
    for product in all_products:
        if not product.planned_date:
            continue

        try:
            # Parse as the first day of that week (e.g., '2026-W05-1')
            planned_dt = datetime.strptime(product.planned_date + "-1", "%G-W%V-%u")
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

    untracked_planned_products.sort(key=lambda p: str(p["planned_date"] or ""))
    return untracked_planned_products


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
        all_timestamps: set[str] = set()

        for item in tracked_items:
            _process_dashboard_item(
                item,
                product_repo,
                store_repo,
                price_repo,
                products_map,
                low_stock_warnings,
                price_increase_warnings,
                graph_data,
                all_timestamps,
                cutoff,
            )

        sorted_labels = sorted(all_timestamps)
        graph_data["labels"] = sorted_labels
        sorted_products = sorted(products_map.values(), key=lambda p: p["name"])

        # Apply best deal logic & flags
        _apply_best_deal_logic(sorted_products)

        # Final Sort for UI
        sorted_products.sort(
            key=lambda p: (not p["has_target_hit"], not p["has_deal"], p["name"])
        )

        # Flatten deals for summary section
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

        # Identify planned but untracked products
        untracked_planned_products = _get_untracked_planned_products(
            product_repo, tracked_repo
        )

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

            best_deal = None

            for item in tracked_items:
                latest = price_repo.get_latest_by_url(item.url)
                if not latest or not latest.price:
                    continue

                u_price, u_unit = calculate_volume_price(
                    latest.price,
                    item.items_per_lot,
                    item.quantity_size,
                    item.quantity_unit,
                )

                current_deal = {
                    "price": latest.price,
                    "currency": latest.currency,
                    "unit_price": u_price,
                    "unit": u_unit,
                }

                if best_deal is None:
                    best_deal = current_deal
                    continue

                # Comparison Logic
                # 1. If both have unit prices, compare unit prices
                if (
                    current_deal["unit_price"] is not None
                    and best_deal["unit_price"] is not None
                ):
                    if current_deal["unit_price"] < best_deal["unit_price"]:
                        best_deal = current_deal

                # 2. If current has unit price but best doesn't, prefer current
                elif (
                    current_deal["unit_price"] is not None
                    and best_deal["unit_price"] is None
                ):
                    best_deal = current_deal

                # 3. If neither has unit price, compare raw prices
                elif (
                    current_deal["unit_price"] is None
                    and best_deal["unit_price"] is None
                ):
                    if current_deal["price"] < best_deal["price"]:
                        best_deal = current_deal

            product_card = {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "target_price": p.target_price,
                "target_unit": p.target_unit,
                "planned_date": p.planned_date,
                "best_price": best_deal["price"] if best_deal else None,
                "best_unit_price": best_deal["unit_price"] if best_deal else None,
                "best_unit": best_deal["unit"] if best_deal else None,
                "currency": best_deal["currency"] if best_deal else "EUR",
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
