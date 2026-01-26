# Purchase Types 🔄

Purchase Types define the buying frequency or nature of a product tracking goal.

## Database Schema

Located in `app/storage/database.py`.

```sql
CREATE TABLE purchase_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
```

---

## Seeded Values
Currently, Price Spy supports two primary purchase types:

1.  **`recurring`**: For items you buy regularly (e.g., groceries like Milk or Soap).
2.  **`one_time`**: For specific purchases (e.g., a specific piece of Electronics or Furniture).

---

## API Interaction
- **`GET /api/purchase-types`**: Lists all available purchase types.
- **`POST /api/purchase-types`**: Create a new purchase type.
- **`PUT /api/purchase-types/{id}`**: Update a purchase type and **cascade changes** to all products using it.
- **`PATCH /api/purchase-types/{id}`**: Partial update for purchase types.
- **`DELETE /api/purchase-types/{id}`**: Safely delete a purchase type. Deletion is **blocked** if it is currently in use by any product.
