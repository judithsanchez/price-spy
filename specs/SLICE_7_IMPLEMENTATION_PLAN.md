# Slice 7: Scheduled Extraction with Smart Queue

**STATUS: COMPLETE** ✅

## Overview

**Objective:** Implement a daily scheduled job that automatically extracts prices for all tracked items, with smart queue management to respect Gemini API rate limits.

**Success Criteria:**

- [x] Scheduler runs daily at configurable time
- [x] Queue processes max 10 concurrent requests to Gemini
- [x] Tracked Items UI shows next scheduled extraction time
- [x] Scheduler status visible in dashboard
- [x] All tests pass (13 new tests)

---

## Features

### 1. APScheduler Integration

**Problem:** No automatic price checking - users must manually trigger extractions.

**Solution:** Use APScheduler to run daily extraction job.

```python
# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

# Run at 08:00 daily (configurable)
scheduler.add_job(
    run_scheduled_extraction,
    CronTrigger(hour=8, minute=0),
    id="daily_extraction",
    replace_existing=True
)
```

**Configuration:**
- `SCHEDULER_ENABLED=true` - Enable/disable scheduler
- `SCHEDULER_HOUR=8` - Hour to run (0-23, default: 8)
- `SCHEDULER_MINUTE=0` - Minute to run (0-59, default: 0)

---

### 2. Smart Queue with Concurrency Limit

**Problem:** Sending too many requests at once will hit Gemini rate limits (15 RPM for Flash).

**Solution:** asyncio.Semaphore to limit concurrent extractions to 10.

```python
# app/core/extraction_queue.py
import asyncio
from typing import List

MAX_CONCURRENT = 10
DELAY_BETWEEN_BATCHES = 5  # seconds

async def process_extraction_queue(items: List[TrackedItem]):
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def extract_with_limit(item):
        async with semaphore:
            return await extract_single_item(item)

    # Process all items with concurrency limit
    tasks = [extract_with_limit(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

**Rate Limit Math:**
- Gemini Flash: 15 requests per minute (RPM)
- With 10 concurrent + delays = ~10 requests per batch
- Safe margin for retries and errors

---

### 3. Tracked Items UI Enhancement

**Problem:** Users can't see when items will be checked next.

**Solution:** Add "Next Check" column to tracked items page.

**UI Changes:**
```
┌───────────────────────────────────────────────────────────────────────────────┐
│  Tracked Items                                                                 │
├───────────────────────────────────────────────────────────────────────────────┤
│  Product        │ Store    │ URL          │ Last Checked  │ Next Check       │
│  ────────────── │ ──────── │ ──────────── │ ───────────── │ ──────────────── │
│  Urea Lotion    │ Amazon   │ amazon.nl... │ Today 14:30   │ Tomorrow 08:00   │
│  Light Strip    │ Amazon   │ amazon.nl... │ Yesterday     │ Tomorrow 08:00   │
│  Rolling Pin    │ Amazon   │ amazon.nl... │ Never         │ Tomorrow 08:00   │
└───────────────────────────────────────────────────────────────────────────────┘
```

**API Changes:**
- Add `next_check_at` to TrackedItemResponse
- Calculate based on scheduler configuration

---

### 4. Scheduler Status Dashboard Panel

**Problem:** Users can't see if scheduler is running or when next job runs.

**Solution:** Add scheduler status panel to dashboard.

**UI Mockup:**
```
┌─ Scheduler ──────────────────────────────────────┐
│  Status: ● Running                                │
│  Next extraction: Tomorrow 08:00 (in 17h 30m)     │
│  Last extraction: Today 08:00 (6h 30m ago)        │
│  Items to check: 3 active                         │
│                                                   │
│  [Run Now]  [Pause]                               │
└───────────────────────────────────────────────────┘
```

**API Endpoints:**
- `GET /api/scheduler/status` - Get scheduler state
- `POST /api/scheduler/run-now` - Trigger immediate run
- `POST /api/scheduler/pause` - Pause scheduler
- `POST /api/scheduler/resume` - Resume scheduler

---

## Database Changes

Add `scheduler_runs` table to track job history:

```sql
CREATE TABLE scheduler_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',  -- running, completed, failed
    items_total INTEGER NOT NULL DEFAULT 0,
    items_success INTEGER NOT NULL DEFAULT 0,
    items_failed INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);
