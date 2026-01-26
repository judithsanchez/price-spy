# What are Products? 📦

A **Product** is the **Concept** or the "Master Idea" of something you want to buy.

- **Example:** "Argan Oil for Hair" or "Levi's 501 Overalls".
- **The Purpose:** It establishes your "budget" or **Target Price** per standard unit (e.g., "I want to pay €X per 100ml of Argan Oil" or "I want to pay €Y for this specific brand of overalls").
- **Independence:** You can create a Product by itself. It’s your wishlist of concepts.

### Products vs. Tracked Items
The Product is the "What," while the **Tracked Item** is the "Where and How."
- A **Product** (Argan Oil) can have multiple **Tracked Items** linked to it (e.g., a 30ml bottle from Amazon, a 60ml bottle from Sephora).
- When you create a **Tracked Item**, you *must* associate it with a **Product**.

---

## Database Schema

### Products: Master concepts (e.g., "Oat Milk")

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    purchase_type TEXT, -- Linked to purchase_types table
    target_price REAL,
    target_unit TEXT,   -- Linked to units table
    created_at TEXT DEFAULT (datetime('now'))
);
```
- `target_price`: According to the unit.
- `target_unit`: This is also from our units list.
- `purchase_type` is not reflected in the UI yet.

### Related Entities
Products rely on two additional static entities for standardization:

- **[Purchase Types](file:///home/judithvsanchezc/Desktop/dev/price-spy/docs/PURCHASE_TYPES.md)**: Defines buying frequency (`recurring` vs `one_time`).
- **[Measurement Units](file:///home/judithvsanchezc/Desktop/dev/price-spy/docs/UNITS.md)**: Standardized units like `ml`, `kg`, `piece`, etc.

---

### Pydantic Validation (The Bouncer)
Located in `app/models/schemas.py`. This ensures data is clean before it enters the database.

```python
class Product(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(default=None, max_length=100)
    purchase_type: Literal["recurring", "one_time"] = "recurring"
    target_price: Optional[float] = Field(default=None, gt=0)
    target_unit: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

---

## Backend Interactions

### Existing: Repository Layer (DAL)
Located in `app/storage/repositories.py`.
- **`insert(product)`**: Creates a new product concept in the database.
- **`get_by_id(id)`**: Fetches a specific product by its primary key.
- **`get_all()`**: Retrieves all products, ordered alphabetically by name.
- **`update(id, product)`**: Replaces all fields of an existing product.
- **`delete(id)`**: Permanently removes a product (and triggers cascade delete for tracked items).
- **`search(query)`**: High-speed SQL `LIKE` search for products by name.
- **`get_by_category(category)`**: Fast filtering by category name.
- **`find_orphans()`**: Identifies products that have no tracked items linked to them.
- **`bulk_delete(ids)`**: Removes multiple products and their history in one operation.
- **`merge(source_id, target_id)`**: A transaction that moves all tracked items from a duplicate product to a main one.

### Existing: API Layer (Controllers)
Located in `app/api/routers/products.py`.
- **`GET /api/products`**: Lists all products.
- **`POST /api/products`**: Validates and creates a product (auto-creates category if new).
- **`GET /api/products/{id}`**: Returns details for one product.
- **`PUT /api/products/{id}`**: Updates a product's full data.
- **`PATCH /api/products/{id}`**: **Surgical, granular update** for specific fields using `ProductUpdate` model.
- **`DELETE /api/products/{id}`**: Removes a product and its trackers.
- **`GET /api/products/search?q=...`**: Real-time search endpoint.
- **`GET /api/products/summary`**: Returns stats like Total Products, Orphans, and Categories.
- **`POST /api/products/merge`**: Resolves duplicate products by merging IDs.
- **`POST /api/products/bulk-delete`**: Mass-cleanup endpoint for removing multiple IDs.

---
---

## CLI Database Inspection 💻
Use these commands to verify the state of the database directly from the terminal using Python (no `sqlite3` binary required).

### 1. Check Table Schemas
Verify exactly what columns exist in each table:
```bash
# Check Products schema
python3 scripts/db_manager.py query "PRAGMA table_info(products)"

# Check Purchase Types and Units
python3 scripts/db_manager.py query "PRAGMA table_info(purchase_types)"
python3 scripts/db_manager.py query "PRAGMA table_info(units)"
```

### 2. View Table Data
See the raw content of the tables in a readable table format:
```bash
# View all Products (Master Concepts)
python3 scripts/db_manager.py query "SELECT * FROM products"

# View Seeded Data (Purchase Types & Units)
python3 scripts/db_manager.py query "SELECT * FROM purchase_types"
python3 scripts/db_manager.py query "SELECT * FROM units"
```

### 3. Quick Table Stats
```bash
# Count total items per table
python3 scripts/db_manager.py query "SELECT 'Products' as TableName, count(*) as Total FROM products UNION SELECT 'Units', count(*) FROM units"
```
