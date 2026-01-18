# Slice 8: Daily Email Report

**STATUS: PLANNING**

## Overview

**Objective:** Send a daily email after the scheduled extraction completes, summarizing what was checked and the results.

**Success Criteria:**

- [ ] Email sent after each scheduler run
- [ ] Email includes all items checked with prices
- [ ] Deals highlighted prominently
- [ ] Errors listed for troubleshooting
- [ ] Configurable recipient and SMTP settings
- [ ] Email skipped if no items were checked
- [ ] All tests pass

---

## Email Content

### Subject Line

```
Price Spy Daily Report - 2 Deals Found! (5 items checked)
```

Or if no deals:
```
Price Spy Daily Report - 5 items checked
```

Or if errors:
```
Price Spy Daily Report - 3 items checked, 2 errors
```

### Email Body (HTML)

```
┌─────────────────────────────────────────────────────────────────┐
│  PRICE SPY DAILY REPORT                                         │
│  January 18, 2026                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🎉 DEALS FOUND                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  Eucerin Urea Repair                                            │
│  Amazon.nl • EUR 14.99 (target: EUR 15.00)                      │
│  [View Product]                                                 │
│                                                                 │
│  Coca-Cola Zero 12-pack                                         │
│  Bol.com • EUR 7.49 (target: EUR 7.50)                          │
│  [View Product]                                                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 ALL ITEMS CHECKED                                           │
│  ─────────────────────────────────────────────────────────────  │
│  Product              │ Store     │ Price    │ Status           │
│  ─────────────────────│───────────│──────────│─────────────────│
│  Eucerin Urea Repair  │ Amazon.nl │ EUR 14.99│ ✓ DEAL          │
│  Coca-Cola Zero       │ Bol.com   │ EUR 7.49 │ ✓ DEAL          │
│  Kitchen Gadget       │ Amazon.nl │ EUR 29.99│ Above target    │
│  Shower Gel           │ Bol.com   │ EUR 3.99 │ No target set   │
│  Light Strip          │ Amazon.nl │ -        │ ✗ Error         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚠️ ERRORS (1)                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  Light Strip (Amazon.nl)                                        │
│  Error: Page timeout after 30 seconds                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📈 SUMMARY                                                     │
│  ─────────────────────────────────────────────────────────────  │
│  Items checked: 5                                               │
│  Successful: 4                                                  │
│  Errors: 1                                                      │
│  Deals found: 2                                                 │
│  Next check: Tomorrow 08:00                                     │
│                                                                 │
│  [Open Dashboard]                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Plain Text Version

For email clients that don't support HTML:

```
PRICE SPY DAILY REPORT
January 18, 2026

🎉 DEALS FOUND
--------------
* Eucerin Urea Repair - Amazon.nl - EUR 14.99 (target: EUR 15.00)
* Coca-Cola Zero 12-pack - Bol.com - EUR 7.49 (target: EUR 7.50)

ALL ITEMS CHECKED
-----------------
✓ Eucerin Urea Repair (Amazon.nl): EUR 14.99 - DEAL
✓ Coca-Cola Zero (Bol.com): EUR 7.49 - DEAL
✓ Kitchen Gadget (Amazon.nl): EUR 29.99 - Above target
✓ Shower Gel (Bol.com): EUR 3.99 - No target
✗ Light Strip (Amazon.nl): Error - Page timeout

ERRORS
------
* Light Strip: Page timeout after 30 seconds

SUMMARY
-------
Items checked: 5 | Successful: 4 | Errors: 1 | Deals: 2
Next check: Tomorrow 08:00

Open dashboard: http://localhost:8000
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_ENABLED` | No | `false` | Enable/disable email reports |
| `EMAIL_RECIPIENT` | Yes* | - | Email address to send reports to |
| `EMAIL_SENDER` | Yes* | - | Sender email address (from) |
| `SMTP_HOST` | Yes* | - | SMTP server hostname |
| `SMTP_PORT` | No | `587` | SMTP server port |
| `SMTP_USER` | Yes* | - | SMTP username (usually email) |
| `SMTP_PASSWORD` | Yes* | - | SMTP password or app password |
| `SMTP_USE_TLS` | No | `true` | Use TLS encryption |
| `EMAIL_DASHBOARD_URL` | No | `http://localhost:8000` | URL for dashboard links in email |

