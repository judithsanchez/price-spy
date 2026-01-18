# Price Spy Roadmap

## Slice 1: The Manual Spy (Complete)
* **Goal:** Proof of Concept for Visual Scraping.
* **Status:** Complete.
* **Scope:** Manual CLI trigger, Chromium/Playwright stealth browser, Gemini 2.5 Flash Vision analysis, Pydantic validation, SQLite persistence (price_history, error_log), structured JSON logging.
* **Success Criteria:**
  - [x] Verified JSON response from Amazon.nl (100% confidence)
  - [x] No CAPTCHA in 5 consecutive runs
  - [x] 31 unit/integration tests passing in Docker

## Slice 2: Full Data Model (Complete)
* **Goal:** Implement complete database schema for product tracking and price comparison.
* **Status:** Complete.
* **Scope:**
    * Implemented full schema: `products`, `stores`, `tracked_items` tables
    * Link tracked URLs to master products and stores
    * Price comparison logic: "Last Price" vs "Current Price"
    * Volume/unit price calculation for multipacks
    * CLI commands: add-product, add-store, track, list
* **Success Criteria:**
  - [x] Track multiple URLs for the same product across different stores
  - [x] Calculate and display price per unit (e.g., EUR/L)
  - [x] 70 tests passing in Docker

## Slice 3: Web Dashboard (Complete)
* **Goal:** Simple web interface to view and trigger extractions.
* **Status:** Complete.
* **Scope:**
    * FastAPI web server with Jinja2 templates
    * Dashboard showing tracked items with prices
    * "Spy Now" button with real-time feedback
    * Price status indicators (above/below target)
    * Screenshot thumbnails
* **Success Criteria:**
  - [x] Access dashboard at http://localhost:8000
  - [x] Trigger extraction via UI
  - [x] See success/error feedback inline

## Slice 4: Full CRUD UI (Complete)
* **Goal:** Complete web interface for managing all entities.
* **Status:** Complete.
* **Scope:**
    * Full CRUD for Products, Stores, Tracked Items via web UI
    * Navigation menu across all pages
    * Delete confirmations with modals
    * Extraction logging (success/error tracking)
    * API usage tracking with rate limit management
    * Auto-fallback between Gemini models on quota exhaustion
    * API endpoints for logs and usage stats
    * Dashboard panels for API usage and recent extractions
* **Success Criteria:**
  - [x] Products: List, Add, Edit, Delete working
  - [x] Stores: List, Add, Edit, Delete working
  - [x] Tracked Items: CRUD with product/store dropdowns
  - [x] Extraction logs visible in dashboard
  - [x] API usage/quota visible in dashboard
  - [x] 157 tests passing

## Slice 5: UX Improvements & Bug Fixes (Complete)
* **Goal:** Fix bugs and improve user experience.
* **Status:** Complete.
* **Scope:**
    * Fixed store/product/tracked-item creation (error handling)
    * Text truncation for long names
    * Admin logs dashboard with filters
    * Unit price display on dashboard
    * Product links from tracked items
* **Success Criteria:**
  - [x] Store creation works reliably
  - [x] Long names don't break UI
  - [x] Logs dashboard shows all entries with filters
  - [x] Unit price displayed on dashboard
  - [x] 160 tests passing

## Slice 6: Batch Extraction & Price Drop Alerts (Complete)
* **Goal:** Batch extraction with visual price drop alerts.
* **Status:** Complete.
* **Scope:**
    * Batch extraction for all active items
    * Price drop alerts on dashboard (DEAL badge + alert banner)
    * CLI commands for batch extraction and test data seeding
* **Success Criteria:**
  - [x] Dashboard shows "DEAL" badge when price ≤ target
  - [x] CLI commands: `extract-all`, `seed-test-data`
  - [x] API endpoint: `POST /api/extract/all`
  - [x] 179 tests passing

## Slice 7: Scheduled Extraction with Smart Queue (Complete)
* **Goal:** Automated daily price checks with smart queue management.
* **Status:** Complete.
* **Scope:**
    * APScheduler integration for daily extraction
    * Smart queue with concurrency limit (max 10 concurrent)
    * Scheduler status panel in dashboard
    * Run Now / Pause / Resume controls
    * Skip items already checked today (manual "Spy Now")
* **Success Criteria:**
  - [x] Scheduler runs daily at configurable time (default 08:00)
  - [x] Max 10 concurrent extractions enforced
  - [x] Dashboard shows scheduler status with next run time
  - [x] Run Now / Pause / Resume buttons work
  - [x] scheduler_runs table logs all runs
  - [x] 199 tests passing

## Slice 8: Daily Email Reports (Complete)
* **Goal:** Receive daily email summary after scheduled extraction.
* **Status:** Complete.
* **Scope:**
    * Email report sent after each scheduler run
    * HTML and plain text email templates
    * Deals highlighted prominently
    * Errors listed for troubleshooting
    * Configurable SMTP settings via environment variables
    * Test email endpoint for configuration verification
* **Success Criteria:**
  - [x] Email sent after each scheduler run with results
  - [x] Deals prominently highlighted in email
  - [x] Both HTML and plain text versions work
  - [x] Email skipped when no items checked
  - [x] Gmail SMTP setup documented
  - [x] Test email endpoint works
  - [x] 215 tests passing

## Slice 9: Responsive UI for Web & Mobile (Planned)
* **Goal:** Make the entire UI fully responsive for all devices.
* **Status:** Planned.
* **Scope:**
    * Mobile hamburger menu navigation
    * Horizontal scrolling tables on small screens
    * Card layouts for list pages on mobile
    * Full-screen modals on mobile
    * Touch-friendly button sizes (44px minimum)
    * Responsive form grids
* **Success Criteria:**
  - [ ] All pages usable on mobile (320px - 480px)
  - [ ] All pages usable on tablet (768px - 1024px)
  - [ ] No horizontal page overflow
  - [ ] All existing tests pass

---

## Future Enhancements (Planned)

### Price History View
* View price history graph/table per tracked item
* Trend visualization over time

### Quick Add Flow
* Combined form to add product + tracked item in one step
* Auto-detect store from URL domain

### Home Assistant Integration
* Webhooks for price drop notifications
* MQTT integration for smart home automations

---

## Tech Stack

* **Backend:** Python 3.11, FastAPI, SQLite
* **Browser:** Playwright with Chromium (stealth mode)
* **AI:** Google Gemini 2.5 Flash/Lite (structured output)
* **Frontend:** Jinja2 templates, Tailwind CSS, Alpine.js
* **Scheduler:** APScheduler (daily extraction)
* **Email:** SMTP (Gmail compatible)
* **Infrastructure:** Docker, Docker Compose

---

## Current Test Count: 215 tests
