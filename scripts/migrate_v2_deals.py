import sqlite3
import os

def migrate():
    db_path = 'data/pricespy.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        print("Adding discount_percentage column...")
        cur.execute("ALTER TABLE price_history ADD COLUMN discount_percentage REAL")
    except sqlite3.OperationalError:
        print("discount_percentage column already exists.")

    try:
        print("Adding discount_fixed_amount column...")
        cur.execute("ALTER TABLE price_history ADD COLUMN discount_fixed_amount REAL")
    except sqlite3.OperationalError:
        print("discount_fixed_amount column already exists.")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
