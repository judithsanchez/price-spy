# Slice 4: Full CRUD UI - Implementation Plan

**STATUS: COMPLETE**

## Overview

**Objective:** Implement complete web UI for managing products, stores, and tracked items. Replace CLI-only workflow with user-friendly forms and navigation.

**Success Criteria:**
- [x] Full CRUD for Products (Create, Read, Update, Delete)
- [x] Full CRUD for Stores
- [x] Full CRUD for Tracked Items with product/store selection
- [x] Navigation menu across all pages
- [ ] Price history view per tracked item (deferred to Slice 5)
- [x] All operations via web UI (CLI remains as fallback)

---

## 1. Current State (Slice 3)

**What we have:**
- Dashboard showing tracked items with prices
- `/api/items` and `/api/items/{id}` endpoints
- `/api/extract/{id}` for triggering extraction
- "Spy Now" button with Alpine.js
- Price status colors (green/red)

**What we need:**
- Products list and form pages
- Stores list and form pages
- Tracked items add/edit with dropdowns
- Price history modal or page
- Navigation header
- Delete confirmations
- Form validation feedback

---

## 2. Data Model Summary

```
Products (master concept)
├── id, name, category, target_price, preferred_unit_size, current_stock

Stores (where to buy)
├── id, name, shipping_cost_standard, free_shipping_threshold, notes

TrackedItems (specific URL to monitor)
├── id, product_id, store_id, url, quantity_size, quantity_unit, items_per_lot
└── References: Product, Store

PriceHistory (extraction results)
└── product_name, price, currency, url, created_at
```

---

## 3. New Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/products` | Products list page |
| GET | `/products/new` | New product form |
| POST | `/products` | Create product |
| GET | `/products/{id}/edit` | Edit product form |
| POST | `/products/{id}` | Update product |
| POST | `/products/{id}/delete` | Delete product |
| GET | `/stores` | Stores list page |
| GET | `/stores/new` | New store form |
| POST | `/stores` | Create store |
| GET | `/stores/{id}/edit` | Edit store form |
| POST | `/stores/{id}` | Update store |
| POST | `/stores/{id}/delete` | Delete store |
| GET | `/tracked/new` | New tracked item form |
| POST | `/tracked` | Create tracked item |
| GET | `/tracked/{id}/edit` | Edit tracked item form |
| POST | `/tracked/{id}` | Update tracked item |
| POST | `/tracked/{id}/delete` | Delete tracked item |
| GET | `/tracked/{id}/history` | Price history page |

---

## 4. API Endpoints (JSON)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/products` | List all products |
| POST | `/api/products` | Create product |
| GET | `/api/products/{id}` | Get product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| GET | `/api/stores` | List all stores |
| POST | `/api/stores` | Create store |
| GET | `/api/stores/{id}` | Get store |
| PUT | `/api/stores/{id}` | Update store |
| DELETE | `/api/stores/{id}` | Delete store |
| DELETE | `/api/items/{id}` | Delete tracked item |
| PUT | `/api/items/{id}` | Update tracked item |
| GET | `/api/items/{id}/history` | Get price history |

---

## 5. Template Structure

```
app/templates/
├── base.html              # Updated with navigation
├── dashboard.html         # Existing (minor updates)
├── products/
│   ├── list.html          # Products table with actions
│   └── form.html          # Add/Edit product form
├── stores/
│   ├── list.html          # Stores table with actions
│   └── form.html          # Add/Edit store form
├── tracked/
│   ├── form.html          # Add/Edit tracked item (with dropdowns)
│   └── history.html       # Price history table/chart
└── partials/
    ├── nav.html           # Navigation component
    ├── flash.html         # Flash messages
    └── confirm_delete.html # Delete confirmation modal
```

---

## 6. Navigation Design

```html
<nav>
  Logo: Price Spy
  Links: Dashboard | Products | Stores | Tracked Items
</nav>
```

Active link highlighted based on current route.

---

## 7. Form Designs

### 7.1 Product Form

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Name | text | Yes | min 1 char |
| Category | text | No | - |
| Target Price | number | No | > 0 |
| Preferred Unit Size | text | No | e.g., "250ml" |

### 7.2 Store Form

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Name | text | Yes | min 1 char, unique |
| Shipping Cost | number | No | >= 0 |
| Free Shipping Threshold | number | No | > 0 |
| Notes | textarea | No | - |

### 7.3 Tracked Item Form

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Product | dropdown | Yes | existing product |
| Store | dropdown | Yes | existing store |
| URL | url | Yes | valid URL |
| Size | number | Yes | > 0 |
| Unit | dropdown | Yes | ml, L, g, kg, piece |
| Items per Lot | number | No | >= 1 |

