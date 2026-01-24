# Slice 10: Price History Graphs

**STATUS: COMPLETE**

## Overview

**Objective:** Display price history graphs for each tracked item, allowing users to visualize price trends over time.

**Success Criteria:**

- [x] API endpoint returns price history for a tracked item
- [x] Line chart shows price over time
- [x] Chart is responsive (works on mobile and desktop)
- [x] Can access graph from dashboard and tracked items page
- [x] Graph shows key data points (min, max, current, target)
- [x] All tests pass (223 tests)

---

## Current State

### Existing Infrastructure

**Database:** `price_history` table already stores all price data:
- `price` - Extracted price value
- `currency` - Currency code (EUR, USD, etc.)
- `url` - The tracked URL
- `created_at` - Timestamp

**Repository:** `app/storage/repositories.py`
- `get_by_url(url)` - Returns all price records for a URL (already exists)
- `get_latest_by_url(url)` - Returns most recent price

**Dashboard:** Currently shows only latest price, no historical view.

---

## Technical Approach

### Chart Library: Chart.js

Using Chart.js (lightweight, responsive, works well with Alpine.js):
- CDN: `https://cdn.jsdelivr.net/npm/chart.js`
- ~60KB gzipped
- Built-in responsive support
- Line charts with time axis

---

## Implementation Plan

### Phase 1: API Endpoint

**New Endpoint:** `GET /api/items/{item_id}/price-history`

**Response:**
```json
{
  "item_id": 1,
  "product_name": "Coca-Cola 24x330ml",
  "currency": "EUR",
  "target_price": 15.00,
  "prices": [
    {"date": "2026-01-10", "price": 18.99},
    {"date": "2026-01-12", "price": 17.50},
    {"date": "2026-01-15", "price": 16.99},
    {"date": "2026-01-18", "price": 15.49}
  ],
  "stats": {
    "min": 15.49,
    "max": 18.99,
    "avg": 17.24,
    "current": 15.49,
    "price_drop_pct": -18.4
  }
}
```

**Query Parameters:**
- `days` (optional, default 30) - How many days of history to return

---

### Phase 2: Price History Modal

Add a modal that displays when clicking a "View History" button.

**Location:** Dashboard and Tracked Items pages

**Modal Contents:**
1. Product name header
2. Line chart with price over time
3. Stats summary (min, max, avg, current)
4. Target price line on chart (if set)
5. Close button

**Mobile:** Full-screen modal with responsive chart

---

### Phase 3: Chart Implementation

```html
<!-- Chart.js from CDN -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<div x-data="priceHistoryModal()">
  <!-- Trigger button -->
  <button @click="openModal(itemId)">
    <svg><!-- chart icon --></svg>
  </button>

  <!-- Modal -->
  <div x-show="showModal" class="fixed inset-0 z-50">
    <div class="bg-white rounded-lg p-4 max-w-2xl mx-auto">
      <h3 x-text="productName"></h3>
      <canvas id="priceChart"></canvas>
      <div class="grid grid-cols-4 gap-2 mt-4">
        <div><span class="text-gray-500">Min:</span> €<span x-text="stats.min"></span></div>
        <div><span class="text-gray-500">Max:</span> €<span x-text="stats.max"></span></div>
        <div><span class="text-gray-500">Avg:</span> €<span x-text="stats.avg"></span></div>
        <div><span class="text-gray-500">Current:</span> €<span x-text="stats.current"></span></div>
      </div>
    </div>
  </div>
</div>
```

**Chart Configuration:**
```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: prices.map(p => p.date),
    datasets: [{
      label: 'Price',
      data: prices.map(p => p.price),
      borderColor: 'rgb(59, 130, 246)',
      tension: 0.1
    }, {
      label: 'Target',
      data: prices.map(() => targetPrice),
      borderColor: 'rgb(34, 197, 94)',
      borderDash: [5, 5]
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { type: 'time', time: { unit: 'day' } },
      y: { beginAtZero: false }
    }
  }
});
```

---

## Files to Create/Modify

| File | Change |
|------|--------|
| `app/api/main.py` | Add `/api/items/{item_id}/price-history` endpoint |
| `app/templates/base.html` | Add Chart.js CDN script |
| `app/templates/dashboard.html` | Add "View History" button + modal |
| `app/templates/tracked-items.html` | Add "View History" button + modal |
| `app/templates/partials/price-history-modal.html` | New partial for reusable modal |
| `tests/test_price_history_api.py` | Tests for new API endpoint |

---

## UI Design

### Dashboard - History Button

Add chart icon button next to each item:
```
| Product        | Price  | Target | Status | Actions     |
|----------------|--------|--------|--------|-------------|
| Coca-Cola 24pk | €15.49 | €15.00 | DEAL   | 📊 🔄 Spy   |
```

### Modal Layout (Desktop)

```
┌─────────────────────────────────────────────────┐
│  Coca-Cola 24x330ml - Price History         [X] │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │     📈 Price Chart                       │   │
│  │                                          │   │
│  │   €19 ─                                  │   │
│  │   €18 ─      ╲                           │   │
│  │   €17 ─        ╲___                      │   │
│  │   €16 ─            ╲___                  │   │
│  │   €15 ─ ─ ─ ─ ─ ─ ─ ─ ─ (target)        │   │
│  │        Jan 10  Jan 12  Jan 15  Jan 18    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌──────┬──────┬──────┬──────┐                 │
│  │ Min  │ Max  │ Avg  │ Now  │                 │
│  │€15.49│€18.99│€17.24│€15.49│                 │
│  └──────┴──────┴──────┴──────┘                 │
│                                                 │
│  Price dropped 18.4% from highest              │
└─────────────────────────────────────────────────┘
```

### Modal Layout (Mobile)

Full-screen with larger touch targets, chart takes 60% of height.

---

## Test Plan

### Unit Tests

```python
# tests/test_price_history_api.py

class TestPriceHistoryAPI:
    def test_get_price_history_returns_prices(self):
        """GET /api/items/{id}/price-history returns price list"""

    def test_get_price_history_calculates_stats(self):
        """Response includes min, max, avg, current stats"""

    def test_get_price_history_respects_days_param(self):
        """days=7 returns only last 7 days of prices"""

    def test_get_price_history_item_not_found(self):
        """Returns 404 for non-existent item"""

    def test_get_price_history_no_prices(self):
        """Returns empty list when no price history exists"""

    def test_get_price_history_includes_target_price(self):
        """Response includes target_price from tracked item"""
```

---

## Definition of Done

Slice 10 is complete when:

- [x] API endpoint returns price history with stats
- [x] Chart.js integrated via CDN
- [x] Modal opens from dashboard
- [x] Modal opens from tracked items page
- [x] Chart shows price line and target line
- [x] Stats panel shows min/max/avg/current
- [x] Chart is responsive on mobile
- [x] All new tests pass (8 new tests)
- [x] All existing tests pass (223 total)
- [x] Documentation updated

---

## Future Enhancements (CANCELLED - January 2026)

- ~~Export price history to CSV~~ [CANCELLED]
- ~~Compare prices across multiple stores~~ [CANCELLED]
- ~~Price prediction/forecasting~~ [CANCELLED]
- ~~Customizable date ranges with date picker~~ [CANCELLED]
- ~~Email alerts when price drops below target~~ [CANCELLED]

---

**Status: COMPLETE** (January 2026)
