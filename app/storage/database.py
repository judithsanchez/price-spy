"""SQLite database connection management."""

import sqlite3
from typing import Optional

SCHEMA = """
-- Purchase Types Table (Seeded)
CREATE TABLE IF NOT EXISTS purchase_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Units Table (Seeded)
CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Products Table (Master product concepts)
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    purchase_type TEXT DEFAULT 'recurring',
    target_price REAL,
    target_unit TEXT,
    planned_date TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Stores Table (Names only)
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Tracked Items Table (URLs linked to products and stores)
CREATE TABLE IF NOT EXISTS tracked_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    target_size TEXT,
    quantity_size REAL NOT NULL,
    quantity_unit TEXT NOT NULL,
    items_per_lot INTEGER DEFAULT 1,
    last_checked_at TEXT,
    is_active INTEGER DEFAULT 1,
    alerts_enabled INTEGER DEFAULT 1,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY(store_id) REFERENCES stores(id) ON DELETE CASCADE
);

-- Junction table for optional labels on tracked items
CREATE TABLE IF NOT EXISTS tracked_item_labels (
    tracked_item_id INTEGER NOT NULL,
    label_id INTEGER NOT NULL,
    PRIMARY KEY (tracked_item_id, label_id),
    FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id) ON DELETE CASCADE,
    FOREIGN KEY(label_id) REFERENCES labels(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tracked_items_url ON tracked_items(url);
CREATE INDEX IF NOT EXISTS idx_tracked_items_product ON tracked_items(product_id);
CREATE INDEX IF NOT EXISTS idx_tracked_items_active ON tracked_items(is_active);

-- Price History Table
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    product_name TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    is_available INTEGER DEFAULT 1,
    is_size_matched INTEGER DEFAULT 1,
    confidence REAL NOT NULL,
    url TEXT NOT NULL,
    store_name TEXT,
    page_type TEXT,
    notes TEXT,
    original_price REAL,
    deal_type TEXT,
    deal_description TEXT,
    available_sizes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (item_id) REFERENCES tracked_items (id) ON DELETE CASCADE
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

-- Extraction Logs Table (tracks all extraction attempts)
CREATE TABLE IF NOT EXISTS extraction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracked_item_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('success', 'error')) NOT NULL,
    model_used TEXT,
    price REAL,
    currency TEXT,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id)
);

CREATE INDEX IF NOT EXISTS idx_extraction_logs_item ON extraction_logs(tracked_item_id);
CREATE INDEX IF NOT EXISTS idx_extraction_logs_created_at
    ON extraction_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_extraction_logs_status ON extraction_logs(status);

-- API Usage Table (tracks rate limits per model per day)
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    date TEXT NOT NULL,
    request_count INTEGER DEFAULT 0,
    last_request_at TEXT,
    is_exhausted INTEGER DEFAULT 0,
    UNIQUE(model, date)
);

CREATE INDEX IF NOT EXISTS idx_api_usage_date ON api_usage(date);

-- Scheduler Runs Table (tracks scheduled extraction runs)
CREATE TABLE IF NOT EXISTS scheduler_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    status TEXT CHECK(status IN ('running', 'completed', 'failed')) NOT NULL DEFAULT 'running',
    items_total INTEGER NOT NULL DEFAULT 0,
    items_success INTEGER NOT NULL DEFAULT 0,
    items_failed INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_scheduler_runs_started_at
    ON scheduler_runs(started_at);

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_size_sensitive INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- Labels Table (Names only, not seeded)
CREATE TABLE IF NOT EXISTS labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_labels_name ON labels(name);

"""


