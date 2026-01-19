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
            "items": [],
            "errors": [],
            "next_run": "Tomorrow 08:00",
        }

    items = []
    deals = []
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

        # Check if it's a deal
        is_deal = (
            status == "success"
            and price is not None
            and target_price is not None
            and price <= target_price
        )

        item_data = {
            "item_id": item_id,
            "product_name": product_name,
            "store_name": store_name,
            "price": price,
            "currency": currency,
            "target_price": target_price,
            "url": url,
            "status": status,
            "is_deal": is_deal,
            "error": error_msg,
        }

        if status == "success":
            items.append(item_data)
            if is_deal:
                deals.append(item_data)
        else:
            errors.append(item_data)

    success_count = len([r for r in results if r.get("status") == "success"])
    error_count = len([r for r in results if r.get("status") == "error"])

    return {
        "date": datetime.now().strftime("%B %d, %Y"),
        "total": len(results),
        "success_count": success_count,
        "error_count": error_count,
        "deals_count": len(deals),
        "deals": deals,
        "items": items,
        "errors": errors,
        "next_run": "Tomorrow 08:00",
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


def render_html_email(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Render HTML email template."""
    dashboard_url = config.get("dashboard_url", "http://localhost:8000")

    # Build deals section
    deals_html = ""
    if report_data["deals"]:
        deals_items = ""
        for deal in report_data["deals"]:
            deals_items += f"""
            <div style="background: #dcfce7; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <div style="font-weight: bold; color: #166534;">{deal['product_name']}</div>
                <div style="color: #15803d; font-size: 14px;">
                    {deal['store_name']} &bull; {deal['currency']} {deal['price']:.2f}
                    <span style="color: #166534;">(target: {deal['currency']} {deal['target_price']:.2f})</span>
                </div>
                {f'<a href="{deal["url"]}" style="color: #16a34a; font-size: 12px;">View Product</a>' if deal.get('url') else ''}
            </div>
            """
        deals_html = f"""
        <div style="margin-bottom: 24px;">
            <h2 style="color: #166534; font-size: 18px; margin-bottom: 12px;">🎉 DEALS FOUND</h2>
            {deals_items}
        </div>
        """

    # Build items table
    items_rows = ""
    for item in report_data["items"]:
        status_badge = ""
        if item["is_deal"]:
            status_badge = '<span style="background: #16a34a; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">DEAL</span>'
        elif item["target_price"]:
            status_badge = '<span style="color: #dc2626;">Above target</span>'
        else:
            status_badge = '<span style="color: #6b7280;">No target</span>'

        items_rows += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{item['product_name']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{item['store_name']}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{item['currency']} {item['price']:.2f}</td>
            <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{status_badge}</td>
        </tr>
        """

    # Build errors section
    errors_html = ""
    if report_data["errors"]:
        error_items = ""
        for err in report_data["errors"]:
            error_items += f"""
            <div style="background: #fef2f2; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                <div style="font-weight: bold; color: #991b1b;">{err['product_name']} ({err['store_name']})</div>
                <div style="color: #dc2626; font-size: 14px;">Error: {err.get('error', 'Unknown error')}</div>
            </div>
            """
        errors_html = f"""
        <div style="margin-bottom: 24px;">
            <h2 style="color: #991b1b; font-size: 18px; margin-bottom: 12px;">⚠️ ERRORS ({report_data['error_count']})</h2>
            {error_items}
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; padding: 20px; margin: 0;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="background: #2563eb; color: white; padding: 24px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">Price Spy Daily Report</h1>
            <div style="opacity: 0.9; margin-top: 4px;">{report_data['date']}</div>
        </div>

        <!-- Content -->
        <div style="padding: 24px;">
            {deals_html}

            <!-- All Items -->
            <div style="margin-bottom: 24px;">
                <h2 style="color: #374151; font-size: 18px; margin-bottom: 12px;">📊 ALL ITEMS CHECKED</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f9fafb;">
                            <th style="padding: 8px; text-align: left; font-size: 12px; color: #6b7280;">Product</th>
                            <th style="padding: 8px; text-align: left; font-size: 12px; color: #6b7280;">Store</th>
                            <th style="padding: 8px; text-align: left; font-size: 12px; color: #6b7280;">Price</th>
                            <th style="padding: 8px; text-align: left; font-size: 12px; color: #6b7280;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_rows}
                    </tbody>
                </table>
            </div>

            {errors_html}

            <!-- Summary -->
            <div style="background: #f9fafb; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
                <h2 style="color: #374151; font-size: 18px; margin-bottom: 12px;">📈 SUMMARY</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 14px;">
                    <div>Items checked: <strong>{report_data['total']}</strong></div>
                    <div>Successful: <strong style="color: #16a34a;">{report_data['success_count']}</strong></div>
                    <div>Errors: <strong style="color: #dc2626;">{report_data['error_count']}</strong></div>
                    <div>Deals found: <strong style="color: #2563eb;">{report_data['deals_count']}</strong></div>
                </div>
                <div style="margin-top: 12px; font-size: 14px; color: #6b7280;">
                    Next check: {report_data['next_run']}
                </div>
            </div>

            <!-- CTA -->
            <div style="text-align: center;">
                <a href="{dashboard_url}" style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                    Open Dashboard
                </a>
            </div>
        </div>

        <!-- Footer -->
        <div style="background: #f9fafb; padding: 16px; text-align: center; font-size: 12px; color: #6b7280;">
            Price Spy - Your Personal Price Tracker
        </div>
    </div>
</body>
</html>
"""
    return html


def render_text_email(report_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Render plain text email template."""
    dashboard_url = config.get("dashboard_url", "http://localhost:8000")

    lines = [
        "PRICE SPY DAILY REPORT",
        report_data['date'],
        "",
    ]

    # Deals section
    if report_data["deals"]:
        lines.append("🎉 DEALS FOUND")
        lines.append("-" * 40)
        for deal in report_data["deals"]:
            lines.append(
                f"* {deal['product_name']} - {deal['store_name']} - "
                f"{deal['currency']} {deal['price']:.2f} (target: {deal['currency']} {deal['target_price']:.2f})"
            )
        lines.append("")

    # All items section
    lines.append("ALL ITEMS CHECKED")
    lines.append("-" * 40)
    for item in report_data["items"]:
        status = "DEAL" if item["is_deal"] else ("Above target" if item["target_price"] else "No target")
        lines.append(
            f"✓ {item['product_name']} ({item['store_name']}): "
            f"{item['currency']} {item['price']:.2f} - {status}"
        )
    for err in report_data["errors"]:
        lines.append(
            f"✗ {err['product_name']} ({err['store_name']}): Error - {err.get('error', 'Unknown')}"
        )
    lines.append("")

    # Errors section
    if report_data["errors"]:
        lines.append("ERRORS")
        lines.append("-" * 40)
        for err in report_data["errors"]:
            lines.append(f"* {err['product_name']}: {err.get('error', 'Unknown error')}")
        lines.append("")

    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(
        f"Items checked: {report_data['total']} | "
        f"Successful: {report_data['success_count']} | "
        f"Errors: {report_data['error_count']} | "
        f"Deals: {report_data['deals_count']}"
    )
    lines.append(f"Next check: {report_data['next_run']}")
    lines.append("")
    lines.append(f"Open dashboard: {dashboard_url}")

    return "\n".join(lines)


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
