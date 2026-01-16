"""SQLite database connection management."""

import sqlite3
from typing import Optional


SCHEMA = """
-- Products Table (Master product concepts)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    purchase_type TEXT CHECK(purchase_type IN ('recurring', 'one_time')) DEFAULT 'recurring',
    target_price REAL,
    preferred_unit_size TEXT,
    current_stock INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Stores Table (Shipping rules)
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    shipping_cost_standard REAL DEFAULT 0,
    free_shipping_threshold REAL,
    notes TEXT
);

-- Tracked Items Table (URLs linked to products and stores)
CREATE TABLE IF NOT EXISTS tracked_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    item_name_on_site TEXT,
    quantity_size REAL NOT NULL,
    quantity_unit TEXT NOT NULL,
    items_per_lot INTEGER DEFAULT 1,
    last_checked_at TEXT,
    is_active INTEGER DEFAULT 1,
    alerts_enabled INTEGER DEFAULT 1,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(store_id) REFERENCES stores(id)
);

CREATE INDEX IF NOT EXISTS idx_tracked_items_url ON tracked_items(url);
CREATE INDEX IF NOT EXISTS idx_tracked_items_product ON tracked_items(product_id);
CREATE INDEX IF NOT EXISTS idx_tracked_items_active ON tracked_items(is_active);

-- Price History Table
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    confidence REAL NOT NULL,
    url TEXT NOT NULL,
    store_name TEXT,
    page_type TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_price_history_url ON price_history(url);
CREATE INDEX IF NOT EXISTS idx_price_history_created_at ON price_history(created_at);

-- Error Log Table
CREATE TABLE IF NOT EXISTS error_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL,
    message TEXT NOT NULL,
    url TEXT,
    screenshot_path TEXT,
    stack_trace TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_error_log_created_at ON error_log(created_at);
"""


class Database:
    """SQLite database connection manager."""

    def __init__(self, db_path: str = "data/pricespy.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def _connect(self) -> sqlite3.Connection:
        """Create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def initialize(self) -> None:
        """Initialize database schema."""
        conn = self._connect()
        conn.executescript(SCHEMA)
        conn.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        conn = self._connect()
        return conn.execute(query, params)

    def commit(self) -> None:
        """Commit current transaction."""
        if self._conn:
            self._conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
