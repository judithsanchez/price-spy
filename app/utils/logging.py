"""Structured JSON logging for Price Spy."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "url"):
            log_entry["url"] = record.url
        if hasattr(record, "price"):
            log_entry["price"] = record.price
        if hasattr(record, "error_type"):
            log_entry["error_type"] = record.error_type

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class ExtraFieldsAdapter(logging.LoggerAdapter):
    """Adapter that merges extra fields into log records."""

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {**self.extra, **extra}
        return msg, kwargs


def get_logger(
    name: str,
    level: int = logging.INFO,
    stream: Any = None
) -> logging.Logger:
    """
    Create a JSON-formatted logger.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        stream: Output stream (default: stderr)

    Returns:
        Configured logger instance
    """
    if stream is None:
        stream = sys.stderr

    logger = logging.getLogger(name)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger
