# Stores 🏪

Price Spy tracks products across various retailers. The `stores` table is simplified to only include basic identification.

## Database Schema

Located in `app/storage/database.py`.

```sql
CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
```

---

## API Interaction
The Store API is modularized in `app/api/routers/stores.py`.

- **`GET /api/stores`**: Retrieves all stores in alphabetical order.
- **`POST /api/stores`**: Create a new store. Automatically capitalizes the name and checks for existing stores case-insensitively.
- **`PUT /api/stores/{id}`**: Update a store's name.
- **`PATCH /api/stores/{id}`**: Partially update a store.
- **`DELETE /api/stores/{id}`**: Safely delete a store. Deletion is **blocked** if the store is currently in use by any tracked items.

---

## Normalization
When creating or updating a store, the system uses `normalize_name`:
1.  **Case-Insensitive Match**: If "Amazon" exists and you send "amazon", it matches the existing record.
2.  **Auto-Capitalization**: If it's a new store like "my store", it becomes "My store".
