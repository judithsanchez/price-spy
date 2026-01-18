"""Quick script to test email configuration."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def test_email():
    # Read config from environment
    config = {
        "recipient": os.getenv("EMAIL_RECIPIENT"),
        "sender": os.getenv("EMAIL_SENDER"),
        "smtp_host": os.getenv("SMTP_HOST"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_user": os.getenv("SMTP_USER"),
        "smtp_password": os.getenv("SMTP_PASSWORD"),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    }

    # Check required fields
    required = ["recipient", "sender", "smtp_host", "smtp_user", "smtp_password"]
    missing = [k for k in required if not config.get(k)]
    if missing:
        print(f"ERROR: Missing environment variables: {missing}")
        print("\nRequired variables:")
        print("  EMAIL_RECIPIENT - Your email address")
        print("  EMAIL_SENDER - Sender address (can be same as recipient)")
        print("  SMTP_HOST - e.g., smtp.gmail.com")
        print("  SMTP_USER - Your Gmail address")
        print("  SMTP_PASSWORD - Gmail App Password (16 chars)")
        return False

    print(f"Configuration:")
    print(f"  SMTP Host: {config['smtp_host']}:{config['smtp_port']}")
    print(f"  From: {config['sender']}")
    print(f"  To: {config['recipient']}")
    print(f"  TLS: {config['use_tls']}")
    print()

    # Build test email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Price Spy Test Email"
    msg["From"] = config["sender"]
    msg["To"] = config["recipient"]

    text = """
Hello from Price Spy!

This is a test email to verify your email configuration is working.

If you received this, your daily reports will work!

- Price Spy
"""

    html = """
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #2563eb;">Hello from Price Spy!</h2>
    <p>This is a test email to verify your email configuration is working.</p>
    <p style="color: #16a34a; font-weight: bold;">If you received this, your daily reports will work!</p>
    <hr style="margin: 20px 0;">
    <p style="color: #666; font-size: 12px;">- Price Spy</p>
</body>
</html>
"""

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send
    print("Connecting to SMTP server...")
    try:
        with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
            server.set_debuglevel(0)  # Set to 1 for verbose output

            if config["use_tls"]:
                print("Starting TLS...")
                server.starttls()

            print("Logging in...")
            server.login(config["smtp_user"], config["smtp_password"])

            print("Sending email...")
            server.sendmail(config["sender"], config["recipient"], msg.as_string())

        print()
        print("=" * 50)
        print("SUCCESS! Test email sent.")
        print(f"Check your inbox at: {config['recipient']}")
        print("=" * 50)
        return True

    except smtplib.SMTPAuthenticationError as e:
        print()
        print("=" * 50)
        print("AUTHENTICATION ERROR")
        print("=" * 50)
        print(f"Error: {e}")
        print()
        print("For Gmail, make sure you:")
        print("1. Have 2-Factor Authentication enabled")
        print("2. Are using an App Password (not your regular password)")
        print("   Go to: Google Account → Security → App Passwords")
        print("3. The App Password is 16 characters (no spaces)")
        return False

    except smtplib.SMTPException as e:
        print()
        print("=" * 50)
        print("SMTP ERROR")
        print("=" * 50)
        print(f"Error: {e}")
        return False

    except Exception as e:
        print()
        print("=" * 50)
        print("ERROR")
        print("=" * 50)
        print(f"Error: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    test_email()
