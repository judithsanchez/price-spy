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

        # Standard LogRecord attributes to ignore
        standard_attrs = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "persist_to_db",
            "db_error_type",
        }

        # Add all extra fields dynamically
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_entry[key] = value

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Persist to database if requested
        if getattr(record, "persist_to_db", False) or record.levelno >= logging.ERROR:
            try:
                from app.core.error_logger import log_error_to_db

                log_error_to_db(
                    error_type=getattr(record, "db_error_type", "application_error"),
                    message=record.getMessage(),
                    url=getattr(record, "url", None),
                    include_stack=bool(record.exc_info),
                )
            except Exception:
                # Prevent recursion or crash if error logger fails
                pass

        return json.dumps(log_entry, default=str)


class ExtraFieldsAdapter(logging.LoggerAdapter):
    """Adapter that merges extra fields into log records."""

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {**self.extra, **extra}
        return msg, kwargs


def get_logger(
    name: str, level: int = logging.INFO, stream: Any = None
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
