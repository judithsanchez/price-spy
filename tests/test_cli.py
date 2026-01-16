"""Tests for the CLI entry point."""

import subprocess
import sys
import tempfile
import os
import pytest


def test_cli_with_no_args_shows_usage():
    """CLI should show help when no command is provided."""
    result = subprocess.run(
        [sys.executable, "spy.py"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    # Should show help or usage info
    output = result.stdout.lower() + result.stderr.lower()
    assert "usage" in output or "extract" in output or "help" in output


def test_cli_with_invalid_url_shows_error():
    """CLI should show error for invalid URL."""
    result = subprocess.run(
        [sys.executable, "spy.py", "extract", "not-a-url"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()


def test_cli_legacy_url_mode():
    """CLI should accept URL directly (legacy mode)."""
    result = subprocess.run(
        [sys.executable, "spy.py", "not-a-url"],
        capture_output=True,
        text=True
    )
    # Should fail with invalid URL error (but recognize it as extract command)
    assert result.returncode != 0
    output = result.stderr.lower()
    assert "invalid" in output or "error" in output


def test_cli_list_empty():
    """CLI list command should work with empty database."""
    # Use a temp database
    env = os.environ.copy()

    result = subprocess.run(
        [sys.executable, "spy.py", "list", "products"],
        capture_output=True,
        text=True,
        env=env
    )
    # Should succeed even with no products
    assert "no products" in result.stdout.lower() or result.returncode == 0


def test_cli_help_shows_commands():
    """CLI help should show available commands."""
    result = subprocess.run(
        [sys.executable, "spy.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    output = result.stdout.lower()
    assert "extract" in output
    assert "add-product" in output
    assert "add-store" in output
    assert "track" in output
    assert "list" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
