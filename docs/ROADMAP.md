## Slice 1: The Manual Spy (Complete)
* **Goal:** Proof of Concept for Visual Scraping.
* **Status:** Complete.
* **Scope:** Manual CLI trigger, Chromium/Playwright stealth browser, Gemini 2.5 Flash Vision analysis, Pydantic validation, SQLite persistence (price_history, error_log), structured JSON logging.
* **Success Criteria:**
  - [x] Verified JSON response from Amazon.nl (100% confidence)
  - [x] No CAPTCHA in 5 consecutive runs
  - [x] 31 unit/integration tests passing in Docker

## Slice 2: Full Data Model (The Memory)
* **Goal:** Implement complete database schema for product tracking and price comparison.
* **Status:** In Development.
* **Scope:**
    * Implement full schema: `products`, `stores`, `tracked_items` tables (per DATA_STRUCTURE.md)
    * Link tracked URLs to master products and stores
    * Price comparison logic: "Last Price" vs "Current Price"
    * Volume/unit price calculation for multipacks
    * Process logging with run_id grouping
* **Success Criteria:**
  - Track multiple URLs for the same product across different stores
  - Calculate and display price per unit (e.g., EUR/L)

## Slice 3: Communication (The Alert)
* **Goal:** Notify the user when a price drops.
* **Scope:**
    * Integrate Python `smtplib` for **Email** notifications.
    * Daily Summary: One email at the end of the day with all monitored prices.
    * Price Drop Alert: Immediate email if a price is lower than the previous record.
* **Success Criteria:** Receiving a formatted email on a test price drop.

## Slice 4: Automation & Integration
* **Goal:** Connect to the Smart Home ecosystem.
* **Scope:**
    * Schedule the spy to run **once a day** using a Cron job or Docker Compose scheduler.
    * Integrate with **Home Assistant** via Webhooks or MQTT to trigger phone notifications.
* **Success Criteria:** An automated daily run that triggers a phone notification.

## Slice 5: Management (The Dashboard)
* **Goal:** A simple Web UI to manage the Spy.
* **Scope:** * A lightweight Flask or FastAPI web server.
    * UI to add/remove URLs and view price history graphs.
* **Success Criteria:** Accessing `http://raspberrypi:5000` and adding a new tracking URL via the browser.
