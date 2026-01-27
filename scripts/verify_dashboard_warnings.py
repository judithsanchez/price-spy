import sqlite3
import os
from datetime import datetime, timedelta


def verify():
    db_path = "data/pricespy.db"
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # TEST URL
        test_url = "http://test.com/warning-logic"

        # 1. Setup a product and tracked item
        cursor.execute(
            "INSERT OR IGNORE INTO products (id, name, target_price) VALUES (999, 'Verification Logic Test', 100.0)"
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO tracked_items (id, product_id, store_id, url, is_active, quantity_size, quantity_unit) 
            VALUES (999, 999, 1, ?, 1, 100, 'ml')
        """,
            (test_url,),
        )

        # 2. Add History for Price Increase & Low Stock
        # Record 1: Yesterday, low price
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute(
            """
            INSERT INTO price_history (product_name, price, currency, is_available, confidence, url, store_name, notes, created_at)
            VALUES ('Verification Logic Test', 80.0, 'EUR', 1, 1.0, ?, 'Test Store', 'Stable', ?)
        """,
            (test_url, yesterday),
        )

        # Record 2: Now, high price + low stock note
        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO price_history (product_name, price, currency, is_available, confidence, url, store_name, notes, created_at)
            VALUES ('Verification Logic Test', 120.0, 'EUR', 1, 1.0, ?, 'Test Store', 'Only 1 unit left! (Low Stock Alert)', ?)
        """,
            (test_url, now),
        )

        conn.commit()
        print("Verification data inserted successfully.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    verify()
