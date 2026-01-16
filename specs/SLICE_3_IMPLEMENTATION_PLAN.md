# Slice 3: Service & UI Transition - Implementation Plan

## Overview

**Objective:** Transition from CLI-only to a persistent Service-Oriented Architecture (SOA) with a Web UI for manual job triggering and visual data management.

**Success Criteria:**
- FastAPI server running on port 8000
- Dashboard showing all tracked items with price status
- "Spy Now" button triggers extraction without page refresh
- Screenshots displayed in UI
- Gemini extraction uses structured outputs (guaranteed JSON)
- All existing tests still pass + new API/UI tests

---

## 1. Current State (Slice 2)

**What we have:**
- CLI tool (`spy.py`) with commands: `extract`, `add-product`, `add-store`, `track`, `list`
- Gemini vision extraction with prompt-based JSON parsing
- SQLite database with: `products`, `stores`, `tracked_items`, `price_history`, `error_log`
- 70 passing tests
- Docker container running pytest by default

**What we need:**
- FastAPI web server as default entry point
- Jinja2 templates for server-side rendering
- Alpine.js for interactive "Spy Now" buttons
- Structured outputs from Gemini (guaranteed valid JSON)
- Screenshot storage and display
- Background task execution for extractions

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Container                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    FastAPI (uvicorn)                      │  │
│  │                     localhost:8000                        │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  Routes:                                                  │  │
│  │  GET  /              → Dashboard (Jinja2)                 │  │
│  │  GET  /api/items     → JSON list of tracked items         │  │
│  │  POST /api/extract   → Trigger extraction (background)    │  │
│  │  GET  /screenshots/  → Static file serving                │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  Core Modules (unchanged):                                │  │
│  │  - app/core/browser.py (Playwright)                       │  │
│  │  - app/core/vision.py (Gemini + Structured Outputs)       │  │
│  │  - app/storage/* (SQLite repositories)                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                    ┌─────────▼─────────┐                        │
│                    │  data/pricespy.db │                        │
│                    │  screenshots/*.png│                        │
│                    └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. New File Structure

```
app/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory
│   ├── routes.py            # API endpoints
│   └── dependencies.py      # Database dependency injection
├── templates/
│   ├── base.html            # Base layout with Tailwind
│   ├── dashboard.html       # Main dashboard view
│   └── partials/
│       └── item_row.html    # HTMX/Alpine partial for item row
├── static/
│   └── (empty - using CDN)
├── core/
│   ├── vision.py            # UPDATED: Structured outputs
│   └── extraction.py        # NEW: Extraction service
screenshots/                  # Stored screenshots (mounted volume)
```

---

## 4. Infrastructure Changes

### 4.1 Dockerfile Updates

```dockerfile
# Change default CMD from pytest to uvicorn
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 docker-compose.yml Updates

```yaml
services:
  price-spy:
    build:
      context: ..
      dockerfile: infrastructure/Dockerfile
    container_name: price_spy
    env_file:
      - ../.env
    ports:
      - "8000:8000"           # NEW: Expose web UI
    volumes:
      - ../tests/screenshots:/app/tests/screenshots
      - ../data:/app/data
      - ../screenshots:/app/screenshots  # NEW: Screenshot storage
    stdin_open: true
    tty: true
```

### 4.3 requirements.txt Additions

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
jinja2>=3.1.0
python-multipart>=0.0.6
```

---

## 5. Structured Extraction Engine

### 5.1 New Schema: `ExtractionResult`

```python
class ExtractionResult(BaseModel):
    """Guaranteed structured output from Gemini."""

    price: float = Field(..., gt=0, description="Numeric price value")
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    is_available: bool = Field(default=True, description="In stock status")
    product_name: str = Field(..., min_length=1)
    store_name: Optional[str] = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 5.2 Gemini Structured Output API

Use Gemini's native `response_mime_type: "application/json"` with `response_schema`:

```python
async def extract_with_structured_output(
    image_bytes: bytes,
    api_key: str
) -> ExtractionResult:
    """Extract price using Gemini structured outputs."""

    payload = {
        "contents": [...],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "price": {"type": "number"},
                    "currency": {"type": "string"},
                    "is_available": {"type": "boolean"},
                    "product_name": {"type": "string"},
                    "store_name": {"type": "string"}
                },
                "required": ["price", "currency", "is_available", "product_name"]
            }
        }
    }
```

---

## 6. FastAPI Backend

### 6.1 Main Application (`app/api/main.py`)

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Price Spy", version="0.3.0")

# Mount static files
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Templates
templates = Jinja2Templates(directory="app/templates")
```

### 6.2 Routes (`app/api/routes.py`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard HTML page |
| GET | `/api/items` | JSON list of all tracked items with latest prices |
| GET | `/api/items/{id}` | Single item details with price history |
| POST | `/api/extract/{id}` | Trigger extraction for tracked item |
| GET | `/api/health` | Health check endpoint |

### 6.3 Background Task Execution

```python
from fastapi import BackgroundTasks

@router.post("/api/extract/{item_id}")
async def trigger_extraction(
    item_id: int,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_db)
):
    """Queue extraction as background task."""
    background_tasks.add_task(run_extraction, item_id, db)
    return {"status": "queued", "item_id": item_id}
```

---

## 7. Web UI (Jinja2 + Alpine.js)

### 7.1 Dashboard Layout

```html
<!-- dashboard.html -->
<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Price Spy Dashboard</h1>

  <table class="w-full">
    <thead>
      <tr>
        <th>Product</th>
        <th>Store</th>
        <th>Current Price</th>
        <th>Target</th>
        <th>Status</th>
        <th>Screenshot</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      {% for item in items %}
      <tr x-data="{ loading: false }">
        <td>{{ item.product_name }}</td>
        <td>{{ item.store_name }}</td>
        <td>{{ item.currency }} {{ item.price }}</td>
        <td>{{ item.target_price or '-' }}</td>
        <td>
          {% if item.is_below_target %}
            <span class="text-green-600">✓ Below target</span>
          {% else %}
            <span class="text-red-600">✗ Above target</span>
          {% endif %}
        </td>
        <td>
          <img src="/screenshots/{{ item.id }}.png" class="w-24 h-auto" />
        </td>
        <td>
          <button
            @click="loading = true; fetch('/api/extract/{{ item.id }}', {method: 'POST'}).then(() => location.reload())"
            :disabled="loading"
            class="bg-blue-500 text-white px-3 py-1 rounded">
            <span x-show="!loading">Spy Now</span>
            <span x-show="loading">⏳</span>
          </button>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
```

### 7.2 Price Status Logic

```python
class DashboardItem(BaseModel):
    """View model for dashboard."""
    id: int
    product_name: str
    store_name: str
    price: Optional[float]
    currency: str
    target_price: Optional[float]
    unit_price: Optional[float]
    unit: Optional[str]
    screenshot_path: Optional[str]
    last_checked: Optional[datetime]

    @property
    def is_below_target(self) -> bool:
        if not self.target_price or not self.price:
            return False
        return self.price <= self.target_price
```

---

## 8. Screenshot Management

### 8.1 Storage Strategy

- Screenshots saved to `screenshots/{tracked_item_id}.png`
- Overwritten on each extraction (only keep latest)
- Mounted as Docker volume for persistence

### 8.2 Updated Browser Module

```python
async def capture_screenshot(url: str, save_path: Optional[str] = None) -> bytes:
    """Capture screenshot and optionally save to disk."""
    # ... existing capture logic ...

    if save_path:
        with open(save_path, 'wb') as f:
            f.write(screenshot_bytes)

    return screenshot_bytes
```

---

## 9. Test Plan (TDD)

### 9.1 API Tests (`tests/test_api.py`)

```python
# Test health endpoint
def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# Test dashboard renders
def test_dashboard_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Price Spy Dashboard" in response.text

# Test items endpoint
def test_get_items_empty(client, db):
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.json() == []

# Test items with data
def test_get_items_with_data(client, db_with_items):
    response = client.get("/api/items")
    items = response.json()
    assert len(items) > 0
    assert "product_name" in items[0]

# Test extract trigger
def test_trigger_extraction(client, db_with_items, mock_gemini):
    response = client.post("/api/extract/1")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"
```

### 9.2 Structured Output Tests (`tests/test_structured_vision.py`)

```python
# Test structured output parsing
def test_structured_extraction_valid():
    raw = '{"price": 12.99, "currency": "EUR", "is_available": true, "product_name": "Test"}'
    result = ExtractionResult.model_validate_json(raw)
    assert result.price == 12.99

# Test schema validation
def test_structured_extraction_missing_required():
    raw = '{"price": 12.99}'  # missing required fields
    with pytest.raises(ValidationError):
        ExtractionResult.model_validate_json(raw)
```

### 9.3 UI Integration Tests (`tests/test_ui.py`)

```python
# Test dashboard shows items
def test_dashboard_shows_tracked_items(client, db_with_items):
    response = client.get("/")
    assert "Campina Slagroom" in response.text

# Test price status colors
def test_dashboard_price_below_target(client, db_with_item_below_target):
    response = client.get("/")
    assert "text-green-600" in response.text

# Test spy button present
def test_dashboard_has_spy_buttons(client, db_with_items):
    response = client.get("/")
    assert "Spy Now" in response.text
```

---

## 10. Implementation Order

### Phase 1: Infrastructure (TDD)
1. Write test for health endpoint
2. Create FastAPI app with health endpoint
3. Update Dockerfile (uvicorn entry point)
4. Update docker-compose.yml (port 8000)
5. Add new dependencies to requirements.txt

### Phase 2: Structured Outputs (TDD)
1. Write tests for `ExtractionResult` model
2. Implement model in `schemas.py`
3. Write tests for structured Gemini API call
4. Update `vision.py` with `response_mime_type`

### Phase 3: API Endpoints (TDD)
1. Write tests for `/api/items` endpoint
2. Implement items endpoint
3. Write tests for `/api/extract/{id}` endpoint
4. Implement extraction trigger with background tasks
5. Implement screenshot saving

### Phase 4: Web UI (TDD)
1. Write test for dashboard rendering
2. Create base template with Tailwind CDN
3. Create dashboard template
4. Implement dashboard route with data
5. Add Alpine.js for Spy Now button

### Phase 5: Integration & Polish
1. Run all tests in Docker
2. Manual E2E: Add item, view dashboard, click Spy Now
3. Verify screenshot appears in UI
4. Test price status colors

---

## 11. Database Schema Updates

### 11.1 Add `is_available` to price_history

```sql
ALTER TABLE price_history ADD COLUMN is_available BOOLEAN DEFAULT 1;
```

### 11.2 Add `screenshot_path` to tracked_items

```sql
ALTER TABLE tracked_items ADD COLUMN screenshot_path TEXT;
```

---

## 12. CLI Preservation

The CLI (`spy.py`) remains functional for:
- Quick testing: `python spy.py extract <URL>`
- Batch scripts: `python spy.py list`
- Database management: `python spy.py add-product ...`

Both CLI and Web UI share the same core modules.

---

## 13. Definition of Done

Slice 3 is complete when:
- [ ] FastAPI server starts with `uvicorn` on port 8000
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Dashboard renders with Jinja2 + Tailwind CSS
- [ ] `/api/items` returns JSON list of tracked items
- [ ] "Spy Now" button triggers extraction via Alpine.js
- [ ] Gemini uses structured outputs (guaranteed JSON)
- [ ] `ExtractionResult` includes `is_available` field
- [ ] Screenshots saved and displayed in UI
- [ ] Price status shows green (below target) or red (above)
- [ ] All existing tests pass (70+)
- [ ] New API/UI tests pass (15+)
- [ ] Works in Docker on ARM64 (Raspberry Pi 5)
- [ ] Documentation updated

---

## 14. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Gemini structured outputs not supported | Fallback to Instructor library |
| Background tasks blocking | Use `asyncio.create_task` for non-blocking |
| Screenshot storage fills disk | Implement cleanup for old screenshots |
| ARM64 compatibility | Test on Pi early in Phase 1 |

---

## 15. Quick Reference: Docker Commands

```bash
# Build with new dependencies
docker compose -f infrastructure/docker-compose.yml build

# Start web server
docker compose -f infrastructure/docker-compose.yml up -d

# View logs
docker compose -f infrastructure/docker-compose.yml logs -f

# Run tests
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v

# Access shell
docker compose -f infrastructure/docker-compose.yml run --rm price-spy bash
```

**Status: PLANNING** (January 2026)
