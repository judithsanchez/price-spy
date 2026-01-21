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

## Slice 9: Responsive UI for Web & Mobile (Complete)
* **Goal:** Make the entire UI fully responsive for all devices.
* **Status:** Complete.
* **Scope:**
    * Mobile hamburger menu navigation with Alpine.js
    * Horizontal scrolling tables on small screens
    * Card layouts for list pages on mobile (Products, Stores, Tracked Items, Logs)
    * Slide-up modals on mobile with transitions
    * Touch-friendly button sizes (44px minimum)
    * Responsive form grids
    * Responsive filter panels
* **Success Criteria:**
  - [x] All pages usable on mobile (320px - 480px)
  - [x] All pages usable on tablet (768px - 1024px)
  - [x] No horizontal page overflow
  - [x] All existing tests pass (215 tests)

## Slice 10: Price History Graphs (Complete)
* **Goal:** Display price history graphs for each tracked item.
* **Status:** Complete.
* **Scope:**
    * API endpoint for price history data (`GET /api/items/{id}/price-history`)
    * Line chart visualization with Chart.js
    * Stats panel (min, max, avg, current price)
    * Target price line overlay (dashed green line)
    * Price drop percentage indicator
    * Access from dashboard and tracked items page
    * Responsive modal for mobile/desktop
* **Success Criteria:**
  - [x] API endpoint returns price history with stats
  - [x] Chart shows price trend over time
  - [x] Target price shown as reference line
  - [x] Modal works on mobile and desktop
  - [x] 223 tests passing

## Slice 11: Admin Dashboard & Hard Delete (Planned)
* **Goal:** Powerful admin tools for data management.
* **Scope:**
    * "Hard delete" capability for all entities (cascading deletes)
    * Bulk data cleanup tools
    * Advanced system monitoring

## Slice 12: Soft Delete & Archiving (Planned)
* **Goal:** Allow users to hide items without deleting data.
* **Scope:**
    * Implement `is_archived` status for products and tracked items
    * Filter archived items from the main dashboard
    * Option to "unarchive" items
    * Pause/Resume cron job spies directly from the dashboard

## Slice 13: Bol.com Extraction Fix (Next Priority)
* **Goal:** Resolve issues with Bol.com price extraction.
* **Scope:**
    * Investigate rendering or selector issues on Bol.com
    * Update vision extraction or browser stealth settings if needed

---

## Future Enhancements (Planned)

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
* **Frontend:** Jinja2 templates, Tailwind CSS, Alpine.js, Chart.js
* **Scheduler:** APScheduler (daily extraction)
* **Email:** SMTP (Gmail compatible)
* **Infrastructure:** Docker, Docker Compose

---

## Current Test Count: 223 tests
