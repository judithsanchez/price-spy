# Slice 2: Full Data Model - Implementation Plan

## Overview

**Objective:** Implement the complete database schema from DATA_STRUCTURE.md to support multi-product, multi-store tracking with price comparison and unit price calculations.

**Success Criteria:**
- Track multiple URLs for the same product across different stores
- Calculate and display price per unit (e.g., EUR/L)
- Compare current price vs last price
- All tests pass within Docker/ARM64 environment

---

## 1. Current State (Slice 1)

What we have:
- `price_history` table (simple: url, product_name, price, currency, confidence)
- `error_log` table (error tracking)
- CLI that extracts and saves to database

What we need:
- `products` table (master product concepts)
- `stores` table (shipping rules)
- `tracked_items` table (URLs linked to products and stores)
- Enhanced `price_history` with volume_price calculations
- `process_logs` table with run_id grouping

---

## 2. Database Schema Changes

### 2.1 New Tables

```sql
-- Master product concepts (what you buy)
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    purchase_type TEXT CHECK(purchase_type IN ('recurring', 'one_time')) DEFAULT 'recurring',
    target_price REAL,
    preferred_unit_size TEXT,
    current_stock INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Store definitions with shipping rules
CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    shipping_cost_standard REAL DEFAULT 0,
    free_shipping_threshold REAL,
    notes TEXT
);

-- URLs to track (linked to products and stores)
CREATE TABLE tracked_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    item_name_on_site TEXT,
    quantity_size REAL NOT NULL,
    quantity_unit TEXT NOT NULL,
    items_per_lot INTEGER DEFAULT 1,
    last_checked_at DATETIME,
    is_active BOOLEAN DEFAULT 1,
    alerts_enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(store_id) REFERENCES stores(id)
);
```

### 2.2 Updated Tables

