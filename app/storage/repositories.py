"""Repository classes for database operations."""

from datetime import datetime
from typing import List, Optional

from app.storage.database import Database
from app.models.schemas import (
    PriceHistoryRecord,
    ErrorRecord,
    Product,
    Store,
    TrackedItem,
)


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


class ProductRepository:
    """Repository for product operations."""

    def __init__(self, db: Database):
        self.db = db

    def insert(self, product: Product) -> int:
        """Insert a product and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO products
            (name, category, purchase_type, target_price, preferred_unit_size, current_stock)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                product.name,
                product.category,
                product.purchase_type,
                product.target_price,
                product.preferred_unit_size,
                product.current_stock,
            )
        )
        self.db.commit()
        return cursor.lastrowid

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        cursor = self.db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_all(self) -> List[Product]:
        """Get all products."""
        cursor = self.db.execute("SELECT * FROM products ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def update_stock(self, product_id: int, delta: int) -> None:
        """Update product stock by delta (positive or negative)."""
        self.db.execute(
            "UPDATE products SET current_stock = current_stock + ? WHERE id = ?",
            (delta, product_id)
        )
        self.db.commit()

    def update(self, product_id: int, product: Product) -> None:
        """Update a product."""
        self.db.execute(
            """
            UPDATE products SET
                name = ?,
                category = ?,
                purchase_type = ?,
                target_price = ?,
                preferred_unit_size = ?,
                current_stock = ?
            WHERE id = ?
            """,
            (
                product.name,
                product.category,
                product.purchase_type,
                product.target_price,
                product.preferred_unit_size,
                product.current_stock,
                product_id,
            )
        )
        self.db.commit()

    def delete(self, product_id: int) -> None:
        """Delete a product."""
        self.db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.db.commit()

    def _row_to_record(self, row) -> Product:
        """Convert a database row to a Product."""
        return Product(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            purchase_type=row["purchase_type"],
            target_price=row["target_price"],
            preferred_unit_size=row["preferred_unit_size"],
            current_stock=row["current_stock"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


class StoreRepository:
    """Repository for store operations."""

    def __init__(self, db: Database):
        self.db = db

    def insert(self, store: Store) -> int:
        """Insert a store and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO stores
            (name, shipping_cost_standard, free_shipping_threshold, notes)
            VALUES (?, ?, ?, ?)
            """,
            (
                store.name,
                store.shipping_cost_standard,
                store.free_shipping_threshold,
                store.notes,
            )
        )
        self.db.commit()
        return cursor.lastrowid

    def get_by_id(self, store_id: int) -> Optional[Store]:
        """Get a store by ID."""
        cursor = self.db.execute(
            "SELECT * FROM stores WHERE id = ?",
            (store_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_name(self, name: str) -> Optional[Store]:
        """Get a store by name."""
        cursor = self.db.execute(
            "SELECT * FROM stores WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_all(self) -> List[Store]:
        """Get all stores."""
        cursor = self.db.execute("SELECT * FROM stores ORDER BY name")
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def update(self, store_id: int, store: Store) -> None:
        """Update a store."""
        self.db.execute(
            """
            UPDATE stores SET
                name = ?,
                shipping_cost_standard = ?,
                free_shipping_threshold = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                store.name,
                store.shipping_cost_standard,
                store.free_shipping_threshold,
                store.notes,
                store_id,
            )
        )
        self.db.commit()

    def delete(self, store_id: int) -> None:
        """Delete a store."""
        self.db.execute("DELETE FROM stores WHERE id = ?", (store_id,))
        self.db.commit()

    def _row_to_record(self, row) -> Store:
        """Convert a database row to a Store."""
        return Store(
            id=row["id"],
            name=row["name"],
            shipping_cost_standard=row["shipping_cost_standard"],
            free_shipping_threshold=row["free_shipping_threshold"],
            notes=row["notes"],
        )


class TrackedItemRepository:
    """Repository for tracked item operations."""

    def __init__(self, db: Database):
        self.db = db

    def insert(self, item: TrackedItem) -> int:
        """Insert a tracked item and return its ID."""
        cursor = self.db.execute(
            """
            INSERT INTO tracked_items
            (product_id, store_id, url, item_name_on_site, quantity_size,
             quantity_unit, items_per_lot, is_active, alerts_enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.product_id,
                item.store_id,
                item.url,
                item.item_name_on_site,
                item.quantity_size,
                item.quantity_unit,
                item.items_per_lot,
                1 if item.is_active else 0,
                1 if item.alerts_enabled else 0,
            )
        )
        self.db.commit()
        return cursor.lastrowid

    def get_by_id(self, item_id: int) -> Optional[TrackedItem]:
        """Get a tracked item by ID."""
        cursor = self.db.execute(
            "SELECT * FROM tracked_items WHERE id = ?",
            (item_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_url(self, url: str) -> Optional[TrackedItem]:
        """Get a tracked item by URL."""
        cursor = self.db.execute(
            "SELECT * FROM tracked_items WHERE url = ?",
            (url,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_active(self) -> List[TrackedItem]:
        """Get all active tracked items."""
        cursor = self.db.execute(
            "SELECT * FROM tracked_items WHERE is_active = 1"
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def set_last_checked(self, item_id: int) -> None:
        """Update the last_checked_at timestamp."""
        self.db.execute(
            "UPDATE tracked_items SET last_checked_at = datetime('now') WHERE id = ?",
            (item_id,)
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
                item_name_on_site = ?,
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
                item.item_name_on_site,
                item.quantity_size,
                item.quantity_unit,
                item.items_per_lot,
                1 if item.is_active else 0,
                1 if item.alerts_enabled else 0,
                item_id,
            )
        )
        self.db.commit()

    def delete(self, item_id: int) -> None:
        """Delete a tracked item."""
        self.db.execute("DELETE FROM tracked_items WHERE id = ?", (item_id,))
        self.db.commit()

    def get_by_product(self, product_id: int) -> List[TrackedItem]:
        """Get all tracked items for a product."""
        cursor = self.db.execute(
            "SELECT * FROM tracked_items WHERE product_id = ?",
            (product_id,)
        )
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def _row_to_record(self, row) -> TrackedItem:
        """Convert a database row to a TrackedItem."""
        last_checked = None
        if row["last_checked_at"]:
            last_checked = datetime.fromisoformat(row["last_checked_at"])

        return TrackedItem(
            id=row["id"],
            product_id=row["product_id"],
            store_id=row["store_id"],
            url=row["url"],
            item_name_on_site=row["item_name_on_site"],
            quantity_size=row["quantity_size"],
            quantity_unit=row["quantity_unit"],
            items_per_lot=row["items_per_lot"],
            last_checked_at=last_checked,
            is_active=bool(row["is_active"]),
            alerts_enabled=bool(row["alerts_enabled"]),
        )
