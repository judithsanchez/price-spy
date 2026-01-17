# Slice 5: UX Improvements & Bug Fixes

**STATUS: PLANNING**

## Overview

**Objective:** Fix bugs discovered during testing and improve the user experience with smarter forms, better data display, and a dedicated logs dashboard.

**Success Criteria:**
- [ ] Streamlined product+tracked item creation flow
- [ ] Responsive UI with text truncation
- [ ] Store creation bug fixed
- [ ] Admin logs dashboard
- [ ] Price per unit displayed on dashboards
- [ ] All tests pass

---

## Issues & Features

### 1. Streamlined Product Creation

**Problem:** Adding a new product requires navigating to 3 different pages (Products → Stores → Tracked Items).

**Solution:** Combined "Quick Add" flow that:
- Creates product, store, and tracked item in one form
- Auto-detects store from URL domain (e.g., `amazon.nl` → "Amazon.nl")
- Falls back to existing store if domain matches

**Implementation:**
- Add `/quick-add` page with unified form
- Smart store detection: extract domain from URL, check if store exists
- If store doesn't exist, create it automatically
- Single "Track This Product" button

---

### 2. Responsive UI & Text Truncation

**Problem:** Long product names break the layout; can't see Edit/Delete buttons.

**Solution:**
- Truncate long text with `truncate` CSS class
- Add `max-w-*` constraints to table columns
- Show full text on hover (title attribute)
- Test with very long names

**Files to Update:**
- `app/templates/products.html`
- `app/templates/stores.html`
- `app/templates/tracked-items.html`
- `app/templates/dashboard.html`

---

### 3. Store Creation Bug

**Problem:** Store modal submits but nothing happens; store not created.

**Investigation Needed:**
- Check if API endpoint is being called
- Verify modal form submission handler
- Check for JavaScript errors in console
- Test API directly with curl

**Likely Causes:**
- Modal not closing/resetting properly
- API response not handled
- Validation error not displayed

---

### 4. Admin Logs Dashboard

**Problem:** Need to see all logs, not just the summary panel on the dashboard.

**Solution:** Dedicated `/logs` page with:
- Full extraction logs table (last 100 entries)
- Filters: status (success/error), date range, tracked item
- Most recent on top
- Scrollable container
- Auto-refresh option
- Export to CSV (optional)

**API Updates:**
- `GET /api/logs?limit=100&status=error&item_id=1`

**New Template:**
- `app/templates/logs.html`

---

### 5. Tracked Item → Product Relationship

**Problem:** Tracked Items page shows product name but can't navigate to edit the product.

**Solution:**
- Make product name a clickable link to edit product
- Show product details in tracked item view (category, target price)
- Add "View Product" button in tracked item row

**Implementation:**
- Update tracked items template to include product link
- Add product info to tracked items API response

---

### 6. Price Per Unit Display

**Problem:** Dashboard shows total price but not price per unit (EUR/L, EUR/kg).

**Solution:** Calculate and display unit price on:
- Dashboard (main tracked items table)
- Products page (show latest unit price per product)
- Tracked Items page

**Calculation:**
```python
unit_price = (price / items_per_lot) / quantity_size
# Convert to standard unit (L, kg)
# e.g., 250ml → 0.25L, 500g → 0.5kg
```

**Display Format:**
- "€14.11/L" or "€8.50/kg"
- Show both total price and unit price

**Files to Update:**
- `app/api/main.py` - Add unit price to API responses
- `app/templates/dashboard.html` - Display unit price column
- `app/core/price_calculator.py` - Reuse existing logic

---

## Implementation Order

### Phase 1: Bug Fixes
1. [ ] Investigate and fix store creation bug
2. [ ] Add text truncation CSS to all templates
3. [ ] Test with long names

### Phase 2: Price Per Unit
1. [ ] Add unit price calculation to dashboard API
2. [ ] Display unit price in dashboard table
3. [ ] Add to products and tracked items pages

### Phase 3: Admin Logs Dashboard
1. [ ] Create `/logs` page template
2. [ ] Add filters to logs API
3. [ ] Add navigation link
4. [ ] Test with many log entries

### Phase 4: Product-Tracked Item Relationship
1. [ ] Add product link to tracked items page
2. [ ] Include product details in API response
3. [ ] Test navigation flow

### Phase 5: Quick Add Flow (Optional)
1. [ ] Design unified form
2. [ ] Implement store auto-detection
3. [ ] Create `/quick-add` endpoint
4. [ ] Test end-to-end flow

---

## Test Plan

### Bug Fix Tests
- `test_store_creation_works` - API creates store successfully
- `test_long_name_truncates` - UI handles 100+ char names
- `test_buttons_visible_long_names` - Edit/Delete always visible

### Feature Tests
- `test_logs_page_renders` - Logs page loads
- `test_logs_api_filters` - Filters work correctly
- `test_unit_price_calculation` - Price per unit is accurate
- `test_unit_price_displayed` - Shows in dashboard

---

## UI Mockups

### Logs Dashboard
```
┌─────────────────────────────────────────────────────────┐
│  Extraction Logs                          [Refresh]     │
├─────────────────────────────────────────────────────────┤
│  Filters: [All ▼] [Today ▼] [All Items ▼]  [Search]    │
├─────────────────────────────────────────────────────────┤
│  Time     │ Item        │ Status  │ Price   │ Model    │
│  12:34    │ Urea Lotion │ ✓       │ €13.49  │ flash    │
│  12:30    │ Cola 6-pack │ ✗       │ -       │ flash    │
│  12:25    │ Urea Lotion │ ✓       │ €13.49  │ lite     │
│  ...      │             │         │         │          │
└─────────────────────────────────────────────────────────┘
```

### Dashboard with Unit Price
```
┌──────────────────────────────────────────────────────────────────┐
│  Product        │ Store    │ Price    │ Unit Price │ Target     │
│  Urea Lotion    │ Amazon   │ €13.49   │ €14.20/L   │ €15.00/L   │
│  Cola 6-pack    │ AH       │ €6.00    │ €3.03/L    │ €3.00/L    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Definition of Done

Slice 5 is complete when:
- [ ] Store creation works reliably
- [ ] Long names don't break UI
- [ ] Logs dashboard shows all entries with filters
- [ ] Unit price displayed on dashboard
- [ ] Product links work from tracked items
- [ ] All tests pass
- [ ] Documentation updated

---

## Quick Commands

```bash
# Run tests
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v

# View logs
docker compose -f infrastructure/docker-compose.yml logs -f

# Test store API
curl -X POST http://localhost:8000/api/stores \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Store"}'
```

---

**Status: PLANNING** (January 2026)
