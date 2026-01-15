## Slice 1: The Manual Spy (Current)
* **Goal:** Proof of Concept for Visual Scraping.
* **Status:** In Development.
* **Scope:** Manual CLI trigger, Chromium/Playwright context, Gemini Vision analysis, JSON output to console.
* **Success Criteria:** Verified JSON response from Amazon.nl and Google Shopping.

## Slice 2: Persistence (The Memory)
* **Goal:** Stop "forgetting" prices between runs.
* **Scope:** * Implement **SQLite** database to store `product_name`, `price`, `timestamp`, and `url`.
    * Logic to compare "Last Price" vs "Current Price."
    * TDD check: Verify database creates entries and retrieves history correctly on ARM64.
* **Success Criteria:** Running the tool twice for the same URL results in two database entries.

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
