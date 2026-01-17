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
- [x] Extraction logging with error display
- [x] API usage tracking with rate limit management

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

ExtractionLogs (all extraction attempts)
└── tracked_item_id, status, model_used, price, currency, error_message, duration_ms, created_at

ApiUsage (rate limit tracking)
└── model, date, request_count, last_request_at, is_exhausted
```

---

## 3. Page Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard with tracked items |
| GET | `/products` | Products management page |
| GET | `/stores` | Stores management page |
| GET | `/tracked-items` | Tracked items management page |

---

## 4. API Endpoints (JSON)

### Products
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/products` | List all products |
| POST | `/api/products` | Create product |
| GET | `/api/products/{id}` | Get product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |

### Stores
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stores` | List all stores |
| POST | `/api/stores` | Create store |
| GET | `/api/stores/{id}` | Get store |
| PUT | `/api/stores/{id}` | Update store |
| DELETE | `/api/stores/{id}` | Delete store |

### Tracked Items
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tracked-items` | List all tracked items |
| POST | `/api/tracked-items` | Create tracked item |
| GET | `/api/tracked-items/{id}` | Get tracked item |
| PUT | `/api/tracked-items/{id}` | Update tracked item |
| DELETE | `/api/tracked-items/{id}` | Delete tracked item |

### Extraction & Monitoring
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/extract/{id}` | Trigger extraction for item |
| GET | `/api/logs` | Get recent extraction logs |
| GET | `/api/logs/stats` | Get today's extraction stats |
| GET | `/api/usage` | Get API usage per model |

---

## 5. Template Structure

```
app/templates/
├── base.html              # Layout with navigation
├── dashboard.html         # Main dashboard with logs/usage panels
├── products.html          # Products CRUD (Alpine.js)
├── stores.html            # Stores CRUD (Alpine.js)
└── tracked-items.html     # Tracked items CRUD (Alpine.js)
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

## 8. Repository Classes

### 8.1 ProductRepository
- `insert()`, `get_by_id()`, `get_all()`, `update()`, `delete()`, `update_stock()`

### 8.2 StoreRepository
- `insert()`, `get_by_id()`, `get_by_name()`, `get_all()`, `update()`, `delete()`

### 8.3 TrackedItemRepository
- `insert()`, `get_by_id()`, `get_by_url()`, `get_active()`, `update()`, `delete()`, `get_by_product()`, `set_last_checked()`

### 8.4 ExtractionLogRepository
- `insert()`, `get_by_id()`, `get_recent()`, `get_by_item()`, `get_stats()`

---

## 9. Rate Limiting & Fallback

### Gemini Models Configuration
```python
class GeminiModels:
    VISION_EXTRACTION = ModelConfig(model="gemini-2.5-flash", rpd=250)
    VISION_FALLBACK = ModelConfig(model="gemini-2.5-flash-lite", rpd=1000)
```

### Rate Limit Tracker
- Tracks daily usage per model in `api_usage` table
- Auto-marks models as exhausted on 429 errors
- Provides fallback to next available model
- Resets at midnight Pacific time (Google's reset time)

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

### Phase 3: Stores CRUD - COMPLETE
1. [x] Write tests for stores API
2. [x] Implement `/api/stores` endpoints
3. [x] Create stores list template
4. [x] Create stores form template (modal)

### Phase 4: Tracked Items CRUD - COMPLETE
1. [x] Write tests for tracked items update/delete
2. [x] Create tracked item form with dropdowns
3. [x] Implement `/api/tracked-items` endpoints

### Phase 5: Navigation & Polish - COMPLETE
1. [x] Update base template with navigation
2. [x] Add delete confirmation modals
3. [x] Add inline error/success feedback

### Phase 6: Extraction Logging & Usage - COMPLETE
1. [x] Create extraction_logs table and ExtractionLog model
2. [x] Create ExtractionLogRepository with stats
3. [x] Integrate rate limiter into extraction endpoint
4. [x] Add `/api/logs` and `/api/usage` endpoints
5. [x] Add API Usage panel to dashboard
6. [x] Add Recent Extractions panel to dashboard

---

## 11. Definition of Done

Slice 4 is complete when:
- [x] Products: List, Add, Edit, Delete working
- [x] Stores: List, Add, Edit, Delete working
- [x] Tracked Items: Add, Edit, Delete with product/store dropdowns
- [ ] Price History: View per tracked item (deferred to Slice 5)
- [x] Navigation: Menu links to all sections
- [x] Delete requires confirmation
- [x] Form validation with error display
- [x] Extraction logs visible in UI
- [x] API usage/quota visible in UI
- [x] Rate limit fallback working
- [x] All tests pass (157 total)
- [x] Documentation updated

---

## 12. Quick Commands

```bash
# Build and start
docker compose -f infrastructure/docker-compose.yml build
docker compose -f infrastructure/docker-compose.yml up -d

# Run tests
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v

# View logs
docker compose -f infrastructure/docker-compose.yml logs -f

# Access UI
open http://localhost:8000
```

---

## 13. Files Modified/Created

### New Files
- `app/core/gemini.py` - Centralized Gemini model configuration
- `app/core/rate_limiter.py` - Rate limit tracking and fallback
- `app/templates/products.html` - Products management UI
- `app/templates/stores.html` - Stores management UI
- `app/templates/tracked-items.html` - Tracked items management UI

### Modified Files
- `app/storage/database.py` - Added extraction_logs and api_usage tables
- `app/storage/repositories.py` - Added ExtractionLogRepository
- `app/models/schemas.py` - Added ExtractionLog model
- `app/core/vision.py` - Added rate limiter integration, returns (result, model_used)
- `app/api/main.py` - Added CRUD endpoints, logs/usage endpoints
- `app/templates/dashboard.html` - Added API usage and extraction logs panels
- `app/templates/base.html` - Added navigation
- `requirements.txt` - Added pytz

---

**Completed:** January 2026
