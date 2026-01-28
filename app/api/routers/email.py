from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.email_report import get_email_config, is_email_configured, send_email

router = APIRouter(prefix="/api/email", tags=["Email"])


class EmailTestResponse(BaseModel):
    """Response for email test endpoint."""

    success: bool
    message: str
    recipient: Optional[str] = None


class EmailStatusResponse(BaseModel):
    """Response for email status endpoint."""

    enabled: bool
    configured: bool
    recipient: Optional[str] = None


@router.get("/status", response_model=EmailStatusResponse)
async def email_status():
    """Get email configuration status."""
    config = get_email_config()
    return EmailStatusResponse(
        enabled=config["enabled"],
        configured=is_email_configured(),
        recipient=config.get("recipient"),
    )


@router.post("/test", response_model=EmailTestResponse)
async def email_test():
    """Send a test email to verify configuration."""
    if not is_email_configured():
        return EmailTestResponse(
            success=False,
            message=(
                "Email not configured. Set EMAIL_ENABLED=true "
                "and configure SMTP settings."
            ),
        )

    config = get_email_config()

    # Build test email content
    html = """
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #2563eb;">Price Spy Test Email</h2>
        <p>This is a test email to verify your email configuration is working.</p>
        <p style="color: #16a34a; font-weight: bold;">
            If you received this, your daily reports will work!
        </p>
        <hr style="margin: 20px 0;">
        <p style="color: #666; font-size: 12px;">- Price Spy</p>
    </body>
    </html>
    """

    text = """
Price Spy Test Email

This is a test email to verify your email configuration is working.
If you received this, your daily reports will work!

- Price Spy
"""

    success = send_email(
        to=config["recipient"],
        subject="Price Spy Test Email",
        html=html,
        text=text,
        config=config,
    )

    if success:
        return EmailTestResponse(
            success=True,
            message="Test email sent successfully!",
            recipient=config["recipient"],
        )
    else:
        return EmailTestResponse(
            success=False,
            message="Failed to send email. Check SMTP settings and credentials.",
        )