*Required only if `EMAIL_ENABLED=true`

### Example Configuration

```bash
# .env file

# Email settings
EMAIL_ENABLED=true
EMAIL_RECIPIENT=judith@example.com
EMAIL_SENDER=pricespy@example.com

# Gmail SMTP (use App Password, not regular password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yourname@gmail.com
SMTP_PASSWORD=abcd-efgh-ijkl-mnop

# For links in email
EMAIL_DASHBOARD_URL=http://192.168.1.100:8000
```

### Gmail Setup

1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account → Security → App Passwords
3. Generate a new app password for "Mail"
4. Use that 16-character password as `SMTP_PASSWORD`

### Other Email Providers

**Outlook/Hotmail:**
```
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

**SendGrid:**
```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

---

## Implementation

### New Files

```
app/
├── core/
│   └── email_report.py    # Email generation and sending
├── templates/
│   └── email/
│       ├── daily_report.html    # HTML email template
│       └── daily_report.txt     # Plain text template
tests/
└── test_email_report.py
```

### Email Report Module

```python
# app/core/email_report.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def get_email_config() -> Dict[str, Any]:
    """Get email configuration from environment."""
    return {
        "enabled": os.getenv("EMAIL_ENABLED", "false").lower() == "true",
        "recipient": os.getenv("EMAIL_RECIPIENT"),
        "sender": os.getenv("EMAIL_SENDER"),
        "smtp_host": os.getenv("SMTP_HOST"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_user": os.getenv("SMTP_USER"),
        "smtp_password": os.getenv("SMTP_PASSWORD"),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        "dashboard_url": os.getenv("EMAIL_DASHBOARD_URL", "http://localhost:8000"),
    }

def is_email_configured() -> bool:
    """Check if email is properly configured."""
    config = get_email_config()
    if not config["enabled"]:
        return False
    required = ["recipient", "sender", "smtp_host", "smtp_user", "smtp_password"]
    return all(config.get(key) for key in required)

def generate_report_data(
    results: List[Dict[str, Any]],
    db
) -> Dict[str, Any]:
    """Generate report data from extraction results."""
    # Get product/store info for each result
    # Calculate deals, errors, etc.
    ...

def send_daily_report(
    results: List[Dict[str, Any]],
    db
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
            if config["use_tls"]:
                server.starttls()
            server.login(config["smtp_user"], config["smtp_password"])
            server.sendmail(config["sender"], to, msg.as_string())
        return True
    except Exception as e:
        # Log error
        return False
```

### Integration with Scheduler

```python
# app/core/scheduler.py (modified)

async def run_scheduled_extraction():
    """Run the scheduled extraction job."""
    # ... existing code ...

    results = await process_extraction_queue(items, db)

    # ... existing code ...

    # Send email report after extraction completes
    from app.core.email_report import send_daily_report
    send_daily_report(results, db)

    return _last_run_result
```

---

## Database Changes

### Add email_logs table (optional, for tracking)

```sql
CREATE TABLE IF NOT EXISTS email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_at TEXT NOT NULL DEFAULT (datetime('now')),
    recipient TEXT NOT NULL,
    subject TEXT NOT NULL,
    items_count INTEGER NOT NULL,
    deals_count INTEGER NOT NULL,
    errors_count INTEGER NOT NULL,
    success INTEGER NOT NULL DEFAULT 1,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_email_logs_sent_at ON email_logs(sent_at);
```

---

## Test Plan

### Unit Tests

```python
# tests/test_email_report.py

class TestEmailConfig:
    def test_email_disabled_by_default(self):
        """Email should be disabled when not configured."""

    def test_email_config_from_env(self):
        """Should read config from environment variables."""

    def test_is_configured_requires_all_fields(self):
        """Should return False if any required field missing."""

class TestReportGeneration:
    def test_generate_report_with_deals(self):
        """Report should highlight deals."""

    def test_generate_report_with_errors(self):
        """Report should include error details."""

    def test_generate_report_empty_results(self):
        """Report should handle empty results."""

    def test_subject_includes_deal_count(self):
        """Subject should mention deals when found."""

    def test_subject_includes_error_count(self):
        """Subject should mention errors when present."""

class TestEmailSending:
    def test_send_email_success(self):
        """Should send email via SMTP."""

    def test_send_email_handles_smtp_error(self):
        """Should handle SMTP failures gracefully."""

    def test_skip_email_when_disabled(self):
        """Should not send when EMAIL_ENABLED=false."""

    def test_skip_email_when_no_items(self):
        """Should not send when no items were checked."""

class TestEmailTemplates:
    def test_html_template_renders(self):
        """HTML template should render without errors."""

    def test_text_template_renders(self):
        """Text template should render without errors."""

    def test_template_includes_all_items(self):
        """Template should include all checked items."""

    def test_template_highlights_deals(self):
        """Template should prominently show deals."""
```