```

---

## Implementation Order

### Phase 1: Core Scheduler ✅
1. [x] Add APScheduler to requirements.txt
2. [x] Create `app/core/scheduler.py` with basic job
3. [x] Create `app/core/extraction_queue.py` with semaphore
4. [x] Integrate scheduler startup with FastAPI lifespan
5. [x] Add environment variable configuration

### Phase 2: Queue Management ✅
1. [x] Implement semaphore-based concurrency limit
2. [x] Add delay between batches
3. [x] Handle individual item failures gracefully
4. [x] Log queue progress

### Phase 3: Database & API ✅
1. [x] Create scheduler_runs table
2. [x] Add SchedulerRunRepository
3. [x] Implement status endpoint
4. [x] Implement run-now endpoint
5. [x] Implement pause/resume endpoints

### Phase 4: UI Updates ✅
1. [x] Add scheduler status panel to dashboard
2. [x] Add Run Now / Pause / Resume buttons
3. [x] Show next scheduled run time
4. [x] Show last run status and results

---

## Test Plan

### Unit Tests

```python
# tests/test_scheduler.py
def test_scheduler_starts_with_app()
def test_scheduler_respects_enabled_flag()
def test_scheduler_uses_configured_time()

# tests/test_extraction_queue.py
def test_queue_limits_concurrency_to_10()
def test_queue_processes_all_items()
def test_queue_continues_on_single_failure()
def test_queue_returns_all_results()

# tests/test_scheduler_api.py
def test_scheduler_status_endpoint()
def test_run_now_triggers_extraction()
def test_pause_stops_scheduler()
def test_resume_restarts_scheduler()
```

### Integration Tests

```python
def test_full_scheduled_extraction_flow()
def test_scheduler_logs_to_scheduler_runs()
def test_ui_shows_next_check_time()
```

---

## Configuration

```bash
# Environment variables
SCHEDULER_ENABLED=true      # Enable/disable scheduler (default: true)
SCHEDULER_HOUR=8            # Hour to run daily (0-23, default: 8)
SCHEDULER_MINUTE=0          # Minute to run (0-59, default: 0)
MAX_CONCURRENT_EXTRACTIONS=10  # Max parallel requests (default: 10)
```

---

## New Files

```
app/
├── core/
│   ├── scheduler.py          # APScheduler setup and job definitions
│   └── extraction_queue.py   # Queue with concurrency management
├── storage/
│   └── repositories.py       # Add SchedulerRunRepository
tests/
├── test_scheduler.py
└── test_extraction_queue.py
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `requirements.txt` | Add `apscheduler>=3.10.0` |
| `app/api/main.py` | Add scheduler startup, new endpoints |
| `app/storage/database.py` | Add scheduler_runs table |
| `app/templates/dashboard.html` | Add scheduler status panel |
| `app/templates/tracked-items.html` | Add "Next Check" column |

---

## Definition of Done

Slice 7 is complete when:

- [x] Scheduler runs daily at configured time
- [x] Max 10 concurrent extractions enforced
- [x] Dashboard shows scheduler status panel with next run time
- [x] Run Now / Pause / Resume buttons work
- [x] scheduler_runs table logs all runs
- [x] All tests pass (13 new tests)
- [x] Documentation updated

---

## Quick Commands

```bash
# Run tests
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v

# Check scheduler status
curl http://localhost:8000/api/scheduler/status

# Trigger immediate run
curl -X POST http://localhost:8000/api/scheduler/run-now

# Pause scheduler
curl -X POST http://localhost:8000/api/scheduler/pause
```

---

**Status: COMPLETE** ✅ (January 2026)
