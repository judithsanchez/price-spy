"""Service for standardized error logging to the database."""

import traceback
from typing import Optional
from app.storage.database import Database
from app.storage.repositories import ErrorLogRepository
from app.models.schemas import ErrorRecord
from app.core.config import settings


def log_error_to_db(
    error_type: str,
    message: str,
    url: Optional[str] = None,
    screenshot_path: Optional[str] = None,
    include_stack: bool = True,
):
    """
    Persist an error record to the database.

    This utility uses its own DB connection to ensure it can log errors
    even when the primary request connection is failing.
    """
    db = Database(settings.DATABASE_PATH)
    try:
        db.initialize()
        repo = ErrorLogRepository(db)

        stack_trace = traceback.format_exc() if include_stack else None

        record = ErrorRecord(
            error_type=error_type,
            message=message[:2000],
            url=url,
            screenshot_path=screenshot_path,
            stack_trace=stack_trace,
        )

        repo.insert(record)
    except Exception as e:
        # Fail-safe: if DB logging fails, at least print to stderr
        import sys

        print(f"CRITICAL: Failed to persist error to DB: {e}", file=sys.stderr)
    finally:
        db.close()