### Integration Tests

```python
class TestSchedulerEmailIntegration:
    def test_email_sent_after_scheduler_run(self):
        """Email should be sent after successful scheduler run."""

    def test_no_email_when_scheduler_finds_no_items(self):
        """No email when all items already checked today."""
```

---

## Implementation Order

### Phase 1: Core Email Functionality
1. [ ] Create email configuration module
2. [ ] Implement SMTP sending function
3. [ ] Create HTML email template
4. [ ] Create plain text email template
5. [ ] Write unit tests

### Phase 2: Report Generation
1. [ ] Implement report data generation
2. [ ] Build subject line generator
3. [ ] Add deal highlighting logic
4. [ ] Add error section
5. [ ] Write unit tests

### Phase 3: Scheduler Integration
1. [ ] Add email_logs table (optional)
2. [ ] Integrate with scheduler
3. [ ] Add email status to scheduler API response
4. [ ] Write integration tests

### Phase 4: Documentation
1. [ ] Add email config to README
2. [ ] Document Gmail/provider setup
3. [ ] Add troubleshooting guide

---

## API Changes

### Scheduler Status Response (Extended)

```json
{
  "running": true,
  "next_run": "2026-01-19T08:00:00",
  "last_run": {
    "status": "completed",
    "items_total": 5,
    "items_success": 4,
    "items_failed": 1,
    "email_sent": true
  },
  "email_enabled": true,
  "email_recipient": "judith@example.com"
}
```

### New Endpoint: Test Email

```
POST /api/email/test
```

Sends a test email to verify configuration. Returns:
```json
{
  "success": true,
  "message": "Test email sent to judith@example.com"
}
```

Or on failure:
```json
{
  "success": false,
  "error": "SMTP authentication failed"
}
```

---

## Security Considerations

1. **SMTP password in environment** - Never commit to git
2. **App passwords** - Use app-specific passwords, not main password
3. **TLS required** - Always use TLS for SMTP connections
4. **No sensitive data in email** - Don't include full URLs with auth tokens

---

## Files to Modify

| File | Changes |
|------|---------|
| `app/core/scheduler.py` | Call send_daily_report after extraction |
| `app/api/main.py` | Add /api/email/test endpoint (optional) |
| `app/storage/database.py` | Add email_logs table (optional) |
| `requirements.txt` | No new dependencies (uses stdlib) |
| `README.md` | Add email configuration section |
| `.env.example` | Add email environment variables |

---

## Definition of Done

Slice 8 is complete when:

- [ ] Email sent after each scheduler run with results
- [ ] Deals prominently highlighted in email
- [ ] Errors listed with details
- [ ] Both HTML and plain text versions work
- [ ] Email skipped when no items checked
- [ ] Configuration via environment variables
- [ ] Gmail setup documented
- [ ] Test email endpoint works
- [ ] All tests pass
- [ ] Documentation updated

---

## Example .env.example

```bash
# Email Configuration (optional)
# Set EMAIL_ENABLED=true and configure SMTP to receive daily reports

EMAIL_ENABLED=false
EMAIL_RECIPIENT=you@example.com
EMAIL_SENDER=pricespy@example.com

# Gmail SMTP (recommended)
# 1. Enable 2FA on your Google account
# 2. Generate App Password: Google Account → Security → App Passwords
# 3. Use the 16-character app password below
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yourname@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
SMTP_USE_TLS=true

# URL for links in email (your Pi's IP or domain)
EMAIL_DASHBOARD_URL=http://localhost:8000
```

---

**Status: PLANNING** (January 2026)
