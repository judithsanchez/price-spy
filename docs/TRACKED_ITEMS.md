# Tracked Items 🎯

Tracked items are specific product configurations (URL + Store) that Price Spy monitors.

## Schema

Located in `app/storage/database.py`.

```sql
CREATE TABLE tracked_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    quantity_size REAL NOT NULL, -- e.g. 500
    quantity_unit TEXT NOT NULL, -- e.g. 'g'
    items_per_lot INTEGER DEFAULT 1,
    last_checked_at TEXT,
    is_active INTEGER DEFAULT 1,
    alerts_enabled INTEGER DEFAULT 1,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY(store_id) REFERENCES stores(id) ON DELETE CASCADE
);
```

**Key Associations:**
- **Product**: Every tracked item belongs to exactly one conceptual `Product`.
- **Store**: Every tracked item belongs to exactly one `Store`.
- **Labels**: Can have multiple optional `Labels` via a junction table (see [LABELS.md](LABELS.md)).

---

## API Interaction

Modularized in `app/api/routers/tracked_items.py`.

- **`GET /api/tracked-items`**: List all tracked items.
- **`GET /api/tracked-items/{id}`**: Get a single item with its labels and latest price data.
- **`POST /api/tracked-items`**: Create a new tracked item.
- **`PUT /api/tracked-items/{id}`**: Update item details.
- **`PATCH /api/tracked-items/{id}`**: Partial update (e.g., toggle `is_active`).
- **`DELETE /api/tracked-items/{id}`**: Delete item.

### Creating an Item
You must provide `product_id`, `store_id`, `url`, and presentation details (`quantity_size`, `quantity_unit`).
Optionally, provide `label_ids` to auto-associate labels.

```json
{
  "product_id": 1,
  "store_id": 5,
  "url": "https://example.com/product",
  "quantity_size": 500,
  "quantity_unit": "ml",
  "label_ids": [2, 4]
}
```

---

## Unit Normalization
The `quantity_unit` field works with the `units` table to normalize prices. The system converts the item's unit price to the Product's `target_unit` for apples-to-apples comparison.