class Database:
    """SQLite database connection manager."""

    def __init__(self, db_path: str = "data/pricespy.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def _connect(self) -> sqlite3.Connection:
        """Create database connection with safety check."""
        import os

        # SAFETY GUARD: Prevent accidental production database modification during tests
        is_test = (
            os.environ.get("PYTEST_CURRENT_TEST")
            or os.environ.get("PRICESPY_ENV") == "test"
        )
        is_prod_path = self.db_path == "data/pricespy.db" or os.path.abspath(
            self.db_path
        ) == os.path.abspath("data/pricespy.db")

        if is_test and is_prod_path:
            raise RuntimeError(
                f"SAFETY BLOCK: Attempted to connect to production database "
                f"'{self.db_path}' while running tests. "
                "Please ensure DATABASE_PATH is correctly overridden "
                "in your test environment."
            )

        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _needs_products_migration(self, cursor) -> bool:
        cursor.execute("PRAGMA table_info(products)")
        columns = [row["name"] for row in cursor.fetchall()]
        unwanted = ["labels", "brand", "preferred_unit_size", "current_stock"]
        return any(col in columns for col in unwanted)

    def _migrate_products_table(self, conn) -> None:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = [row["name"] for row in cursor.fetchall()]
        unwanted = ["labels", "brand", "preferred_unit_size", "current_stock"]
        keep = [c for c in columns if c not in unwanted]
        keep_csv = ", ".join(keep)
        conn.execute("BEGIN TRANSACTION")
        try:
            conn.execute("ALTER TABLE products RENAME TO products_old")
            conn.executescript(SCHEMA)
            conn.execute(
                f"INSERT INTO products ({keep_csv}) SELECT {keep_csv} FROM products_old"  # nosec B608
            )
            conn.execute("DROP TABLE products_old")
            conn.commit()
        except:
            conn.rollback()
            raise

    def initialize(self) -> None:
        """Initialize database schema and perform migrations."""
        conn = self._connect()
        conn.executescript(SCHEMA)

        cursor = conn.cursor()
        if self._needs_products_migration(cursor):
            try:
                self._migrate_products_table(conn)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Migration failed (products): {e}")

        # 1.1. Ensure planned_date exists (for cases where other migrations already ran)
        cursor.execute("PRAGMA table_info(products)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "planned_date" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN planned_date TEXT")

        # 2. Handle stores table migration
        cursor.execute("PRAGMA table_info(stores)")
        columns = [row["name"] for row in cursor.fetchall()]
        unwanted_stores = [
            "is_size_sensitive",
            "shipping_cost_standard",
            "free_shipping_threshold",
            "notes",
        ]

        if any(col in columns for col in unwanted_stores):
            conn.execute("BEGIN TRANSACTION")
            try:
                conn.execute("ALTER TABLE stores RENAME TO stores_old")
                conn.executescript(SCHEMA)
                # Only copy id and name
                conn.execute(
                    "INSERT INTO stores (id, name) SELECT id, name FROM stores_old"
                )
                conn.execute("DROP TABLE stores_old")
                conn.commit()
                print("Stores migration successful.")
            except Exception as e:
                conn.rollback()
                print(f"Migration failed (stores): {e}")

        # 2. Seed purchase_types if empty
        cursor.execute("SELECT COUNT(*) FROM purchase_types")
        if cursor.fetchone()[0] == 0:
            purchase_types = ["recurring", "one_time"]
            conn.executemany(
                "INSERT INTO purchase_types (name) VALUES (?)",
                [(p,) for p in purchase_types],
            )

        # 3. Seed units if empty
        cursor.execute("SELECT COUNT(*) FROM units")
        if cursor.fetchone()[0] == 0:
            units = [
                "ml",
                "cl",
                "dl",
                "L",
                "g",
                "kg",
                "lb",
                "oz",
                "fl oz",
                "piece",
                "pack",
                "pair",
                "set",
                "tube",
                "bottle",
                "can",
                "box",
                "bag",
                "tub",
                "jar",
                "unit",
            ]
            conn.executemany(
                "INSERT INTO units (name) VALUES (?)", [(u,) for u in units]
            )

        # 3. Handle tracked_items table migration
        cursor.execute("PRAGMA table_info(tracked_items)")
        columns = [row["name"] for row in cursor.fetchall()]
        unwanted_ti = ["item_name_on_site", "preferred_model", "target_size_label"]

        if any(col in columns for col in unwanted_ti):
            # Identify columns we want to KEEP
            keep = [c for c in columns if c not in unwanted_ti]
            keep_csv = ", ".join(keep)

            conn.execute("BEGIN TRANSACTION")
            try:
                conn.execute("ALTER TABLE tracked_items RENAME TO tracked_items_old")
                conn.executescript(SCHEMA)
                # Copy data intersection
                conn.execute(
                    f"INSERT INTO tracked_items ({keep_csv}) "
                    f"SELECT {keep_csv} FROM tracked_items_old"  # nosec B608
                )
                conn.execute("DROP TABLE tracked_items_old")
                conn.commit()
                print("Tracked items migration successful.")
            except Exception as e:
                conn.rollback()
                print(f"Migration failed (tracked_items): {e}")

        # 4. Handle labels table migration (Remove is_size_sensitive)
        cursor.execute("PRAGMA table_info(labels)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "is_size_sensitive" in columns:
            conn.execute("BEGIN TRANSACTION")
            try:
                conn.execute("ALTER TABLE labels RENAME TO labels_old")
                conn.executescript(SCHEMA)
                conn.execute(
                    "INSERT INTO labels (id, name, created_at) "
                    "SELECT id, name, created_at FROM labels_old"
                )
                conn.execute("DROP TABLE labels_old")
                conn.commit()
                print("Labels table simplified.")
            except Exception as e:
                conn.rollback()
                print(f"Migration failed (labels): {e}")

        # 5. Handle other schema evolutions (if any)
        cursor.execute("PRAGMA table_info(price_history)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "is_available" not in columns:
            cursor.execute(
                "ALTER TABLE price_history ADD COLUMN is_available INTEGER DEFAULT 1"
            )
        if "notes" not in columns:
            cursor.execute("ALTER TABLE price_history ADD COLUMN notes TEXT")
        if "item_id" not in columns:
            cursor.execute("ALTER TABLE price_history ADD COLUMN item_id INTEGER")
        if "original_price" not in columns:
            cursor.execute("ALTER TABLE price_history ADD COLUMN original_price REAL")
        if "deal_type" not in columns:
            cursor.execute("ALTER TABLE price_history ADD COLUMN deal_type TEXT")
        if "discount_percentage" not in columns:
            cursor.execute(
                "ALTER TABLE price_history ADD COLUMN discount_percentage REAL"
            )
        if "discount_fixed_amount" not in columns:
            cursor.execute(
                "ALTER TABLE price_history ADD COLUMN discount_fixed_amount REAL"
            )
        if "deal_description" not in columns:
            cursor.execute("ALTER TABLE price_history ADD COLUMN deal_description TEXT")
        if "available_sizes" not in columns:
            cursor.execute("ALTER TABLE price_history ADD COLUMN available_sizes TEXT")
        if "is_size_matched" not in columns:
            cursor.execute(
                "ALTER TABLE price_history ADD COLUMN is_size_matched INTEGER DEFAULT 1"
            )

        # 5. Seed categories if table is empty
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            # Categories where physical size/fit is the tracking factor (Clothing, Footwear, Bedding)
            size_sensitive = [
                "Clothing",
                "Footwear",
                "Bedding",
                "Underwear & Sleepwear",
                "Accessories",
                "Jewelry",
                "Luggage & Bags",
            ]

            categories = [
                "Dairy",
                "Bakery",
                "Beverages",
                "Snacks",
                "Frozen Foods",
                "Canned Goods",
                "Pasta & Grains",
                "Meat & Poultry",
                "Seafood",
                "Fruits",
                "Vegetables",
                "Condiments & Sauces",
                "Spices & Seasonings",
                "Baking Supplies",
                "Breakfast Foods",
                "Coffee & Tea",
                "Delicatessen",
                "Health Foods",
                "Baby Food",
                "Pet Food",
                "Cleaning Supplies",
                "Paper Products",
                "Laundry Care",
                "Dishwashing",
                "Personal Care",
                "Hair Care",
                "Skincare",
                "Oral Care",
                "Shaving & Grooming",
                "Cosmetics",
                "Feminine Care",
                "First Aid",
                "Over-the-Counter Medicine",
                "Vitamins & Minerals",
                "Baby Care",
                "School Supplies",
                "Office Supplies",
                "Electronics",
                "Computer Accessories",
                "Mobile Accessories",
                "Audio",
                "Photography",
                "Gaming",
                "Kitchen Appliances",
                "Small Home Appliances",
                "Tools & Hardware",
                "Painting & Decorating",
                "Electrical",
                "Plumbing",
                "Gardening",
                "Outdoor Tools",
                "Home Security",
                "Automotive",
                "Sports Equipment",
                "Fitness",
                "Camping & Outdoors",
                "Toys",
                "Board Games",
                "Crafts & Hobbies",
                "Party Supplies",
                "Gift Wrapping",
                "Clothing",
                "Underwear & Sleepwear",
                "Footwear",
                "Accessories",
                "Jewelry",
                "Luggage & Bags",
                "Bedding",
                "Bath Linens",
                "Kitchen Linens",
                "Curtains & Blinds",
                "Lighting",
                "Home Decor",
                "Storage & Organization",
                "Furniture",
                "Cookware",
                "Dinnerware",
                "Flatware",
                "Kitchen Utensils",
                "Glassware",
                "Barware",
                "Books - Fiction",
                "Books - Non-Fiction",
                "Books - Educational",
                "Books - Children",
                "Magazines & Newspapers",
                "Stationery",
                "Musical Instruments",
                "Professional Equipment",
                "Safety Equipment",
                "Travel Accessories",
                "Seasonal Decor",
                "Religious & Spiritual Items",
                "Wine",
                "Beer",
                "Spirits",
                "Alcohol-Free Alternatives",
                "Organic Foods",
                "Gluten-Free Products",
                "Vegan & Plant-Based",
                "International Foods - Asian",
                "International Foods - Mexican",
                "International Foods - Mediterranean",
                "Fresh Herbs",
                "Cooking Oils",
                "Vinegar",
                "Honey & Syrups",
                "Spreads",
                "Prepared Meals",
                "Deli Meats",
                "Artisanal Cheeses",
                "Smoked Fish",
                "Tofu & Meat Substitutes",
                "Special Diets",
                "Nuts & Dried Fruits",
                "Seeds",
                "Sweets & Confectionery",
                "Gum & Mints",
                "Dessert Toppings",
                "Water Softening Salts",
                "Pest Control",
                "Pool Maintenance",
                "Bicycle Accessories",
                "Pet Accessories",
                "Fish Tank Supplies",
                "Small Animal Supplies",
                "Terrarium Supplies",
                "Collectibles",
                "Antiques",
                "Fine Art",
                "Photography Equipment",
                "Video Projectors & Screens",
                "Smart Home Devices",
                "Wearable Tech",
                "Drones & RC Vehicles",
                "Home Office Furniture",
                "Space Heaters & Fans",
                "Air Purifiers & Humidifiers",
                "Water Filtration",
                "Fitness Large Equipment",
                "Yoga & Pilates",
                "Swimming Gear",
                "Team Sports",
                "Exercise Monitors",
                "Protective Gear",
                "Foot Care",
                "Eye Care",
                "Hearing Care",
                "Massage & Relaxation",
                "Aromatherapy & Essential Oils",
            ]

            # Use INSERT OR IGNORE to handle duplicates if schema exists
            for cat in categories:
                is_sensitive = 1 if cat in size_sensitive else 0
                conn.execute(
                    "INSERT OR IGNORE INTO categories "
                    "(name, is_size_sensitive) "
                    "VALUES (?, ?)",
                    (cat, is_sensitive),
                )
            conn.commit()

        # 6. Seed labels if table is empty
        cursor.execute("SELECT COUNT(*) FROM labels")
        if cursor.fetchone()[0] == 0:
            labels = [
                "Eco-friendly",
                "Sustainable",
                "Recyclable",
                "Biodegradable",
                "Plastic-free",
                "Compostable",
                "Zero-waste",
                "Carbon-neutral",
                "Ethically-sourced",
                "Fair-trade",
                "Cruelty-free",
                "Vegan",
                "Plant-based",
                "Organic",
                "Non-GMO",
                "Pesticide-free",
                "BPA-free",
                "Reusable",
                "Refillable",
                "Upcycled",
                "Local",
                "Handmade",
                "Artisanal",
                "B-Corp",
                "Rainforest-Alliance",
                "FSC-certified",
                "Animal-welfare",
                "Forest-friendly",
                "Oceans-safe",
                "Low-impact",
                "Gluten-free",
                "Dairy-free",
                "Nut-free",
                "Sugar-free",
                "Low-carb",
                "Keto",
                "Paleo",
                "Kosher",
                "Halal",
                "High-protein",
                "Low-sodium",
                "High-fiber",
                "No-additives",
                "No-preservatives",
                "Naturally-flavored",
                "Raw",
                "Sprouted",
                "Whole-grain",
                "Ancient-grains",
                "Soy-free",
                "Egg-free",
                "Shellfish-free",
                "Lactose-free",
                "Low-fat",
                "No-cholesterol",
                "Cold-pressed",
                "Wild-caught",
                "Grass-fed",
                "Free-range",
                "Pasture-raised",
                "Energy-star",
                "Wifi-enabled",
                "Bluetooth",
                "Smart",
                "Rechargeable",
                "Wireless",
                "Compact",
                "High-speed",
                "4K-Ready",
                "HDR",
                "Waterproof",
                "Shockproof",
                "Dustproof",
                "Anti-glare",
                "Ergonomic",
                "Quick-charge",
                "Noise-cancelling",
                "Studio-grade",
                "Heavy-duty",
                "USB-C",
                "Thunderbolt",
                "OLED",
                "LED",
                "Long-battery-life",
                "Portable",
                "Hypoallergenic",
                "Antibacterial",
                "Non-toxic",
                "Fragrance-free",
                "Odor-neutralizing",
                "Machine-washable",
                "Stain-resistant",
                "Wrinkle-free",
                "Flame-retardant",
                "Hand-wash-only",
                "Solid-wood",
                "Modular",
                "Space-saving",
                "Easy-assembly",
                "Child-safe",
                "Pet-safe",
                "Indoor-only",
                "Outdoor-use",
                "Weather-resistant",
                "Lightweight",
                "Premium",
                "Luxury",
                "Designer",
                "Limited-edition",
                "Bestseller",
                "Dermatologist-tested",
                "Paraben-free",
                "Sulfate-free",
                "Alcohol-free",
                "PH-balanced",
                "Anti-aging",
                "Moisturizing",
                "Sensitive-skin",
                "Natural-ingredients",
                "Essentials",
                "Travel-size",
                "Value-pack",
                "Refill",
                "Sample",
                "New-formula",
                "Fast-absorbing",
                "Long-lasting",
                "Water-resistant",
                "SPF-protection",
                "Professional-use",
                "Buy-1-Get-1",
                "Discounted",
                "On-sale",
                "New-arrival",
                "Trending",
                "Gift-idea",
                "Must-have",
                "Highly-rated",
                "Verified",
                "Authentic",
                "Exclusive",
                "Member-only",
                "Early-access",
                "Bulk-buy",
                "Stock-clearance",
                "Back-in-stock",
                "Seasonal",
                "Holiday-special",
                "Limited-stock",
                "Fan-favorite",
            ]
            conn.executemany(
                "INSERT INTO labels (name) VALUES (?)", [(label,) for label in labels]
            )

        conn.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        conn = self._connect()
        return conn.execute(query, params)

    def commit(self) -> None:
        """Commit current transaction."""
        if self._conn:
            self._conn.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        if self._conn:
            self._conn.rollback()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


def get_database(db_path: Optional[str] = None) -> Database:
    """Get a database instance."""
    from app.core.config import settings

    path = db_path or settings.DATABASE_PATH
    db = Database(path)
    db.initialize()
    return db
