"""Repository classes for database operations."""

import logging
from datetime import datetime
from typing import Any

from app.models.schemas import (
    Category,
    ErrorRecord,
    ExtractionLog,
    Label,
    PriceHistoryRecord,
    Product,
    PurchaseType,
    Store,
    TrackedItem,
    Unit,
)
from app.storage.database import Database

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base class for all repositories."""

    def __init__(self, db: Database):
        """Initialize repository."""
        self.db = db


class PriceHistoryRepository(BaseRepository):
    """Repository for price history operations."""

    def insert(self, record: PriceHistoryRecord) -> int:
        """Insert a price history record and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO price_history (
                item_id,
                product_name,
                price,
                currency,
                is_available,
                is_size_matched,
                confidence,
                url,
                store_name,
                page_type,
                notes,
                original_price,
                deal_type,
                discount_percentage,
                discount_fixed_amount,
                deal_description,
                available_sizes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.item_id,
                record.product_name,
                record.price,
                record.currency,
                1 if record.is_available else 0,
                1 if record.is_size_matched else 0,
                record.confidence,
                record.url,
                record.store_name,
                record.page_type,
                record.notes,
                record.original_price,
                record.deal_type,
                record.discount_percentage,
                record.discount_fixed_amount,
                record.deal_description,
                record.available_sizes,
            ),
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_by_id(self, record_id: int) -> PriceHistoryRecord | None:
        """Get a price history record by ID."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE id = ?", (record_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_url(self, url: str) -> list[PriceHistoryRecord]:
        """Get all price history records for a URL."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE url = ? ORDER BY created_at DESC", (url,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_latest_by_url(self, url: str) -> PriceHistoryRecord | None:
        """Get the most recent price history record for a URL."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE url = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 1",
            (url,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_recent_history_by_url(
        self,
        url: str,
        limit: int = 30,
    ) -> list[PriceHistoryRecord]:
        """Get the recent price history records for a URL."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE url = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (url, limit),
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_by_item(self, item_id: int) -> list[PriceHistoryRecord]:
        """Get all price history records for a tracked item."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE item_id = ? ORDER BY created_at DESC",
            (item_id,),
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_history_since(self, url: str, since: datetime) -> list[PriceHistoryRecord]:
        """Get price history records for a URL since a specific date."""
        cursor = self.db.execute(
            "SELECT * FROM price_history WHERE url = ? "
            "AND created_at >= ? "
            "ORDER BY created_at DESC",
            (url, since.isoformat()),
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_record(row) -> PriceHistoryRecord:
        """Convert a database row to a PriceHistoryRecord."""
        return PriceHistoryRecord(
            id=row["id"],
            item_id=row["item_id"],
            product_name=row["product_name"],
            price=row["price"],
            currency=row["currency"],
            is_available=bool(row["is_available"]),
            is_size_matched=bool(row["is_size_matched"]),
            confidence=row["confidence"],
            url=row["url"],
            store_name=row["store_name"],
            page_type=row["page_type"],
            notes=row["notes"],
            original_price=row["original_price"],
            deal_type=row["deal_type"],
            discount_percentage=row["discount_percentage"],
            discount_fixed_amount=row["discount_fixed_amount"],
            deal_description=row["deal_description"],
            available_sizes=row["available_sizes"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class ErrorLogRepository(BaseRepository):
    """Repository for error log operations."""

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
            ),
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_recent(self, limit: int = 10) -> list[ErrorRecord]:
        """Get recent error records."""
        cursor = self.db.execute(
            "SELECT * FROM error_log ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_all_filtered(
        self,
        filters: dict | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ErrorRecord]:
        """Get all error logs with filters and pagination."""
        query = "SELECT * FROM error_log"
        conditions = []
        params: list[Any] = []

        if filters:
            if filters.get("error_type"):
                conditions.append("error_type = ?")
                params.append(filters["error_type"])
            if filters.get("start_date"):
                conditions.append("date(created_at) >= ?")
                params.append(filters["start_date"])
            if filters.get("end_date"):
                conditions.append("date(created_at) <= ?")
                params.append(filters["end_date"])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.db.execute(query, tuple(params))
        return [self._row_to_record(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_record(row) -> ErrorRecord:
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


class ProductRepository(BaseRepository):
    """Repository for product operations."""

    def insert(self, product: Product) -> int:
        """Insert a product and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO products
            (name, category, purchase_type, target_price, target_unit, planned_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                product.name,
                product.category,
                product.purchase_type,
                product.target_price,
                product.target_unit,
                product.planned_date,
            ),
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_by_id(self, product_id: int) -> Product | None:
        """Get a product by ID."""
        cursor = self.db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_all(self) -> list[Product]:
        """Get all products."""
        cursor = self.db.execute("SELECT * FROM products ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def search(self, query: str) -> list[Product]:
        """Search products by name using SQL LIKE."""
        cursor = self.db.execute(
            "SELECT * FROM products WHERE name LIKE ? ORDER BY name", (f"%{query}%",)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_by_category(self, category: str) -> list[Product]:
        """Get products by category."""
        cursor = self.db.execute(
            "SELECT * FROM products WHERE category = ? ORDER BY name", (category,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def find_orphans(self) -> list[Product]:
        """Find products that have no tracked items linked to them."""
        cursor = self.db.execute(
            """
            SELECT p.* FROM products p
            LEFT JOIN tracked_items ti ON p.id = ti.product_id
            WHERE ti.id IS NULL
            ORDER BY p.name
            """
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def bulk_delete(self, product_ids: list[int]) -> None:
        """Delete multiple products and their tracked items."""
        if not product_ids:
            return

        placeholders = ",".join("?" for _ in product_ids)
        # 1. Delete tracked items first (cascade)
        self.db.execute(
            f"DELETE FROM tracked_items WHERE product_id IN ({placeholders})",  # nosec # noqa: S608
            tuple(product_ids),
        )
        # 2. Delete products
        self.db.execute(
            f"DELETE FROM products WHERE id IN ({placeholders})",  # nosec # noqa: S608
            tuple(product_ids),
        )
        self.db.commit()

    def merge(self, source_id: int, target_id: int) -> None:
        """Merge source product into target product and move all tracked items."""
        if source_id == target_id:
            return

        try:
            # 1. Update all tracked items to point to the target product
            self.db.execute(
                "UPDATE tracked_items SET product_id = ? WHERE product_id = ?",
                (target_id, source_id),
            )
            # 2. Delete the source product
            self.db.execute("DELETE FROM products WHERE id = ?", (source_id,))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def update(self, product_id: int, product: Product) -> None:
        """Update a product."""
        self.db.execute(
            """
            UPDATE products SET
                name = ?,
                category = ?,
                purchase_type = ?,
                target_price = ?,
                target_unit = ?,
                planned_date = ?
            WHERE id = ?
            """,
            (
                product.name,
                product.category,
                product.purchase_type,
                product.target_price,
                product.target_unit,
                product.planned_date,
                product_id,
            ),
        )
        self.db.commit()

    def delete(self, product_id: int) -> None:
        """Delete a product."""
        self.db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.db.commit()

    @staticmethod
    def _row_to_record(row) -> Product:
        """Convert a database row to a Product."""
        return Product(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            purchase_type=row["purchase_type"],
            target_price=row["target_price"],
            target_unit=row["target_unit"],
            planned_date=row["planned_date"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class StoreRepository(BaseRepository):
    """Repository for store operations."""

    def normalize_name(self, name: str) -> str:
        """Normalize store name: case-insensitive check against DB, else capitalize."""
        clean_name = name.strip()
        if not clean_name:
            return clean_name

        cursor = self.db.execute(
            "SELECT name FROM stores WHERE name = ? COLLATE NOCASE", (clean_name,)
        )
        row = cursor.fetchone()
        if row:
            return row["name"]

        return clean_name.capitalize()

    def insert(self, store: Store) -> int:
        """Insert a store and return its ID."""
        cursor = self.db.execute("INSERT INTO stores (name) VALUES (?)", (store.name,))
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_by_id(self, store_id: int) -> Store | None:
        """Get a store by ID."""
        cursor = self.db.execute("SELECT * FROM stores WHERE id = ?", (store_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_name(self, name: str) -> Store | None:
        """Get a store by name."""
        cursor = self.db.execute("SELECT * FROM stores WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_all(self) -> list[Store]:
        """Get all stores."""
        cursor = self.db.execute("SELECT * FROM stores ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def update(self, store_id: int, store: Store) -> None:
        """Update a store."""
        self.db.execute(
            "UPDATE stores SET name = ? WHERE id = ?", (store.name, store_id)
        )
        self.db.commit()

    def delete(self, store_id: int) -> None:
        """Delete a store."""
        self.db.execute("DELETE FROM stores WHERE id = ?", (store_id,))
        self.db.commit()

    @staticmethod
    def _row_to_record(row) -> Store:
        """Convert a database row to a Store."""
        return Store(id=row["id"], name=row["name"])


class TrackedItemRepository(BaseRepository):
    """Repository for tracked item operations."""

    def insert(self, item: TrackedItem) -> int:
        """Insert a tracked item and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO tracked_items
            (product_id, store_id, url,
             target_size, quantity_size, quantity_unit,
             items_per_lot, is_active, alerts_enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.product_id,
                item.store_id,
                item.url,
                item.target_size,
                item.quantity_size,
                item.quantity_unit,
                item.items_per_lot,
                1 if item.is_active else 0,
                1 if item.alerts_enabled else 0,
            ),
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_by_id(self, item_id: int) -> TrackedItem | None:
        """Get a tracked item by ID."""
        cursor = self.db.execute("SELECT * FROM tracked_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_url(self, url: str) -> TrackedItem | None:
        """Get a tracked item by URL."""
        cursor = self.db.execute("SELECT * FROM tracked_items WHERE url = ?", (url,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_all(self) -> list[TrackedItem]:
        """Get all tracked items."""
        cursor = self.db.execute("SELECT * FROM tracked_items")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_active(self) -> list[TrackedItem]:
        """Get all active tracked items."""
        cursor = self.db.execute("SELECT * FROM tracked_items WHERE is_active = 1")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_due_for_check(self) -> list[TrackedItem]:
        """Get active items not checked today (for scheduled extraction)."""
        cursor = self.db.execute(
            """
            SELECT * FROM tracked_items
            WHERE is_active = 1
            AND (last_checked_at IS NULL OR date(last_checked_at) < date('now'))
            """
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def set_last_checked(self, item_id: int) -> None:
        """Update the last_checked_at timestamp."""
        self.db.execute(
            "UPDATE tracked_items SET last_checked_at = datetime('now') WHERE id = ?",
            (item_id,),
        )
        self.db.commit()

    def update(self, item_id: int, item: TrackedItem) -> None:
        """Update a tracked item."""
        self.db.execute(
            """
            UPDATE tracked_items SET
                product_id = ?,
                store_id = ?,
                url = ?,
                target_size = ?,
                quantity_size = ?,
                quantity_unit = ?,
                items_per_lot = ?,
                is_active = ?,
                alerts_enabled = ?
            WHERE id = ?
            """,
            (
                item.product_id,
                item.store_id,
                item.url,
                item.target_size,
                item.quantity_size,
                item.quantity_unit,
                item.items_per_lot,
                1 if item.is_active else 0,
                1 if item.alerts_enabled else 0,
                item_id,
            ),
        )
        self.db.commit()

    def delete(self, item_id: int) -> None:
        """Delete a tracked item."""
        self.db.execute("DELETE FROM tracked_items WHERE id = ?", (item_id,))
        self.db.commit()

    def get_by_product(self, product_id: int) -> list[TrackedItem]:
        """Get all tracked items for a product."""
        cursor = self.db.execute(
            "SELECT * FROM tracked_items WHERE product_id = ?", (product_id,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def count_by_store(self, store_id: int) -> int:
        """Count tracked items associated with a store."""
        cursor = self.db.execute(
            "SELECT COUNT(*) FROM tracked_items WHERE store_id = ?", (store_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0

    def delete_by_product(self, product_id: int) -> None:
        """Delete all tracked items for a product."""
        self.db.execute("DELETE FROM tracked_items WHERE product_id = ?", (product_id,))
        self.db.commit()

    # --- Label Management ---

    def add_label(self, tracked_item_id: int, label_id: int) -> None:
        """Associate a label with a tracked item."""
        self.db.execute(
            "INSERT OR IGNORE INTO tracked_item_labels "
            "(tracked_item_id, label_id) VALUES (?, ?)",
            (tracked_item_id, label_id),
        )
        self.db.commit()

    def remove_all_labels(self, tracked_item_id: int) -> None:
        """Remove all label associations for a tracked item."""
        self.db.execute(
            "DELETE FROM tracked_item_labels WHERE tracked_item_id = ?",
            (tracked_item_id,),
        )
        self.db.commit()

    def set_labels(self, tracked_item_id: int, label_ids: list[int]) -> None:
        """Set label associations for a tracked item (replaces existing)."""
        self.remove_all_labels(tracked_item_id)
        for label_id in label_ids:
            self.add_label(tracked_item_id, label_id)

    def get_labels(self, tracked_item_id: int) -> list[Label]:
        """Get all labels associated with a tracked item."""
        cursor = self.db.execute(
            """
            SELECT l.* FROM labels l
            JOIN tracked_item_labels til ON l.id = til.label_id
            WHERE til.tracked_item_id = ?
            """,
            (tracked_item_id,),
        )

        return [Label(id=row["id"], name=row["name"]) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_record(row) -> TrackedItem:
        """Convert a database row to a TrackedItem."""
        last_checked = None
        if row["last_checked_at"]:
            try:
                last_checked = datetime.fromisoformat(row["last_checked_at"])
            except Exception:
                logger.debug("Failed to parse last_checked_at")

        return TrackedItem(
            id=int(row["id"]),
            product_id=int(row["product_id"]),
            store_id=int(row["store_id"]),
            url=str(row["url"]),
            target_size=str(row["target_size"]) if row["target_size"] else None,
            quantity_size=float(row["quantity_size"]),
            quantity_unit=str(row["quantity_unit"]),
            items_per_lot=int(row["items_per_lot"]),
            last_checked_at=last_checked,
            is_active=bool(row["is_active"]),
            alerts_enabled=bool(row["alerts_enabled"]),
        )


class ExtractionLogRepository(BaseRepository):
    """Repository for extraction log operations."""

    def insert(self, log: ExtractionLog) -> int:
        """Insert an extraction log and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO extraction_logs
            (tracked_item_id, status, model_used, price, currency,
             error_message, duration_ms, blocking_type, is_screenshot_faulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                log.tracked_item_id,
                log.status,
                log.model_used,
                log.price,
                log.currency,
                log.error_message,
                log.duration_ms,
                log.blocking_type,
                1 if log.is_screenshot_faulty else 0,
            ),
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_by_id(self, log_id: int) -> ExtractionLog | None:
        """Get an extraction log by ID."""
        cursor = self.db.execute(
            "SELECT * FROM extraction_logs WHERE id = ?", (log_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_recent(self, limit: int = 50) -> list[ExtractionLog]:
        """Get recent extraction logs."""
        cursor = self.db.execute(
            "SELECT * FROM extraction_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_by_item(self, tracked_item_id: int, limit: int = 20) -> list[ExtractionLog]:
        """Get extraction logs for a specific tracked item."""
        cursor = self.db.execute(
            """
            SELECT * FROM extraction_logs
            WHERE tracked_item_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (tracked_item_id, limit),
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_stats(self) -> dict:
        """Get extraction statistics."""
        cursor = self.db.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(
                    CASE WHEN status = 'success' THEN 1
                    ELSE 0 END
                ) as success_count,
                SUM(
                    CASE WHEN status = 'error' THEN 1
                    ELSE 0 END
                ) as error_count,
                AVG(
                    CASE WHEN status = 'success' THEN duration_ms
                    END
                ) as avg_duration_ms
            FROM extraction_logs
            WHERE date(created_at) = date('now')
            """
        )
        row = cursor.fetchone()
        return {
            "total_today": row["total"] or 0,
            "success_count": row["success_count"] or 0,
            "error_count": row["error_count"] or 0,
            "avg_duration_ms": int(row["avg_duration_ms"])
            if row["avg_duration_ms"]
            else 0,
        }

    def get_all_filtered(
        self,
        filters: dict | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ExtractionLog]:
        """Get all extraction logs with filters and pagination."""
        query = "SELECT * FROM extraction_logs"
        conditions = []
        params: list[Any] = []

        if filters:
            if filters.get("status"):
                conditions.append("status = ?")
                params.append(filters["status"])
            if filters.get("item_id"):
                conditions.append("tracked_item_id = ?")
                params.append(filters["item_id"])
            if filters.get("start_date"):
                conditions.append("date(created_at) >= ?")
                params.append(filters["start_date"])
            if filters.get("end_date"):
                conditions.append("date(created_at) <= ?")
                params.append(filters["end_date"])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.db.execute(query, tuple(params))
        return [self._row_to_record(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_record(row) -> ExtractionLog:
        """Convert a database row to an ExtractionLog."""
        return ExtractionLog(
            id=row["id"],
            tracked_item_id=row["tracked_item_id"],
            status=row["status"],
            model_used=row["model_used"],
            price=row["price"],
            currency=row["currency"],
            error_message=row["error_message"],
            duration_ms=row["duration_ms"],
            blocking_type=row["blocking_type"],
            is_screenshot_faulty=bool(row["is_screenshot_faulty"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class SchedulerRunRepository(BaseRepository):
    """Repository for scheduler run logging."""

    def start_run(self, items_total: int) -> int:
        """Start a new scheduler run and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO scheduler_runs (items_total, status)
            VALUES (?, 'running')
            """,
            (items_total,),
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def complete_run(
        self,
        run_id: int,
        items_success: int,
        items_failed: int,
        error_message: str | None = None,
    ) -> None:
        """Mark a scheduler run as completed."""
        status = "failed" if error_message else "completed"
        self.db.execute(
            """
            UPDATE scheduler_runs
            SET completed_at = datetime('now'),
                status = ?,
                items_success = ?,
                items_failed = ?,
                error_message = ?
            WHERE id = ?
            """,
            (status, items_success, items_failed, error_message, run_id),
        )
        self.db.commit()

    def fail_run(self, run_id: int, error_message: str) -> None:
        """Mark a scheduler run as failed."""
        self.db.execute(
            """
            UPDATE scheduler_runs
            SET completed_at = datetime('now'),
                status = 'failed',
                error_message = ?
            WHERE id = ?
            """,
            (error_message, run_id),
        )
        self.db.commit()

    def get_by_id(self, run_id: int) -> dict | None:
        """Get a scheduler run by ID."""
        cursor = self.db.execute("SELECT * FROM scheduler_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_last_run(self) -> dict | None:
        """Get the most recent scheduler run."""
        cursor = self.db.execute(
            "SELECT * FROM scheduler_runs ORDER BY started_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_recent(self, limit: int = 10) -> list[dict]:
        """Get recent scheduler runs."""
        cursor = self.db.execute(
            "SELECT * FROM scheduler_runs ORDER BY started_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


class CategoryRepository(BaseRepository):
    """Repository for category operations."""

    def normalize_name(self, name: str) -> str:
        """
        Normalize category name: case-insensitive check against DB,
        else capitalize.
        """
        clean_name = name.strip()
        if not clean_name:
            return clean_name

        cursor = self.db.execute(
            "SELECT name FROM categories WHERE name = ? COLLATE NOCASE", (clean_name,)
        )
        row = cursor.fetchone()
        if row:
            return row["name"]

        return clean_name.capitalize()

    def insert(self, category: Category) -> int:
        """Insert a category and return its ID."""
        cursor = self.db.execute(
            "INSERT INTO categories (name, is_size_sensitive) VALUES (?, ?)",
            (category.name, 1 if category.is_size_sensitive else 0),
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_all(self) -> list[Category]:
        """Get all categories."""
        cursor = self.db.execute("SELECT * FROM categories ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def search(self, query: str) -> list[Category]:
        """Search categories by name."""
        cursor = self.db.execute(
            "SELECT * FROM categories WHERE name LIKE ? ORDER BY name", (f"%{query}%",)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_by_name(self, name: str) -> Category | None:
        """Get a category by name."""
        cursor = self.db.execute("SELECT * FROM categories WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_id(self, category_id: int) -> Category | None:
        """Get a category by ID."""
        cursor = self.db.execute(
            "SELECT * FROM categories WHERE id = ?", (category_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def update(self, category_id: int, category: Category) -> None:
        """Update a category."""
        self.db.execute(
            "UPDATE categories SET name = ?, is_size_sensitive = ? WHERE id = ?",
            (category.name, 1 if category.is_size_sensitive else 0, category_id),
        )
        self.db.commit()

    def delete(self, category_id: int) -> None:
        """Delete a category."""
        self.db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.db.commit()

    @staticmethod
    def _row_to_record(row) -> Category:
        """Convert a database row to a Category."""
        return Category(
            id=row["id"],
            name=row["name"],
            is_size_sensitive=bool(row["is_size_sensitive"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class LabelRepository(BaseRepository):
    """Repository for label operations."""

    def insert(self, label: Label) -> int:
        """Insert a label and return its ID."""
        cursor = self.db.execute("INSERT INTO labels (name) VALUES (?)", (label.name,))
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_all(self) -> list[Label]:
        """Get all labels."""
        cursor = self.db.execute("SELECT * FROM labels ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def search(self, query: str) -> list[Label]:
        """Search labels by name."""
        cursor = self.db.execute(
            "SELECT * FROM labels WHERE name LIKE ? ORDER BY name", (f"%{query}%",)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_by_name(self, name: str) -> Label | None:
        """Get a label by name."""
        cursor = self.db.execute("SELECT * FROM labels WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_id(self, label_id: int) -> Label | None:
        """Get a label by ID."""
        cursor = self.db.execute("SELECT * FROM labels WHERE id = ?", (label_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def update(self, label_id: int, name: str) -> None:
        """Update a label name."""
        self.db.execute("UPDATE labels SET name = ? WHERE id = ?", (name, label_id))
        self.db.commit()

    def delete(self, label_id: int) -> None:
        """Delete a label."""
        self.db.execute("DELETE FROM labels WHERE id = ?", (label_id,))
        self.db.commit()

    @staticmethod
    def _row_to_record(row) -> Label:
        """Convert a database row to a Label."""
        return Label(
            id=row["id"],
            name=row["name"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class UnitRepository(BaseRepository):
    """Repository for unit operations."""

    def insert(self, unit: Unit) -> int:
        """Insert a unit and return its ID."""
        cursor = self.db.execute("INSERT INTO units (name) VALUES (?)", (unit.name,))
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_all(self) -> list[Unit]:
        """Get all units."""
        cursor = self.db.execute("SELECT * FROM units ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_by_name(self, name: str) -> Unit | None:
        """Get a unit by name."""
        cursor = self.db.execute("SELECT * FROM units WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_id(self, unit_id: int) -> Unit | None:
        """Get a unit by ID."""
        cursor = self.db.execute("SELECT * FROM units WHERE id = ?", (unit_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def update(self, unit_id: int, unit: Unit) -> None:
        """Update a unit and cascade name changes."""
        old_unit = self.get_by_id(unit_id)
        if not old_unit:
            return

        # Cascade changes if name changed
        if unit.name != old_unit.name:
            # Update products target_unit
            self.db.execute(
                "UPDATE products SET target_unit = ? WHERE target_unit = ?",
                (unit.name, old_unit.name),
            )
            # Update tracked_items quantity_unit
            self.db.execute(
                "UPDATE tracked_items SET quantity_unit = ? WHERE quantity_unit = ?",
                (unit.name, old_unit.name),
            )

        self.db.execute("UPDATE units SET name = ? WHERE id = ?", (unit.name, unit_id))
        self.db.commit()

    def delete(self, unit_id: int) -> None:
        """Delete a unit."""
        self.db.execute("DELETE FROM units WHERE id = ?", (unit_id,))
        self.db.commit()

    @staticmethod
    def _row_to_record(row) -> Unit:
        """Convert a database row to a Unit."""
        return Unit(id=row["id"], name=row["name"])


class PurchaseTypeRepository(BaseRepository):
    """Repository for purchase type operations."""

    def insert(self, pt: PurchaseType) -> int:
        """Insert a purchase type and return its ID."""
        cursor = self.db.execute(
            "INSERT INTO purchase_types (name) VALUES (?)", (pt.name,)
        )
        self.db.commit()
        return int(cursor.lastrowid or 0)

    def get_all(self) -> list[PurchaseType]:
        """Get all purchase types."""
        cursor = self.db.execute("SELECT * FROM purchase_types ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_by_name(self, name: str) -> PurchaseType | None:
        """Get a purchase type by name."""
        cursor = self.db.execute("SELECT * FROM purchase_types WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_id(self, pt_id: int) -> PurchaseType | None:
        """Get a purchase type by ID."""
        cursor = self.db.execute("SELECT * FROM purchase_types WHERE id = ?", (pt_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def update(self, pt_id: int, pt: PurchaseType) -> None:
        """Update a purchase type and cascade name changes."""
        old_pt = self.get_by_id(pt_id)
        if not old_pt:
            return

        # Cascade changes to products if name changed
        if pt.name != old_pt.name:
            self.db.execute(
                "UPDATE products SET purchase_type = ? WHERE purchase_type = ?",
                (pt.name, old_pt.name),
            )

        self.db.execute(
            "UPDATE purchase_types SET name = ? WHERE id = ?", (pt.name, pt_id)
        )
        self.db.commit()

    def delete(self, pt_id: int) -> None:
        """Delete a purchase type."""
        self.db.execute("DELETE FROM purchase_types WHERE id = ?", (pt_id,))
        self.db.commit()

    @staticmethod
    def _row_to_record(row) -> PurchaseType:
        """Convert a database row to a PurchaseType."""
        return PurchaseType(id=row["id"], name=row["name"])