```sql
-- Enhanced price history with volume price
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracked_item_id INTEGER NOT NULL,
    price REAL NOT NULL,
    volume_price REAL,
    volume_unit TEXT,
    is_on_sale BOOLEAN DEFAULT 0,
    confidence REAL,
    raw_product_name TEXT,
    captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id)
);

-- Process logs with run grouping
CREATE TABLE process_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    trigger_source TEXT,
    process_name TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    raw_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Module Specifications

### 3.1 `app/models/schemas.py` - New Models

```python
class Product(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    purchase_type: Literal["recurring", "one_time"] = "recurring"
    target_price: Optional[float] = Field(default=None, gt=0)
    preferred_unit_size: Optional[str] = None
    current_stock: int = Field(default=0, ge=0)

class Store(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    shipping_cost_standard: float = Field(default=0, ge=0)
    free_shipping_threshold: Optional[float] = Field(default=None, gt=0)
    notes: Optional[str] = None

class TrackedItem(BaseModel):
    id: Optional[int] = None
    product_id: int
    store_id: int
    url: str
    item_name_on_site: Optional[str] = None
    quantity_size: float = Field(..., gt=0)
    quantity_unit: str = Field(..., min_length=1, max_length=20)
    items_per_lot: int = Field(default=1, ge=1)
    is_active: bool = True
    alerts_enabled: bool = True

class PriceComparison(BaseModel):
    current_price: float
    previous_price: Optional[float]
    price_change: Optional[float]
    price_change_percent: Optional[float]
    volume_price: Optional[float]
    volume_unit: Optional[str]
    is_price_drop: bool = False
```

### 3.2 `app/storage/database.py` - Schema Updates

Add migration support to create new tables while preserving existing data.

### 3.3 `app/storage/repositories.py` - New Repositories

```python
class ProductRepository:
    def insert(self, product: Product) -> int
    def get_by_id(self, id: int) -> Optional[Product]
    def get_all(self) -> List[Product]
    def update_stock(self, id: int, delta: int) -> None

class StoreRepository:
    def insert(self, store: Store) -> int
    def get_by_id(self, id: int) -> Optional[Store]
    def get_by_name(self, name: str) -> Optional[Store]
    def get_all(self) -> List[Store]

class TrackedItemRepository:
    def insert(self, item: TrackedItem) -> int
    def get_by_id(self, id: int) -> Optional[TrackedItem]
    def get_by_url(self, url: str) -> Optional[TrackedItem]
    def get_active(self) -> List[TrackedItem]
    def set_last_checked(self, id: int) -> None
```

### 3.4 `app/core/price_calculator.py` - Price Logic

```python
def calculate_volume_price(
    page_price: float,
    items_per_lot: int,
    quantity_size: float,
    quantity_unit: str
) -> tuple[float, str]:
    """
    Calculate price per standard unit.
    Example: €6.00 for 6x330ml = €3.03/L
    """

def compare_prices(
    current: float,
    previous: Optional[float]
) -> PriceComparison:
    """Compare current vs previous price."""
```

---

## 4. Test Plan (TDD)

### 4.1 Model Tests (`tests/test_models.py`)

- `test_product_valid`
- `test_product_target_price_must_be_positive`
- `test_store_valid`
- `test_tracked_item_valid`
- `test_tracked_item_quantity_must_be_positive`

### 4.2 Repository Tests (`tests/test_database.py`)

- `test_product_insert_and_retrieve`
- `test_store_insert_and_retrieve`
- `test_tracked_item_insert_with_relations`
- `test_get_active_tracked_items`
- `test_price_history_with_tracked_item`

### 4.3 Price Calculator Tests (`tests/test_price_calculator.py`)

- `test_volume_price_single_item` (1x1L = price/L)
- `test_volume_price_multipack` (6x330ml = price/L)
- `test_volume_price_kg_conversion`
- `test_compare_prices_drop`
- `test_compare_prices_increase`
- `test_compare_prices_no_previous`

### 4.4 Integration Tests

- `test_cli_with_tracked_item` - Extract price for a tracked URL
- `test_cli_price_comparison` - Run twice and compare

---

## 5. Implementation Order

### Phase 1: Models & Schema (TDD)
1. Write tests for new Pydantic models
2. Implement models in `schemas.py`
3. Write tests for database schema
4. Update `database.py` with new tables

### Phase 2: Repositories (TDD)
1. Write tests for ProductRepository
2. Implement ProductRepository
3. Write tests for StoreRepository
4. Implement StoreRepository
5. Write tests for TrackedItemRepository
6. Implement TrackedItemRepository
7. Update PriceHistoryRepository for new schema

### Phase 3: Price Calculator (TDD)
1. Write tests for volume price calculation
2. Implement `price_calculator.py`
3. Write tests for price comparison
4. Implement comparison logic

### Phase 4: CLI Integration
1. Update `spy.py` to support tracked items
2. Add `--add-product`, `--add-store`, `--track` commands
3. Display price comparison on extraction

### Phase 5: Docker & E2E
1. Run all tests in Docker
2. Manual E2E: Add product, store, track URL, extract twice, verify comparison

---

## 6. CLI Commands (Phase 4)

```bash
# Add a master product
python spy.py add-product "Campina Slagroom" --category "Dairy"

# Add a store
python spy.py add-store "Amazon.nl" --shipping 4.95 --free-threshold 50

# Track a URL
python spy.py track <URL> --product-id 1 --store-id 1 --size 250 --unit ml

# Extract price (existing, but now with comparison)
python spy.py extract <URL>

# List tracked items
python spy.py list
```

---

## 7. Migration Strategy

To preserve existing price_history data:
1. Rename existing `price_history` to `price_history_v1`
2. Create new schema
3. Create a default "Unknown" product and "Unknown" store
4. Migrate old records to new schema with default references
5. Drop `price_history_v1`

---

## 8. Definition of Done

Slice 2 is complete when:
- [ ] All new model tests pass
- [ ] All repository tests pass
- [ ] Price calculator tests pass
- [ ] CLI supports add-product, add-store, track commands
- [ ] Extracting a tracked URL shows price comparison
- [ ] Volume price calculation works for multipacks
- [ ] All tests pass in Docker (ARM64)
- [ ] Documentation updated
