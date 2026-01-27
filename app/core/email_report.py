"""Daily email report for Price Spy."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.storage.database import Database
from app.storage.repositories import (
    TrackedItemRepository,
    ProductRepository,
    StoreRepository,
    PriceHistoryRepository,
)


from app.core.config import settings

def get_email_config() -> Dict[str, Any]:
    """Get email configuration from environment."""
    return {
        "enabled": settings.EMAIL_ENABLED,
        "recipient": settings.EMAIL_RECIPIENT,
        "sender": settings.EMAIL_SENDER,
        "smtp_host": settings.SMTP_HOST,
        "smtp_port": settings.SMTP_PORT,
        "smtp_user": settings.SMTP_USER,
        "smtp_password": settings.SMTP_PASSWORD,
        "use_tls": settings.SMTP_USE_TLS,
        "dashboard_url": settings.EMAIL_DASHBOARD_URL,
    }


def is_email_configured() -> bool:
    """Check if email is properly configured."""
    config = get_email_config()
    if not config["enabled"]:
        return False
    required = ["recipient", "sender", "smtp_host", "smtp_user", "smtp_password"]
    return all(config.get(key) for key in required)


def get_item_details(item_id: int, db: Database) -> Optional[Dict[str, Any]]:
    """Get product and store details for a tracked item."""
    tracked_repo = TrackedItemRepository(db)
    product_repo = ProductRepository(db)
    store_repo = StoreRepository(db)

    item = tracked_repo.get_by_id(item_id)
    if not item:
        return None

    product = product_repo.get_by_id(item.product_id)
    store = store_repo.get_by_id(item.store_id)

    return {
        "product_name": product.name if product else "Unknown",
        "store_name": store.name if store else "Unknown",
        "target_price": product.target_price if product else None,
        "target_unit": product.target_unit if product else None,
        "items_per_lot": item.items_per_lot,
        "quantity_size": item.quantity_size,
        "quantity_unit": item.quantity_unit,
        "url": item.url,
    }


def generate_report_data(
    results: List[Dict[str, Any]],
    db: Database
) -> Dict[str, Any]:
    """Generate report data from extraction results."""

    if not results:
        return {
            "date": datetime.now().strftime("%B %d, %Y"),
            "total": 0,
            "success_count": 0,
            "error_count": 0,
            "deals_count": 0,
            "deals": [],
            "price_drops": [],
            "price_increases": [],
            "items": [],
            "errors": [],
            "next_run": "Tomorrow 23:00",
        }

    price_repo = PriceHistoryRepository(db)
    items = []
    deals = []
    price_drops = []
    price_increases = []
    errors = []

    for result in results:
        item_id = result.get("item_id")
        status = result.get("status")
        price = result.get("price")
        currency = result.get("currency", "EUR")
        error_msg = result.get("error")

        # Get item details from database
        details = get_item_details(item_id, db) if item_id else None

        if details:
            product_name = details["product_name"]
            store_name = details["store_name"]
            target_price = details["target_price"]
            url = details["url"]
        else:
            product_name = f"Item #{item_id}"
            store_name = "Unknown"
            target_price = None
            url = None

        # Calculate price change
        price_change = 0
        price_change_pct = 0
        prev_price = None

        if status == "success" and url:
            # Get previous price
            history = price_repo.get_by_url(url)
            if len(history) > 1:
                # history[0] is the current one just saved
                prev_record = history[1]
                prev_price = prev_record.price
                price_change = price - prev_price
                if prev_price > 0:
                    price_change_pct = (price_change / prev_price) * 100

        # Check if it's a target hit vs a promo deal
        original_price = result.get("original_price")
        deal_type = result.get("deal_type")
        deal_description = result.get("deal_description")

        # Calculate if it's a target hit (unit-price aware)
        from app.core.price_calculator import calculate_volume_price, normalize_unit
        
        is_target_hit = False
        unit_price = None
        current_unit = None

        if status == "success" and price is not None:
            unit_price, current_unit = calculate_volume_price(
                price,
                details["items_per_lot"] if details else 1,
                details["quantity_size"] if details else 1,
                details["quantity_unit"] if details else None
            )
            
            t_price = details["target_price"] if details else None
            t_unit = details["target_unit"] if details else None
            
            if t_price is not None:
                if t_unit:
                    norm_target_unit = normalize_unit(t_unit)
                    norm_curr_unit = normalize_unit(current_unit) if current_unit else None
                    if norm_target_unit == norm_curr_unit:
                        is_target_hit = unit_price <= t_price
                else:
                    is_target_hit = price <= t_price

        is_promo_deal = False
        if status == "success" and price is not None:
            has_original_higher = original_price is not None and original_price > price
            has_deal_type = deal_type is not None and deal_type.lower() != "none"
            is_promo_deal = has_original_higher or has_deal_type
        
        is_price_drop = status == "success" and price_change < -0.01

        item_data = {
            "item_id": item_id,
            "product_name": product_name,
            "store_name": store_name,
            "price": price,
            "prev_price": prev_price,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "currency": currency,
            "target_price": target_price,
            "url": url,
            "status": status,
            "is_deal": is_promo_deal,
            "is_target_hit": is_target_hit,
            "is_price_drop": is_price_drop,
            "deal_type": deal_type,
            "deal_description": deal_description,
            "original_price": original_price,
            "error": error_msg,
        }

        if status == "success":
            items.append(item_data)
            if is_target_hit or is_promo_deal:
                deals.append(item_data)
            
            # Categorize changes
            if is_price_drop:
                price_drops.append(item_data)
            elif price_change > 0.01:
                price_increases.append(item_data)
        else:
            errors.append(item_data)

    # Sort price drops by most significant drop
    price_drops.sort(key=lambda x: x["price_change_pct"])

    success_count = len([r for r in results if r.get("status") == "success"])
    error_count = len([r for r in results if r.get("status") == "error"])

    # Identify planned but untracked products within 4 weeks (Spying Required)
    from datetime import datetime as dt, timedelta
    now_dt = dt.now()
    four_weeks_later = now_dt + timedelta(days=28)
    
    product_repo = ProductRepository(db)
    tracked_repo = TrackedItemRepository(db)
    all_products = product_repo.get_all()
    untracked_planned = []
    for product in all_products:
        if product.planned_date:
            try:
                planned_dt = dt.strptime(product.planned_date + '-1', "%G-W%V-%u")
                if planned_dt > four_weeks_later:
                    continue
            except (ValueError, TypeError):
                continue

            active_items = [ti for ti in tracked_repo.get_by_product(product.id) if ti.is_active]
            if not active_items:
                untracked_planned.append({
                    "id": product.id,
                    "name": product.name,
                    "planned_date": product.planned_date
                })
    
    untracked_planned.sort(key=lambda p: p["planned_date"])

    return {
        "date": datetime.now().strftime("%B %d, %Y"),
        "total": len(results),
        "success_count": success_count,
        "error_count": error_count,
        "deals_count": len(deals),
        "deals": deals,
        "price_drops": price_drops,
        "price_increases": price_increases,
        "untracked_planned": untracked_planned,
        "all_items": items,
        "errors": errors,
        "next_run": "Tomorrow 23:00",
    }


def build_subject(report_data: Dict[str, Any]) -> str:
    """Build email subject line."""
    total = report_data["total"]
    deals = report_data["deals_count"]
    errors = report_data["error_count"]

    parts = ["Price Spy Daily Report"]

    if deals > 0:
        parts.append(f"- {deals} Deal{'s' if deals > 1 else ''} Found!")

    parts.append(f"({total} item{'s' if total != 1 else ''} checked")

    if errors > 0:
        parts[-1] += f", {errors} error{'s' if errors > 1 else ''}"

    parts[-1] += ")"

    return " ".join(parts)


from jinja2 import Environment, FileSystemLoader

# Initialize Jinja2 environment for email templates
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "email")
env = Environment(loader=FileSystemLoader(template_dir))


def render_html_email(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Render HTML email template."""
    dashboard_url = config.get("dashboard_url", "http://localhost:8000")
    template = env.get_template("daily_report.html")
    return template.render(report=report_data, dashboard_url=dashboard_url)


def render_text_email(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Render plain text email template."""
    dashboard_url = config.get("dashboard_url", "http://localhost:8000")
    template = env.get_template("daily_report.txt")
    return template.render(report=report_data, dashboard_url=dashboard_url)


def send_email(
    to: str,
    subject: str,
    html: str,
    text: str,
    config: Dict[str, Any]
) -> bool:
    """Send email via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config["sender"]
    msg["To"] = to

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
            if config.get("use_tls", True):
                server.starttls()
            server.login(config["smtp_user"], config["smtp_password"])
            server.sendmail(config["sender"], to, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_daily_report(
    results: List[Dict[str, Any]],
    db: Database
) -> bool:
    """Send daily email report after scheduler run."""
    if not is_email_configured():
        return False

    config = get_email_config()
    report_data = generate_report_data(results, db)

    # Skip if no items were checked
    if report_data["total"] == 0:
        return False

    # Generate email content
    html_content = render_html_email(report_data, config)
    text_content = render_text_email(report_data, config)

    # Build subject
    subject = build_subject(report_data)

    # Send email
    return send_email(
        to=config["recipient"],
        subject=subject,
        html=html_content,
        text=text_content,
        config=config
    )
