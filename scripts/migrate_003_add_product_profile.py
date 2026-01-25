
import sqlite3
import os

DB_PATH = "data/pricespy.db"

def migrate():
    print(f"Migrating {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "target_size_label" not in columns:
            print("Adding target_size_label column...")
            cursor.execute("ALTER TABLE products ADD COLUMN target_size_label TEXT")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column target_size_label already exists.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
