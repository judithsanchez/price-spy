from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.api.deps import get_db
from app.storage.repositories import (
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
    PriceHistoryRepository,
    CategoryRepository,
)

router = APIRouter(
    tags=["UI"]
)

# Templates directory (assuming it's in app/templates)
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

class DashboardItem(BaseModel):
    """View model for dashboard items."""
    id: int
    product_name: str
    store_name: str
    url: str
    price: Optional[float] = None
    currency: str = "EUR"
    target_price: Optional[float] = None
    target_unit: Optional[str] = None
    unit_price: Optional[float] = None
    unit: Optional[str] = None
    is_available: Optional[bool] = None
    notes: Optional[str] = None
    screenshot_path: Optional[str] = None
    last_checked: Optional[str] = None
    original_price: Optional[float] = None
    deal_type: Optional[str] = None
    discount_percentage: Optional[float] = None
    discount_fixed_amount: Optional[float] = None
    deal_description: Optional[str] = None
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
async def dashboard(request: Request, db=Depends(get_db)):
    """Render dashboard page."""
    from app.core.price_calculator import calculate_volume_price
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=7)

    try:
        product_repo = ProductRepository(db)
        store_repo = StoreRepository(db)
        tracked_repo = TrackedItemRepository(db)
        price_repo = PriceHistoryRepository(db)

        tracked_items = tracked_repo.get_all()
        products_map = {}
        low_stock_warnings = []
        price_increase_warnings = []
        graph_data = {
            "labels": [],
            "datasets": []
        }
        
        all_timestamps = set()

        for item in tracked_items:
            if not item.is_active:
                continue

            product = product_repo.get_by_id(item.product_id)
            if not product:
                continue
                
            if product.id not in products_map:
                products_map[product.id] = {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "target_price": product.target_price,
                    "target_unit": product.target_unit,
                    "tracked_items": []
                }
            
            store = store_repo.get_by_id(item.store_id)
            latest_price_rec = price_repo.get_latest_by_url(item.url)
            history = price_repo.get_history_since(item.url, cutoff)
            
            trend = "stable"
            if len(history) >= 2:
                prev_price = history[1].price
                curr_price = history[0].price
                if curr_price and prev_price:
                    if curr_price > prev_price:
                        trend = "up"
                        price_increase_warnings.append({
                            "product_name": product.name,
                            "store_name": store.name if store else "Unknown",
                            "price": curr_price,
                            "previous_price": prev_price,
                            "currency": latest_price_rec.currency if latest_price_rec else "EUR"
                        })
                    elif curr_price < prev_price:
                        trend = "down"

            screenshot_path = f"screenshots/{item.id}.png"
            # In a real environment we would check if Path(screenshot_path).exists()
            # But the logic from main.py assumes it can be checked or just passed.
            # I will keep it consistent with main.py.
            from pathlib import Path as OSPath
            has_screenshot = OSPath(screenshot_path).exists()

            unit_price = None
            unit = None
            if latest_price_rec and latest_price_rec.price:
                unit_price, unit = calculate_volume_price(
                    latest_price_rec.price,
                    item.items_per_lot,
                    item.quantity_size,
                    item.quantity_unit
                )
                unit_price = round(unit_price, 2)

            price = latest_price_rec.price if latest_price_rec else None
            original_price = latest_price_rec.original_price if latest_price_rec else None
            deal_type = latest_price_rec.deal_type if latest_price_rec else None
            deal_description = latest_price_rec.deal_description if latest_price_rec else None

            is_target_hit = False
            if price is not None and product.target_price is not None:
                if product.target_unit:
                    from app.core.price_calculator import normalize_unit
                    normalized_target_unit = normalize_unit(product.target_unit)
                    normalized_current_unit = normalize_unit(unit) if unit else None
                    
                    if unit_price is not None and normalized_target_unit == normalized_current_unit:
                        is_target_hit = unit_price <= product.target_price
                else:
                    is_target_hit = price <= product.target_price

            is_price_drop = trend == "down"
            is_deal = False
            if price is not None:
                has_original_higher = original_price is not None and original_price > price
                has_deal_type = deal_type is not None and deal_type.lower() != "none"
                is_deal = has_original_higher or has_deal_type

            products_map[product.id]["tracked_items"].append({
                "id": item.id,
                "store_name": store.name if store else "Unknown",
                "url": item.url,
                "price": price,
                "currency": latest_price_rec.currency if latest_price_rec else "EUR",
                "unit_price": unit_price,
                "unit": unit,
                "target_unit": product.target_unit,
                "trend": trend,
                "is_deal": is_deal,
                "is_price_drop": is_price_drop,
                "is_target_hit": is_target_hit,
                "is_best_deal": False,
                "is_available": latest_price_rec.is_available if latest_price_rec else None,
                "is_size_matched": latest_price_rec.is_size_matched if latest_price_rec else True,
                "notes": latest_price_rec.notes if latest_price_rec else None,
                "screenshot_path": screenshot_path if has_screenshot else None,
                "original_price": original_price,
                "deal_type": deal_type,
                "deal_description": deal_description,
            })
            
            if latest_price_rec and latest_price_rec.notes:
                notes_lower = latest_price_rec.notes.lower()
                low_stock_keywords = ["low stock", "units left", "stock low", "only", "last units"]
                if any(kw in notes_lower for kw in low_stock_keywords):
                    low_stock_warnings.append({
                        "product_name": product.name,
                        "store_name": store.name if store else "Unknown",
                        "notes": latest_price_rec.notes
                    })
            
            if history:
                item_label = f"{product.name} ({store.name if store else '?'})"
                dataset = {
                    "label": item_label,
                    "data": [],
                    "borderColor": f"hsl({(item.id * 137) % 360}, 70%, 50%)",
                    "fill": False,
                    "tension": 0.1
                }
                for h in reversed(history):
                    ts = h.created_at.strftime("%Y-%m-%d %H:%M")
                    all_timestamps.add(ts)
                    dataset["data"].append({"x": ts, "y": h.price})
                graph_data["datasets"].append(dataset)

        sorted_labels = sorted(list(all_timestamps))
        graph_data["labels"] = sorted_labels
        sorted_products = sorted(products_map.values(), key=lambda p: p["name"])
        
        for p in sorted_products:
            p["has_best_deal"] = False
            p["has_target_hit"] = any(it["is_target_hit"] for it in p["tracked_items"])
            p["has_deal"] = any(it["is_deal"] or it["is_price_drop"] for it in p["tracked_items"])
            
            valid_items = [it for it in p["tracked_items"] if it["unit_price"] is not None and it["is_available"] is not False]
            if len(valid_items) > 1:
                best_item = min(valid_items, key=lambda x: x["unit_price"])
                for it in p["tracked_items"]:
                    if it["id"] == best_item["id"]:
                        it["is_best_deal"] = True
                        p["has_best_deal"] = True
        
        sorted_products.sort(key=lambda p: (not p["has_target_hit"], not p["has_deal"], p["name"]))
        
        all_deals = []
        for p in sorted_products:
            for item in p["tracked_items"]:
                if item["is_target_hit"] or item["is_deal"]:
                    all_deals.append({
                        "product_name": p["name"],
                        "price": item["price"],
                        "currency": item["currency"],
                        "unit_price": item["unit_price"],
                        "unit": item["unit"],
                        "target_price": p["target_price"],
                        "target_unit": p["target_unit"],
                        "is_target_hit": item["is_target_hit"]
                    })

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "products": sorted_products,
                "deals": all_deals,
                "low_stock": low_stock_warnings,
                "price_increases": price_increase_warnings,
                "graph_data": graph_data,
                "has_any_items": len(tracked_items) > 0
            }
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

@router.get("/stores")
async def stores_page(request: Request):
    """Render stores management page."""
    return templates.TemplateResponse(request, "stores.html", {})

@router.get("/tracked-items")
async def tracked_items_page(request: Request):
    """Render tracked items management page."""
    return templates.TemplateResponse(request, "tracked-items.html", {})

@router.get("/logs")
async def logs_page(request: Request):
    """Render logs page."""
    return templates.TemplateResponse(request, "logs.html", {})

@router.get("/categories")
async def categories_page(request: Request):
    """Render categories management page."""
    return templates.TemplateResponse(request, "categories.html", {})

@router.get("/labels")
async def labels_page(request: Request):
    """Render labels management page."""
    return templates.TemplateResponse(request, "labels.html", {})
