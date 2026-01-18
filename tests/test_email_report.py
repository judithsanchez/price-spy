"""Tests for daily email report."""

import pytest
from unittest.mock import patch, MagicMock
import os


class TestEmailConfig:
    """Tests for email configuration."""

    def test_email_disabled_by_default(self):
        """Email should be disabled when not configured."""
        from app.core.email_report import get_email_config

        with patch.dict(os.environ, {}, clear=True):
            config = get_email_config()

        assert config["enabled"] is False

    def test_email_config_from_env(self):
        """Should read config from environment variables."""
        from app.core.email_report import get_email_config

        with patch.dict(os.environ, {
            "EMAIL_ENABLED": "true",
            "EMAIL_RECIPIENT": "test@example.com",
            "EMAIL_SENDER": "sender@example.com",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "465",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret123",
            "SMTP_USE_TLS": "false",
            "EMAIL_DASHBOARD_URL": "http://mypi:8000",
        }):
            config = get_email_config()

        assert config["enabled"] is True
        assert config["recipient"] == "test@example.com"
        assert config["sender"] == "sender@example.com"
        assert config["smtp_host"] == "smtp.example.com"
        assert config["smtp_port"] == 465
        assert config["smtp_user"] == "user@example.com"
        assert config["smtp_password"] == "secret123"
        assert config["use_tls"] is False
        assert config["dashboard_url"] == "http://mypi:8000"

    def test_is_configured_requires_all_fields(self):
        """Should return False if any required field missing."""
        from app.core.email_report import is_email_configured

        # Missing password
        with patch.dict(os.environ, {
            "EMAIL_ENABLED": "true",
            "EMAIL_RECIPIENT": "test@example.com",
            "EMAIL_SENDER": "sender@example.com",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_USER": "user@example.com",
            # No SMTP_PASSWORD
        }, clear=True):
            assert is_email_configured() is False

    def test_is_configured_returns_true_when_complete(self):
        """Should return True when all required fields present."""
        from app.core.email_report import is_email_configured

        with patch.dict(os.environ, {
            "EMAIL_ENABLED": "true",
            "EMAIL_RECIPIENT": "test@example.com",
            "EMAIL_SENDER": "sender@example.com",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret123",
        }, clear=True):
            assert is_email_configured() is True


class TestReportGeneration:
    """Tests for report data generation."""

    def test_generate_report_data_with_results(self):
        """Should generate report data from extraction results."""
        from app.core.email_report import generate_report_data

        results = [
            {"item_id": 1, "status": "success", "price": 14.99, "currency": "EUR"},
            {"item_id": 2, "status": "success", "price": 7.49, "currency": "EUR"},
            {"item_id": 3, "status": "error", "error": "Timeout"},
        ]

        # Mock get_item_details to avoid database calls
        with patch('app.core.email_report.get_item_details') as mock_details:
            mock_details.return_value = {
                "product_name": "Test Product",
                "store_name": "Test Store",
                "target_price": None,
                "url": "http://example.com",
            }
            report = generate_report_data(results, MagicMock())

        assert report["total"] == 3
        assert report["success_count"] == 2
        assert report["error_count"] == 1

    def test_generate_report_data_identifies_deals(self):
        """Should identify deals based on target price."""
        from app.core.email_report import generate_report_data

        results = [
            {"item_id": 1, "status": "success", "price": 14.99, "currency": "EUR"},
        ]

        mock_db = MagicMock()

        # Mock getting product with target price
        with patch('app.core.email_report.get_item_details') as mock_details:
            mock_details.return_value = {
                "product_name": "Test Product",
                "store_name": "Amazon",
                "target_price": 15.00,
                "url": "http://example.com",
            }
            report = generate_report_data(results, mock_db)

        assert report["deals_count"] == 1
        assert len(report["deals"]) == 1

    def test_generate_report_empty_results(self):
        """Should handle empty results."""
        from app.core.email_report import generate_report_data

        report = generate_report_data([], MagicMock())

        assert report["total"] == 0
        assert report["success_count"] == 0
        assert report["error_count"] == 0
        assert report["deals_count"] == 0


class TestSubjectGeneration:
    """Tests for email subject line."""

    def test_subject_with_deals(self):
        """Subject should mention deals when found."""
        from app.core.email_report import build_subject

        report_data = {
            "total": 5,
            "success_count": 5,
            "error_count": 0,
            "deals_count": 2,
        }

        subject = build_subject(report_data)

        assert "2 Deals" in subject
        assert "5 items" in subject

    def test_subject_with_errors(self):
        """Subject should mention errors when present."""
        from app.core.email_report import build_subject

        report_data = {
            "total": 5,
            "success_count": 3,
            "error_count": 2,
            "deals_count": 0,
        }

        subject = build_subject(report_data)

        assert "2 errors" in subject

    def test_subject_no_deals_no_errors(self):
        """Subject should be simple when no deals or errors."""
        from app.core.email_report import build_subject

        report_data = {
            "total": 5,
            "success_count": 5,
            "error_count": 0,
            "deals_count": 0,
        }

        subject = build_subject(report_data)

        assert "5 items checked" in subject
        assert "Deal" not in subject


