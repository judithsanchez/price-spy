"""Daily email report for Price Spy."""

import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.storage.database import Database
from app.storage.repositories import (
    PriceHistoryRepository,
    ProductRepository,
    StoreRepository,
    TrackedItemRepository,
)


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


def _initialize_empty_report() -> Dict[str, Any]:
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


def _process_single_result(
    result: Dict[str, Any],
    price_repo: PriceHistoryRepository,
    db: Database,
) -> Dict[str, Any]:
    item_id = result.get("item_id")
    item_details = get_item_details(item_id, db)
    if not item_details:
        return {"error": {"item_id": item_id, "message": "Item not found"}}

    history = price_repo.get_history(item_id)
    if not history:
        return {"error": {"item_id": item_id, "message": "No price history"}}

    current_price = result.get("price")
    target_price = item_details.get("target_price")
    last_price = history[-1].price

    entry = {"item": {**item_details, "current_price": current_price}}
    if target_price is not None and current_price <= target_price:
        entry["deal"] = entry["item"]
    if last_price > current_price:
        entry["drop"] = entry["item"]
    if last_price < current_price:
        entry["increase"] = entry["item"]
    return entry


def generate_report_data(results: List[Dict[str, Any]], db: Database) -> Dict[str, Any]:
    """Generate report data from extraction results."""
    if not results:
        return _initialize_empty_report()

    price_repo = PriceHistoryRepository(db)
    processed = [
        _process_single_result(result, price_repo, db)
        for result in results
    ]

    items = [p["item"] for p in processed if "item" in p]
    deals = [p["deal"] for p in processed if "deal" in p]
    price_drops = [p["drop"] for p in processed if "drop" in p]
    price_increases = [p["increase"] for p in processed if "increase" in p]
    errors = [p["error"] for p in processed if "error" in p]

    return {
        "date": datetime.now().strftime("%B %d, %Y"),
        "total": len(results),
        "success_count": len(items),
        "error_count": len(errors),
        "deals_count": len(deals),
        "deals": deals,
        "price_drops": price_drops,
        "price_increases": price_increases,
        "items": items,
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


# Initialize Jinja2 environment for email templates
template_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "templates", "email"
)
env = Environment(
    loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["html", "xml"])
)


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
    to: str, subject: str, html: str, text: str, config: Dict[str, Any]
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


def send_daily_report(results: List[Dict[str, Any]], db: Database) -> bool:
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
        config=config,
    )
