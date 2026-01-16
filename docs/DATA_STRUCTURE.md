Price Spy Architecture

1. Core Concept: Master vs. Tracked

To solve the problem of "Same product, different names at different stores" AND "Different sizes (250ml vs 500ml)," we use a hierarchy.

Constraint: No barcode scanning. This is a URL-based tracking system.

Product (Master): The abstract substance/item (e.g., "Campina Slagroom"). You buy this concept. It holds your Inventory count.

Tracked Item: The specific URL/SKU (e.g., "AH Campina Room 250ml"). The AI scans this.

2. Database Schema (SQLite)

A. The Products Table (The "Concept")

Holds the general information about items you use and how much you have.

CREATE TABLE products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL, -- e.g., "Campina Slagroom"
category TEXT, -- e.g., "Dairy", "Electronics"

    -- Purchasing Logic
    purchase_type TEXT CHECK(purchase_type IN ('recurring', 'one_time')) DEFAULT 'recurring',
    target_price REAL,               -- Notify if price drops below this (optional global threshold)
    preferred_unit_size TEXT,        -- e.g., "250ml" (for your reference)

    -- Inventory Logic
    current_stock INTEGER DEFAULT 0, -- The live count of items you have at home

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP

);

B. The Stores Table (Shipping Rules)

Defines where you buy from and their specific costs.

CREATE TABLE stores (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL UNIQUE, -- e.g., "Albert Heijn", "Bol.com"
shipping_cost_standard REAL DEFAULT 0, -- e.g., 4.95
free_shipping_threshold REAL, -- e.g., 50.00 (Null if never free)
notes TEXT
);

C. The Tracked Items Table (The "Spy Target")

The actual URLs your headless browser visits.
Update: Now links to store_id and includes items_per_lot for the Atomic Unit logic.

CREATE TABLE tracked_items (
id INTEGER PRIMARY KEY AUTOINCREMENT,
product_id INTEGER NOT NULL, -- Links to the Master Product
store_id INTEGER NOT NULL, -- Links to the Store (Shipping rules)
url TEXT NOT NULL, -- The URL the browser visits
item_name_on_site TEXT, -- e.g., "Campina Verse Slagroom" (Extracted name)

    -- Atomic Unit & Math Logic
    quantity_size REAL NOT NULL,     -- e.g., 330 (Size of ONE Atomic Unit, e.g., 1 can)
    quantity_unit TEXT NOT NULL,     -- e.g., "ml"
    items_per_lot INTEGER DEFAULT 1, -- e.g., 6 (If URL is a 6-pack). Default 1.

    -- Control Flags
    last_checked_at DATETIME,
    is_active BOOLEAN DEFAULT 1,     -- Master switch: 0 = Stop tracking entirely.
    alerts_enabled BOOLEAN DEFAULT 1,-- Notification switch: 0 = Track history silently, 1 = Notify on drop.

    FOREIGN KEY(product_id) REFERENCES products(id),
    FOREIGN KEY(store_id) REFERENCES stores(id)

);

D. Price History Table (The "Cronjob Log")

Every time the cronjob runs and the AI extracts data, it goes here.

CREATE TABLE price_history (
id INTEGER PRIMARY KEY AUTOINCREMENT,
tracked_item_id INTEGER NOT NULL,
price REAL NOT NULL, -- The actual price on the page (e.g., €6.00 for a 6-pack)
volume_price REAL, -- The extracted OR calculated unit price (e.g., €3.03 / L)
volume_unit TEXT, -- e.g., "L", "kg"
is_on_sale BOOLEAN DEFAULT 0, -- 1 if AI detected a "Bonus" or discount tag
captured_at DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id)
);

E. Purchase History Table (The "Habit Tracker")

Where you manually log buys. Triggers inventory updates.

CREATE TABLE purchase_history (
id INTEGER PRIMARY KEY AUTOINCREMENT,
product_id INTEGER NOT NULL,
purchase_date DATE NOT NULL,

    -- Quantity Logic
    item_count INTEGER NOT NULL,     -- e.g., 6 (cans). Adds to stock.
    item_size_label TEXT,            -- e.g., "330ml" (snapshot for reference)
    total_volume_purchased REAL,     -- e.g., 1980 (Calculated: item_count * item_size)

    unit_price_paid REAL,            -- Actual price paid per ATOMIC unit
    shipping_cost REAL DEFAULT 0,
    store_name TEXT,                 -- Keep text here for historical preservation if store is deleted
    notes TEXT,
    FOREIGN KEY(product_id) REFERENCES products(id)

);

F. Process Logs (Debugging)

Stores errors and execution logs.
Update: Added run_id and trigger_source for grouping and tracking execution origin.

CREATE TABLE process_logs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
run_id TEXT, -- UUID to group logs from one "session"
trigger_source TEXT, -- 'CRON' or 'MANUAL'
process_name TEXT NOT NULL, -- e.g., "scraper", "ai_extractor"
status TEXT NOT NULL, -- "INFO", "ERROR", "WARNING"
message TEXT,
raw_data TEXT,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

3. AI Extraction Prompt (The Interface)

System Prompt:

"You are a data extraction assistant for a price tracking system.
Analyze the provided screenshot of a product page.
Extract the pricing and product details into a strict JSON format.

Rules:

price: The current selling price as a number (total price shown on page).

volume_price: The price per unit (e.g., per Liter/Kg) often found in small print. IF NOT FOUND, return null.

product_name: The full name of the product as shown.

on_sale: Boolean true if a discount/bonus tag is visible.

currency: Assume EUR (€) if ambiguous.

Output ONLY raw JSON."

4. System Logic & Workflows

The "Math Fallback" (Critical for Multipacks)

How to determine the true value of a product if the AI misses the "Price per Liter".

Formula: (Page Price / Items Per Lot) / Unit Size

Example (6-Pack Cola):

price (from page): €6.00

items_per_lot (from DB): 6

quantity_size (from DB): 0.33 (L)

Calculation: (6.00 / 6) / 0.33 = 1.00 / 0.33 = €3.03 / L

Inventory Logic (Option A - Atomic Units)

Scenario: You buy a 6-pack of Cola.

User Action: You verify the purchase as "6 items" (since you track Cans, not Packs).

System Action: UPDATE products SET current_stock = current_stock + 6.

Logging Logic (Grouping)

Run ID Generation: At the start of every script execution (CRON or MANUAL), generate a unique ID (e.g., UUID).

Usage: Pass this ID to every log entry created during that run.

Benefit: You can query SELECT \* FROM process_logs WHERE run_id = '...' to see the full story of one specific check.

Notification Logic

Check: Cronjob runs -> Inserts new price.

Verify: Is tracked_items.alerts_enabled = 1?

Compare: Is current_price < last_price?

Send: MQTT payload to Home Assistant.
