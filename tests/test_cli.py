"""Tests for the CLI entry point."""

import subprocess
import sys
import pytest


def test_cli_with_no_args_shows_usage():
    """CLI should show usage when no URL is provided."""
    result = subprocess.run(
        [sys.executable, "spy.py"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "usage" in result.stderr.lower() or "url" in result.stderr.lower()


def test_cli_with_invalid_url_shows_error():
    """CLI should show error for invalid URL."""
    result = subprocess.run(
        [sys.executable, "spy.py", "not-a-url"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
