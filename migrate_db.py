import os
import sqlite3

db_path = "data/pricespy.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding target_size_label to tracked_items...")
    cursor.execute("ALTER TABLE tracked_items ADD COLUMN target_size_label TEXT;")
except sqlite3.OperationalError as e:
    print(f"Note: {e}")

try:
    print("Adding is_size_sensitive to categories...")
    cursor.execute(
        "ALTER TABLE categories ADD COLUMN is_size_sensitive BOOLEAN DEFAULT 0;"
    )
except sqlite3.OperationalError as e:
    print(f"Note: {e}")

try:
    print("Creating brand_sizes table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brand_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            category TEXT NOT NULL,
            size TEXT NOT NULL,
            label TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Ensure label column exists if table already existed without it
    try:
        cursor.execute("ALTER TABLE brand_sizes ADD COLUMN label TEXT;")
    except sqlite3.OperationalError:
        pass  # Already exists
except sqlite3.OperationalError as e:
    print(f"Error creating table: {e}")

conn.commit()
conn.close()
print("Migration completed.")
