import sys
from datetime import datetime
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.email_report import (
    build_subject,
    get_email_config,
    render_html_email,
    render_text_email,
    send_email,
)


def send_mock_email():
    config = get_email_config()

    if not config["enabled"] or not config["recipient"]:
        print("Error: Email not enabled or recipient not set in .env")
        return

    # Mock Report Data
    report_data = {
        "date": datetime.now().strftime("%B %d, %Y"),
        "total": 5,
        "success_count": 4,
        "error_count": 1,
        "deals_count": 1,
        "deals": [
            {
                "product_name": "Premium Coffee Beans 1kg",
                "store_name": "Amazon",
                "price": 14.99,
                "prev_price": 19.99,
                "price_change": -5.00,
                "price_change_pct": -25.0,
                "currency": "EUR",
                "target_price": 15.00,
                "url": "https://amazon.com/coffee",
                "is_deal": True,
            }
        ],
        "price_drops": [
            {
                "product_name": "Premium Coffee Beans 1kg",
                "store_name": "Amazon",
                "price": 14.99,
                "prev_price": 19.99,
                "price_change": -5.00,
                "price_change_pct": -25.0,
                "currency": "EUR",
            },
            {
                "product_name": "Oat Milk 6-pack",
                "store_name": "Albert Heijn",
                "price": 10.50,
                "prev_price": 11.20,
                "price_change": -0.70,
                "price_change_pct": -6.25,
                "currency": "EUR",
            },
        ],
        "price_increases": [
            {
                "product_name": "Extra Virgin Olive Oil 500ml",
                "store_name": "Jumbo",
                "price": 8.95,
                "prev_price": 7.50,
                "price_change": 1.45,
                "price_change_pct": 19.3,
                "currency": "EUR",
            }
        ],
        "all_items": [
            {
                "product_name": "Premium Coffee Beans 1kg",
                "store_name": "Amazon",
                "price": 14.99,
                "price_change_pct": -25.0,
                "currency": "EUR",
                "is_deal": True,
                "target_price": 15.00,
            },
            {
                "product_name": "Oat Milk 6-pack",
                "store_name": "Albert Heijn",
                "price": 10.50,
                "price_change_pct": -6.25,
                "currency": "EUR",
                "is_deal": False,
                "target_price": 9.00,
            },
            {
                "product_name": "Extra Virgin Olive Oil 500ml",
                "store_name": "Jumbo",
                "price": 8.95,
                "price_change_pct": 19.3,
                "currency": "EUR",
                "is_deal": False,
                "target_price": 7.00,
            },
            {
                "product_name": "Basmati Rice 5kg",
                "store_name": "Lidl",
                "price": 12.00,
                "price_change_pct": 0.0,
                "currency": "EUR",
                "is_deal": False,
                "target_price": None,
            },
        ],
        "errors": [
            {
                "product_name": "Greek Yogurt 1kg",
                "store_name": "Plus",
                "error": "Timeout while waiting for selector",
            }
        ],
        "next_run": "Tomorrow 23:00",
    }

    # Generate content
    html_content = render_html_email(report_data, config)
    text_content = render_text_email(report_data, config)
    subject = build_subject(report_data) + " (TEST MOCK)"

    print(f"Sending test email to {config['recipient']}...")
    success = send_email(
        to=config["recipient"],
        subject=subject,
        html=html_content,
        text=text_content,
        config=config,
    )

    if success:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email.")


if __name__ == "__main__":
    send_mock_email()
