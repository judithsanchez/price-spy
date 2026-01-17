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

## Slice 6: Scheduled Extraction & Price Drop Alerts (In Progress)
* **Goal:** Automated daily price checks with visual alerts.
* **Status:** In Progress (Phases 1-3 complete, Phase 4 pending).
* **Scope:**
    * Scheduled extraction job (APScheduler) - TODO
    * Batch extraction for all active items - DONE
    * Price drop alerts on dashboard (DEAL badge + alert banner) - DONE
    * CLI commands for batch extraction and test data seeding - DONE
* **Success Criteria:**
  - [ ] Scheduler runs daily extraction automatically
  - [x] Dashboard shows "DEAL" badge when price ≤ target
  - [x] CLI commands: `extract-all`, `seed-test-data`
  - [x] API endpoint: `POST /api/extract/all`
  - [x] 179 tests passing

## Slice 7: Price History & Notifications (Planned)
* **Goal:** View price history and get notified on price drops.
* **Status:** Planned.
* **Scope:**
    * Price history view per tracked item (chart/table)
    * Email notifications on price drops
    * Home Assistant integration (webhooks/MQTT)
* **Success Criteria:**
  - [ ] View price history graph for any tracked item
  - [ ] Receive notification when price drops below target

---

## Tech Stack

* **Backend:** Python 3.11, FastAPI, SQLite
* **Browser:** Playwright with Chromium (stealth mode)
* **AI:** Google Gemini 2.5 Flash/Lite (structured output)
* **Frontend:** Jinja2 templates, Tailwind CSS, Alpine.js
* **Infrastructure:** Docker, Docker Compose

---

## Current Test Count: 179 tests
