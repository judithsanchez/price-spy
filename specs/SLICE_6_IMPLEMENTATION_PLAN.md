# Slice 6: Scheduled Extraction & Price Drop Alerts

**STATUS: IN PROGRESS** (January 2026)

## Overview

**Objective:** Automate daily price checking with a scheduled job and alert users when prices drop to or below their target.

**Success Criteria:**

- [ ] Scheduled job runs daily and extracts prices for all active items
- [x] Price drop alerts visible on dashboard when price ≤ target (DEAL badge + alert banner)
- [x] CLI command to trigger batch extraction manually (`python -m app.cli extract-all`)
- [x] Test data seeding for UI testing (`python -m app.cli seed-test-data`)
- [x] API endpoint for batch extraction (`POST /api/extract/all`)
- [x] 179 tests passing

---

## Features

### 1. Scheduled Extraction Job

**Problem:** Users must manually click "Spy Now" for each item.

**Solution:** A scheduled job that:
- Runs once daily (configurable time)
- Extracts prices for all active tracked items
- Respects rate limits (uses existing fallback logic)
- Logs all extractions (success/error)

**Implementation Options:**

| Option | Pros | Cons |
|--------|------|------|
| APScheduler | Python-native, runs in same process | Requires app to be running |
| System cron | Simple, OS-level | Needs separate script, Docker config |
| Docker cron | Container-based | More complex setup |

**Chosen:** APScheduler - integrates with FastAPI, no external dependencies.

**New Files:**
- `app/core/scheduler.py` - Scheduler setup and job definitions
- `app/core/batch_extraction.py` - Batch extraction logic

**API Endpoints:**
- `POST /api/extract/all` - Trigger batch extraction manually
- `GET /api/scheduler/status` - Check scheduler status

---

### 2. Price Drop Alerts (UI)

**Problem:** No visual indication when a price drops to/below target.

**Solution:** Visual alerts on dashboard:
- Green badge/banner when price ≤ target
- Pulsing animation to draw attention
- "Deal!" or "Target reached!" label
- Optional: Sound notification (browser)

**UI Mockup:**
```
┌──────────────────────────────────────────────────────────────────────────┐
│  Product        │ Store    │ Price      │ Unit Price │ Target   │ Status │
│  ────────────── │ ──────── │ ────────── │ ────────── │ ──────── │ ────── │
│  Urea Lotion    │ Amazon   │ €12.99     │ €13.67/L   │ €15.00   │ 🎉 DEAL │
│  Cola 6-pack    │ AH       │ €6.00      │ €3.03/L    │ €3.00/L  │ Above   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Files to Update:**
- `app/templates/dashboard.html` - Add deal indicator
- `app/static/css/` - Animation styles (optional)

---

### 3. CLI Batch Extraction

**Problem:** Need way to trigger batch extraction from command line (for testing, manual runs).

**Solution:** CLI command:
```bash
python -m app.cli extract-all
# or
docker compose run --rm price-spy python -m app.cli extract-all
```

**New Files:**
- `app/cli.py` - CLI commands module

---

### 4. Test Data Seeding

**Problem:** Can't test price drop UI without real price drops.

**Solution:** Seed command that creates test data:
```bash
python -m app.cli seed-test-data
```

Creates:
- 3 products with varying target prices
- 2 stores
- 3 tracked items
- Price history with some prices below target

**New Files:**
- `app/core/seeder.py` - Test data generation

---

### 5. Quick Add Flow (Deferred from Slice 5)

**Problem:** Adding a new product requires 3 pages.

**Solution:** Combined form at `/quick-add`:
- Single form: URL + product name + target price
- Auto-detect store from URL domain
- Create product, store (if new), tracked item in one step

**Implementation:**
- `GET /quick-add` - Render form
- `POST /api/quick-add` - Process form

**Deferred to:** Future slice (nice-to-have, not blocking)

---

## Implementation Order

### Phase 1: Price Drop UI ✅
1. [x] Update dashboard template with DEAL badge
2. [x] Add CSS animation for deal badge (animate-pulse)
3. [x] Add deal alert banner at top of dashboard
4. [x] Tests: 6 tests in test_price_alerts.py

### Phase 2: Test Data Seeding ✅
1. [x] Create `app/core/seeder.py`
2. [x] Add `seed-test-data` CLI command (`python -m app.cli seed-test-data`)
3. [x] Seed includes: 3 products, 2 stores, 3 tracked items, price history
4. [x] Tests: 7 tests in test_seeder.py

### Phase 3: Batch Extraction ✅
1. [x] Create `app/core/batch_extraction.py`
2. [x] Add `POST /api/extract/all` endpoint
3. [x] Add `extract-all` CLI command (`python -m app.cli extract-all`)
4. [x] Handle rate limits across batch (uses existing RateLimitTracker)
5. [x] Tests: 6 tests in test_batch_extraction.py

### Phase 4: Scheduler (TODO)
1. [ ] Add APScheduler dependency
2. [ ] Create `app/core/scheduler.py`
3. [ ] Configure daily job (default: 08:00)
4. [ ] Add scheduler status endpoint
5. [ ] Environment variable for schedule time

---

## Database Changes

None required - uses existing tables:
- `extraction_logs` - Already tracks all extractions
- `price_history` - Already stores historical prices
- `tracked_items` - Already has `is_active` flag

---

## Test Plan

### Unit Tests

```python
# tests/test_batch_extraction.py
def test_batch_extracts_all_active_items()
def test_batch_skips_inactive_items()
def test_batch_continues_on_single_item_failure()
def test_batch_respects_rate_limits()