---

## 8. Repository Updates

### 8.1 ProductRepository

```python
def update(self, product_id: int, product: Product) -> None
def delete(self, product_id: int) -> None
```

### 8.2 StoreRepository

```python
def update(self, store_id: int, store: Store) -> None
def delete(self, store_id: int) -> None
```

### 8.3 TrackedItemRepository

```python
def update(self, item_id: int, item: TrackedItem) -> None
def delete(self, item_id: int) -> None
def get_by_product(self, product_id: int) -> List[TrackedItem]
```

---

## 9. Test Plan (TDD)

### 9.1 Repository Tests

- `test_product_update`
- `test_product_delete`
- `test_store_update`
- `test_store_delete`
- `test_tracked_item_update`
- `test_tracked_item_delete`

### 9.2 API Tests

- `test_api_products_list`
- `test_api_products_create`
- `test_api_products_update`
- `test_api_products_delete`
- `test_api_stores_list`
- `test_api_stores_create`
- `test_api_price_history`

### 9.3 UI Tests

- `test_products_page_renders`
- `test_products_form_creates`
- `test_stores_page_renders`
- `test_tracked_form_has_dropdowns`
- `test_navigation_links_work`

---

## 10. Implementation Order

### Phase 1: Repository Updates (TDD) - COMPLETE
1. [x] Write tests for update/delete methods
2. [x] Implement ProductRepository.update/delete
3. [x] Implement StoreRepository.update/delete
4. [x] Implement TrackedItemRepository.update/delete

### Phase 2: Products CRUD - COMPLETE
1. [x] Write tests for products API
2. [x] Implement `/api/products` endpoints
3. [x] Create products list template
4. [x] Create products form template (modal)
5. [x] Implement form routes

### Phase 3: Stores CRUD - COMPLETE
1. [x] Write tests for stores API
2. [x] Implement `/api/stores` endpoints
3. [x] Create stores list template
4. [x] Create stores form template (modal)
5. [x] Implement form routes

### Phase 4: Tracked Items CRUD - COMPLETE
1. [x] Write tests for tracked items update/delete
2. [x] Create tracked item form with dropdowns
3. [x] Implement form routes
4. [ ] Add price history view (deferred to Slice 5)

### Phase 5: Navigation & Polish - COMPLETE
1. [x] Update base template with navigation
2. [x] Add delete confirmation modals
3. [x] Test all flows end-to-end (143 tests pass)

---

## 11. UI Components (Tailwind)

### 11.1 Table Style

```html
<table class="w-full bg-white rounded-lg shadow">
  <thead class="bg-gray-50">
    <tr>
      <th class="px-4 py-3 text-left">Column</th>
    </tr>
  </thead>
  <tbody class="divide-y">
    <tr class="hover:bg-gray-50">
      <td class="px-4 py-3">Data</td>
    </tr>
  </tbody>
</table>
```

### 11.2 Form Style

```html
<form class="bg-white rounded-lg shadow p-6 space-y-4">
  <div>
    <label class="block text-sm font-medium text-gray-700">Field</label>
    <input type="text" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
  </div>
  <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">
    Save
  </button>
</form>
```

### 11.3 Button Styles

```html
<!-- Primary -->
<button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">

<!-- Danger -->
<button class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">

<!-- Secondary -->
<button class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded">
```

---

## 12. Flash Messages

```python
# In route handler
from fastapi import Request
from starlette.responses import RedirectResponse

@app.post("/products")
async def create_product(request: Request, ...):
    # Create product
    return RedirectResponse(url="/products?message=Product+created", status_code=303)
```

```html
<!-- In template -->
{% if request.query_params.get('message') %}
<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
  {{ request.query_params.get('message') }}
</div>
{% endif %}
```

---

## 13. Definition of Done

Slice 4 is complete when:
- [ ] Products: List, Add, Edit, Delete working
- [ ] Stores: List, Add, Edit, Delete working
- [ ] Tracked Items: Add, Edit, Delete with product/store dropdowns
- [ ] Price History: View per tracked item
- [ ] Navigation: Menu links to all sections
- [ ] Flash messages show operation results
- [ ] Delete requires confirmation
- [ ] Form validation with error display
- [ ] All new tests pass (20+)
- [ ] Total test count 120+
- [ ] Documentation updated

---

## 14. Quick Commands

```bash
# Build and start
docker compose -f infrastructure/docker-compose.yml build
docker compose -f infrastructure/docker-compose.yml up -d

# Run tests
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v

# View logs
docker compose -f infrastructure/docker-compose.yml logs -f
```

**Status: PLANNING** (January 2026)
