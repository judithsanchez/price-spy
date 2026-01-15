"""Tests for structured JSON logging."""

import io
import json
import logging
import pytest

from app.utils.logging import get_logger, JSONFormatter


class TestJSONLogger:
    """Tests for JSON structured logging."""

    def test_outputs_valid_json(self):
        """Logger should output valid JSON."""
        stream = io.StringIO()
        logger = get_logger("test", stream=stream)
        logger.info("Test message")

        output = stream.getvalue().strip()
        data = json.loads(output)

        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_includes_logger_name(self):
        """Logger should include logger name."""
        stream = io.StringIO()
        logger = get_logger("my.module", stream=stream)
        logger.info("Hello")

        data = json.loads(stream.getvalue().strip())
        assert data["logger"] == "my.module"

    def test_different_log_levels(self):
        """Logger should handle different log levels."""
        stream = io.StringIO()
        logger = get_logger("test", level=logging.DEBUG, stream=stream)

        logger.debug("Debug message")
        logger.warning("Warning message")
        logger.error("Error message")

        lines = stream.getvalue().strip().split("\n")
        assert len(lines) == 3

        debug_log = json.loads(lines[0])
        warning_log = json.loads(lines[1])
        error_log = json.loads(lines[2])

        assert debug_log["level"] == "DEBUG"
        assert warning_log["level"] == "WARNING"
        assert error_log["level"] == "ERROR"

    def test_includes_extra_context(self):
        """Logger should include extra context fields."""
        stream = io.StringIO()
        logger = get_logger("test", stream=stream)
        logger.info("Price extracted", extra={"url": "https://example.com", "price": 19.99})

        data = json.loads(stream.getvalue().strip())
        assert data["url"] == "https://example.com"
        assert data["price"] == 19.99

    def test_handles_exception_info(self):
        """Logger should include exception info when present."""
        stream = io.StringIO()
        logger = get_logger("test", stream=stream)

        try:
            raise ValueError("Test error")
        except ValueError:
            logger.exception("An error occurred")

        data = json.loads(stream.getvalue().strip())
        assert "exception" in data
        assert "ValueError: Test error" in data["exception"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