class TestEmailSending:
    """Tests for email sending."""

    def test_send_email_calls_smtp(self):
        """Should send email via SMTP."""
        from app.core.email_report import send_email

        config = {
            "sender": "sender@example.com",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "user@example.com",
            "smtp_password": "secret",
            "use_tls": True,
        }

        with patch('app.core.email_report.smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            result = send_email(
                to="recipient@example.com",
                subject="Test",
                html="<p>Test</p>",
                text="Test",
                config=config
            )

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    def test_send_email_handles_smtp_error(self):
        """Should handle SMTP failures gracefully."""
        from app.core.email_report import send_email
        import smtplib

        config = {
            "sender": "sender@example.com",
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "user@example.com",
            "smtp_password": "secret",
            "use_tls": True,
        }

        with patch('app.core.email_report.smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__enter__ = MagicMock(
                side_effect=smtplib.SMTPAuthenticationError(535, b"Auth failed")
            )
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

            result = send_email(
                to="recipient@example.com",
                subject="Test",
                html="<p>Test</p>",
                text="Test",
                config=config
            )

        assert result is False

    def test_skip_report_when_disabled(self):
        """Should not send when EMAIL_ENABLED=false."""
        from app.core.email_report import send_daily_report

        with patch.dict(os.environ, {"EMAIL_ENABLED": "false"}, clear=True):
            with patch('app.core.email_report.send_email') as mock_send:
                result = send_daily_report([], MagicMock())

        mock_send.assert_not_called()
        assert result is False

    def test_skip_report_when_no_items(self):
        """Should not send when no items were checked."""
        from app.core.email_report import send_daily_report

        with patch.dict(os.environ, {
            "EMAIL_ENABLED": "true",
            "EMAIL_RECIPIENT": "test@example.com",
            "EMAIL_SENDER": "sender@example.com",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "secret",
        }, clear=True):
            with patch('app.core.email_report.send_email') as mock_send:
                result = send_daily_report([], MagicMock())

        mock_send.assert_not_called()
        assert result is False


class TestEmailTemplates:
    """Tests for email template rendering."""

    def test_render_html_email(self):
        """HTML template should render without errors."""
        from app.core.email_report import render_html_email

        report_data = {
            "date": "January 18, 2026",
            "total": 3,
            "success_count": 2,
            "error_count": 1,
            "deals_count": 1,
            "deals": [{
                "product_name": "Test Product",
                "store_name": "Amazon",
                "price": 14.99,
                "currency": "EUR",
                "target_price": 15.00,
                "url": "http://example.com",
            }],
            "items": [
                {"product_name": "Test Product", "store_name": "Amazon", "price": 14.99, "currency": "EUR", "status": "success", "is_deal": True, "target_price": 15.00},
                {"product_name": "Other Product", "store_name": "Bol", "price": 29.99, "currency": "EUR", "status": "success", "is_deal": False, "target_price": 25.00},
            ],
            "errors": [
                {"product_name": "Failed Product", "store_name": "Amazon", "error": "Timeout"},
            ],
            "next_run": "Tomorrow 08:00",
        }

        config = {"dashboard_url": "http://localhost:8000"}

        html = render_html_email(report_data, config)

        assert "Test Product" in html
        assert "14.99" in html
        assert "DEAL" in html.upper() or "Deal" in html

    def test_render_text_email(self):
        """Text template should render without errors."""
        from app.core.email_report import render_text_email

        report_data = {
            "date": "January 18, 2026",
            "total": 2,
            "success_count": 2,
            "error_count": 0,
            "deals_count": 1,
            "deals": [{
                "product_name": "Test Product",
                "store_name": "Amazon",
                "price": 14.99,
                "currency": "EUR",
                "target_price": 15.00,
            }],
            "items": [
                {"product_name": "Test Product", "store_name": "Amazon", "price": 14.99, "currency": "EUR", "status": "success", "is_deal": True},
            ],
            "errors": [],
            "next_run": "Tomorrow 08:00",
        }

        config = {"dashboard_url": "http://localhost:8000"}

        text = render_text_email(report_data, config)

        assert "Test Product" in text
        assert "14.99" in text
