"""Repository classes for database operations."""

from datetime import datetime
from typing import List, Optional

from app.storage.database import Database
from app.models.schemas import PriceHistoryRecord, ErrorRecord


class PriceHistoryRepository:
    """Repository for price history operations."""

    def __init__(self, db: Database):
        self.db = db

    def insert(self, record: PriceHistoryRecord) -> int:
        """Insert a price history record and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO price_history
            (product_name, price, currency, confidence, url, store_name, page_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.product_name,
                record.price,
                record.currency,
                record.confidence,
                record.url,
                record.store_name,
                record.page_type,
            )
        )
        self.db.commit()
        return cursor.lastrowid

    def get_by_id(self, record_id: int) -> Optional[PriceHistoryRecord]:
        """Get a price history record by ID."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE id = ?",
            (record_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_url(self, url: str) -> List[PriceHistoryRecord]:
        """Get all price history records for a URL."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE url = ? ORDER BY created_at DESC",
            (url,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_latest_by_url(self, url: str) -> Optional[PriceHistoryRecord]:
        """Get the most recent price history record for a URL."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE url = ? ORDER BY created_at DESC, id DESC LIMIT 1",
            (url,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def _row_to_record(self, row) -> PriceHistoryRecord:
        """Convert a database row to a PriceHistoryRecord."""
        return PriceHistoryRecord(
            id=row["id"],
            product_name=row["product_name"],
            price=row["price"],
            currency=row["currency"],
            confidence=row["confidence"],
            url=row["url"],
            store_name=row["store_name"],
            page_type=row["page_type"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class ErrorLogRepository:
    """Repository for error log operations."""

    def __init__(self, db: Database):
        self.db = db

    def insert(self, error: ErrorRecord) -> int:
        """Insert an error record and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO error_log
            (error_type, message, url, screenshot_path, stack_trace)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                error.error_type,
                error.message,
                error.url,
                error.screenshot_path,
                error.stack_trace,
            )
        )
        self.db.commit()
        return cursor.lastrowid

    def get_recent(self, limit: int = 10) -> List[ErrorRecord]:
        """Get recent error records."""
        cursor = self.db.execute(
            "SELECT * FROM error_log ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def _row_to_record(self, row) -> ErrorRecord:
        """Convert a database row to an ErrorRecord."""
        return ErrorRecord(
            id=row["id"],
            error_type=row["error_type"],
            message=row["message"],
            url=row["url"],
            screenshot_path=row["screenshot_path"],
            stack_trace=row["stack_trace"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
