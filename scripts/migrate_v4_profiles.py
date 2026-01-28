import logging
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = "data/pricespy.db"
BACKUP_PATH = f"data/pricespy.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def migrate():
    db_path = Path(DB_PATH)
    backup_path = Path(BACKUP_PATH)

    if not db_path.exists():
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Backing up database to {BACKUP_PATH}...")
    shutil.copy2(db_path, backup_path)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Creating 'profiles' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        print("Migrating unique labels to profiles...")
        # Get all distinct labels from brand_sizes where label is not null/empty
        cursor.execute(
            "SELECT DISTINCT label FROM brand_sizes "
            "WHERE label IS NOT NULL AND label != ''"
        )
        labels = cursor.fetchall()

        for (label,) in labels:
            print(f"  - Creating profile: {label}")
            try:
                cursor.execute("INSERT INTO profiles (name) VALUES (?)", (label,))
            except sqlite3.IntegrityError:
                print(f"    (Profile '{label}' already exists)")

        print("Adding new columns to 'brand_sizes'...")
        # Check if columns exist
        cursor.execute("PRAGMA table_info(brand_sizes)")
        columns = [info[1] for info in cursor.fetchall()]

        if "profile_id" not in columns:
            print("  - Adding profile_id column")
            cursor.execute(
                "ALTER TABLE brand_sizes ADD COLUMN profile_id INTEGER "
                "REFERENCES profiles(id)"
            )

        if "item_type" not in columns:
            print("  - Adding item_type column")
            cursor.execute("ALTER TABLE brand_sizes ADD COLUMN item_type TEXT")

        print("Linking existing preferences to profiles...")
        # Update profile_id based on label
        cursor.execute("""
            UPDATE brand_sizes
            SET profile_id = (
                SELECT id FROM profiles
                WHERE profiles.name = brand_sizes.label
            )
            WHERE label IS NOT NULL
            AND label != ''
            AND profile_id IS NULL
        """)

        # Verify migration
        # Verify migration
        cursor.execute(
            "SELECT COUNT(*) FROM brand_sizes "
            "WHERE label IS NOT NULL AND label != '' AND profile_id IS NULL"
        )
        orphans = cursor.fetchone()[0]
        if orphans > 0:
            print(f"WARNING: {orphans} preferences could not be linked to a profile!")

        conn.commit()
        print("Migration completed successfully!")

    except Exception:
        logging.exception("Migration failed")
        conn.rollback()
        print("Rolled back changes. Restoring backup is manual if needed.")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
