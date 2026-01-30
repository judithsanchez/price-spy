"""Structured JSON logging for Price Spy."""

import contextlib
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.error_logger import log_error_to_db


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a LogRecord into a JSON string containing timestamp, level, logger name,
        and message.

        :param record: The logging LogRecord to format.
        :return: A JSON-formatted string representation of the log entry.
        """
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
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

        # Add all extra fields dynamically via dict comprehension
        log_entry.update(
            {
                k: v
                for k, v in record.__dict__.items()
                if k not in standard_attrs and not k.startswith("_")
            }
        )

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Persist to database if requested
        if getattr(record, "persist_to_db", False) or record.levelno >= logging.ERROR:
            with contextlib.suppress(Exception):
                log_error_to_db(
                    error_type=getattr(record, "db_error_type", "application_error"),
                    message=record.getMessage(),
                    url=getattr(record, "url", None),
                    include_stack=bool(record.exc_info),
                )

        return json.dumps(log_entry, default=str)


# Logging utilities providing ExtraFieldsAdapter for merging extra context
# into log records.


class ExtraFieldsAdapter(logging.LoggerAdapter):
    """Adapter that merges extra fields into log records."""

    def process(self, msg, kwargs):
        """
        Merge adapter extra fields with provided kwargs extra and return updated
        message.
        """
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {**self.extra, **extra}  # type: ignore
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