# tests/test_scheduler.py
def test_scheduler_starts_on_app_startup()
def test_scheduler_job_runs_at_configured_time()
def test_scheduler_status_endpoint()

# tests/test_seeder.py
def test_seed_creates_products()
def test_seed_creates_price_history()
def test_seed_includes_price_drops()
```

### Integration Tests

```python
# tests/test_price_drop_ui.py
def test_dashboard_shows_deal_badge_when_price_below_target()
def test_dashboard_shows_normal_status_when_price_above_target()
def test_dashboard_handles_no_target_price()
```

---

## Configuration

New environment variables:

```bash
# Scheduler settings
SCHEDULER_ENABLED=true           # Enable/disable scheduler
SCHEDULER_TIME=08:00             # Time to run daily (HH:MM, UTC)
SCHEDULER_TIMEZONE=Europe/Amsterdam  # Optional timezone

# Batch extraction
BATCH_DELAY_SECONDS=5            # Delay between items (rate limit protection)
```

---

## UI Mockups

### Dashboard with Deal Badge

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Dashboard                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ DEAL ALERT ──────────────────────────────────────────────────────────┐  │
│  │ 🎉 Eucerin Urea Lotion is at target price! €12.99 (target: €15.00)    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Product        │ Store    │ Price    │ Unit Price │ Target   │ Status      │
│  ────────────── │ ──────── │ ──────── │ ────────── │ ──────── │ ─────────── │
│  Urea Lotion    │ Amazon   │ €12.99   │ €13.67/L   │ €15.00   │ ✓ DEAL      │
│  Cola 6-pack    │ AH       │ €6.00    │ €3.03/L    │ €3.00/L  │ Above       │
│  Shampoo        │ Bol.com  │ €8.50    │ €17.00/L   │ -        │ -           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Scheduler Status Panel

```
┌─ Scheduler ──────────────────────────────┐
│  Status: Running                          │
│  Next run: Today 08:00 (in 3h 24m)        │
│  Last run: Yesterday 08:00 (24h ago)      │
│  Items checked: 5                         │
│  [Run Now]                                │
└───────────────────────────────────────────┘
```

---

## Definition of Done

Slice 6 is complete when:

- [x] Dashboard shows deal badge when price ≤ target
- [x] Deal alert banner at top of dashboard
- [x] `seed-test-data` CLI creates test scenarios
- [x] `extract-all` CLI triggers batch extraction
- [x] `POST /api/extract/all` API endpoint
- [ ] Scheduler runs daily extraction automatically (deferred)
- [ ] Scheduler status visible in dashboard (deferred)
- [x] All tests pass (179 tests)
- [x] Documentation updated

---

## New Files Created

- `app/core/seeder.py` - Test data generation
- `app/core/batch_extraction.py` - Batch extraction logic
- `app/cli.py` - CLI commands module
- `tests/test_price_alerts.py` - 6 tests for DEAL badge UI
- `tests/test_seeder.py` - 7 tests for seeder
- `tests/test_batch_extraction.py` - 6 tests for batch extraction

## Files Modified

- `app/api/main.py` - Added `is_deal` to dashboard, `POST /api/extract/all`
- `app/templates/dashboard.html` - DEAL badge, alert banner

---

## Dependencies (Future)

```
# requirements.txt additions (when scheduler is implemented)
apscheduler>=3.10.0
```

---

## Quick Commands

```bash
# Run tests
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v

# Seed test data
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python -m app.cli seed-test-data

# Manual batch extraction
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python -m app.cli extract-all

# Trigger batch via API
curl -X POST http://localhost:8000/api/extract/all
```

---

**Status: IN PROGRESS** (January 2026) - Phases 1-3 complete, Phase 4 (Scheduler) deferred
