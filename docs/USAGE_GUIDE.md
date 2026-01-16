# Price Spy - Complete Usage Guide

This guide covers everything you need to use Price Spy effectively.

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Docker Commands](#2-docker-commands)
3. [Database Setup](#3-database-setup)
4. [Complete Workflow](#4-complete-workflow)
5. [CLI Reference](#5-cli-reference)
6. [Inspecting the Database](#6-inspecting-the-database)
7. [Reading Logs](#7-reading-logs)
8. [Best Practices](#8-best-practices)

---

## 1. Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd price-spy

# 2. Create .env file with your API key
echo "GEMINI_API_KEY=your_api_key_here" > .env

# 3. Build the Docker image
docker compose -f infrastructure/docker-compose.yml build

# 4. Run tests to verify everything works
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v
```

---

## 2. Docker Commands

### Build the Image

```bash
docker compose -f infrastructure/docker-compose.yml build
```

### Run Tests

```bash
# All tests
docker compose -f infrastructure/docker-compose.yml run --rm price-spy

# Specific test file
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/test_models.py -v
```

### Run CLI Commands

```bash
# Basic pattern
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python spy.py <command>

# Create a shell alias for convenience (add to ~/.bashrc or ~/.zshrc)
alias spy='docker compose -f infrastructure/docker-compose.yml run --rm price-spy python spy.py'
```

### Interactive Shell

```bash
docker compose -f infrastructure/docker-compose.yml run --rm price-spy bash
```

### Data Persistence

The database is stored in `data/pricespy.db` and is mounted as a volume, so data persists between container runs.

---

## 3. Database Setup

### Automatic Initialization

The database is automatically created and initialized when you run any CLI command. No manual setup required.

### Database Location

- **Inside container:** `/app/data/pricespy.db`
- **On host:** `./data/pricespy.db`

### Tables

| Table | Purpose |
|-------|---------|
| `products` | Master product concepts (what you buy) |
| `stores` | Store definitions with shipping costs |
| `tracked_items` | URLs linked to products and stores |
| `price_history` | Price extraction history |
| `error_log` | Failed extraction logs |

### Reset Database

```bash
# Delete and start fresh
rm data/pricespy.db
```

---

## 4. Complete Workflow

### Step 1: Add Products

First, add the products you want to track:

```bash
# Basic product
spy add-product "Campina Slagroom"

# With category and target price
spy add-product "Campina Slagroom" --category "Dairy" --target-price 2.50

# With preferred unit size
spy add-product "Coca-Cola" --category "Beverages" --target-price 0.80 --unit-size "330ml"
```

**Product fields:**
- `name` (required): Product name
- `--category, -c`: Product category (e.g., "Dairy", "Beverages")
- `--target-price, -t`: Target price for alerts
- `--unit-size, -u`: Preferred unit size (e.g., "250ml", "1L")

### Step 2: Add Stores

Add the stores where you'll track prices:

```bash
# Basic store
spy add-store "Amazon.nl"

# With shipping info
spy add-store "Amazon.nl" --shipping 4.95 --free-threshold 50

# Another store
spy add-store "Bol.com" --shipping 0 --free-threshold 20
```

**Store fields:**
- `name` (required): Store name (must be unique)
- `--shipping, -s`: Standard shipping cost (default: 0)
- `--free-threshold, -f`: Order amount for free shipping

### Step 3: Track URLs

Link a URL to a product and store:

```bash
# Track a single item
spy track "https://www.amazon.nl/dp/B015OAQEHI" \
    --product-id 1 \
    --store-id 1 \
    --size 950 \
    --unit ml

# Track a multipack (6-pack of 330ml cans)
spy track "https://www.amazon.nl/dp/B08XYZ123" \
    --product-id 2 \
    --store-id 1 \
    --size 330 \
    --unit ml \
    --lot 6
```

**Tracked item fields:**
- `url` (required): Product page URL
- `--product-id, -p` (required): Product ID from step 1
- `--store-id, -s` (required): Store ID from step 2
- `--size` (required): Quantity size of one unit (e.g., 950 for 950ml)
- `--unit, -u` (required): Unit of measurement (ml, L, g, kg, piece)
- `--lot, -l`: Items per lot for multipacks (default: 1)

### Step 4: Extract Prices

Run price extraction on any URL:

```bash
# Extract price (works for tracked and non-tracked URLs)
spy extract "https://www.amazon.nl/dp/B015OAQEHI"
```

**Output includes:**
- Product name (from Gemini)
- Current price
- Store name
- Confidence score
- Unit price (if URL is tracked)
- Price comparison with last extraction

### Step 5: View Your Data

```bash
# List all products
spy list products

# List all stores
spy list stores

# List all tracked URLs
spy list tracked
# or just
spy list
```

---

## 5. CLI Reference

### Commands Overview

| Command | Description |
|---------|-------------|
| `extract <url>` | Extract price from a URL |
| `add-product <name>` | Add a new product |
| `add-store <name>` | Add a new store |
| `track <url>` | Track a URL |
| `list [what]` | List products, stores, or tracked items |

### Extract Command

```bash
spy extract "https://www.amazon.nl/dp/B015OAQEHI"
```

**What happens:**
1. Playwright captures a stealth screenshot
2. Gemini Vision API extracts product info
3. Data is saved to `price_history` table
4. If URL is tracked, shows unit price
5. If previous extraction exists, shows price comparison

**Example output:**
```
Product: INSTITUTO ESPAÑOL Urea lotion dispenser 950 ml
Price: EUR 13.44
Store: Amazon
Confidence: 100%
Unit price: EUR 14.15/L
Price change: ↓ 0.50 (-3.6%)
*** PRICE DROP DETECTED ***
```

### Add Product Command

```bash
spy add-product "Name" [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--category` | `-c` | Product category |
| `--target-price` | `-t` | Target price for alerts |
| `--unit-size` | `-u` | Preferred unit size |

### Add Store Command

```bash
spy add-store "Name" [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--shipping` | `-s` | Standard shipping cost |
| `--free-threshold` | `-f` | Free shipping threshold |

### Track Command

```bash
spy track "URL" --product-id N --store-id N --size N --unit UNIT [--lot N]
```

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--product-id` | `-p` | Yes | Product ID |
| `--store-id` | `-s` | Yes | Store ID |
| `--size` | | Yes | Quantity size |
| `--unit` | `-u` | Yes | Unit (ml, L, g, kg, piece) |
| `--lot` | `-l` | No | Items per lot (default: 1) |

### List Command

```bash
spy list [products|stores|tracked]
```

Default: `tracked`

---

## 6. Inspecting the Database

### Using SQLite CLI (Inside Container)

```bash
# Start interactive shell
docker compose -f infrastructure/docker-compose.yml run --rm price-spy bash

# Open SQLite
sqlite3 data/pricespy.db

# Useful SQLite commands:
.tables              # List all tables
.schema products     # Show table schema
.headers on          # Show column headers
.mode column         # Pretty print

# Example queries:
SELECT * FROM products;
SELECT * FROM stores;
SELECT * FROM tracked_items;
SELECT * FROM price_history ORDER BY created_at DESC LIMIT 10;
SELECT * FROM error_log ORDER BY created_at DESC LIMIT 10;
```

### Using SQLite on Host

```bash
sqlite3 data/pricespy.db "SELECT * FROM products;"
```

### Useful Queries

```sql
-- All price history for a product
SELECT ph.*, ti.quantity_size, ti.quantity_unit
FROM price_history ph
JOIN tracked_items ti ON ph.url = ti.url
WHERE ti.product_id = 1
ORDER BY ph.created_at DESC;

-- Latest price for each tracked URL
SELECT url, product_name, price, currency, created_at
FROM price_history
GROUP BY url
HAVING created_at = MAX(created_at);

-- Price drops (comparing consecutive extractions)
WITH ranked AS (
  SELECT *,
    LAG(price) OVER (PARTITION BY url ORDER BY created_at) as prev_price
  FROM price_history
)
SELECT url, product_name, prev_price, price,
  ROUND((prev_price - price) / prev_price * 100, 1) as drop_percent
FROM ranked
WHERE price < prev_price;

-- Recent errors
SELECT error_type, message, url, created_at
FROM error_log
ORDER BY created_at DESC
LIMIT 10;
```

---

## 7. Reading Logs

### Log Format

All logs are output as JSON to stderr:

```json
{
  "timestamp": "2026-01-16T10:04:25.105341+00:00",
  "level": "INFO",
  "logger": "__main__",
  "message": "Starting price extraction",
  "url": "https://www.amazon.nl/..."
}
```

### Viewing Logs

```bash
# Run command and see logs
spy extract "https://..." 2>&1 | jq '.'

# Filter by level
spy extract "https://..." 2>&1 | grep '"level": "ERROR"'

# Save logs to file
spy extract "https://..." 2>logs.jsonl
```

### Log Levels

| Level | Meaning |
|-------|---------|
| INFO | Normal operations (starting, completed) |
| WARNING | Non-fatal issues (low confidence, retries) |
| ERROR | Failed operations (saved to error_log table) |

### Error Log Table

Errors are also persisted in the `error_log` table:

```sql
SELECT error_type, message, url, created_at
FROM error_log
ORDER BY created_at DESC;
```

---

## 8. Best Practices

### Organizing Products

```bash
# Group by category
spy add-product "Campina Slagroom" -c "Dairy"
spy add-product "Milk" -c "Dairy"
spy add-product "Coca-Cola" -c "Beverages"
spy add-product "Heineken" -c "Beverages"
```

### Setting Target Prices

Set target prices based on your desired per-unit price:

```bash
# For a 250ml cream, target €1.00/250ml = €4.00/L
spy add-product "Campina Slagroom" -c "Dairy" -t 1.00 -u "250ml"
```

### Tracking Multipacks

Always specify the lot size for multipacks:

```bash
# 6-pack of 330ml cans
spy track "https://..." -p 1 -s 1 --size 330 --unit ml --lot 6

# 12-pack of 500ml bottles
spy track "https://..." -p 1 -s 1 --size 500 --unit ml --lot 12
```

### Unit Conversions

The system automatically converts to standard units:

| Input | Converts To |
|-------|-------------|
| ml | L (liters) |
| cl | L (liters) |
| g | kg (kilograms) |
| L | L (stays) |
| kg | kg (stays) |
| piece/stuks | piece (stays) |

### Scheduled Extraction

For automated price checking, use cron on the host:

```bash
# Edit crontab
crontab -e

# Add daily check at 8 AM
0 8 * * * cd /path/to/price-spy && docker compose -f infrastructure/docker-compose.yml run --rm price-spy python spy.py extract "https://..." >> /var/log/pricespy.log 2>&1
```

### Backup Database

```bash
# Backup
cp data/pricespy.db data/pricespy.db.backup

# Restore
cp data/pricespy.db.backup data/pricespy.db
```

---

## Example: Full Setup for Body Lotion

```bash
# 1. Add the product
spy add-product "Instituto Español Urea Lotion" \
    --category "Beauty" \
    --target-price 12.00

# 2. Add stores
spy add-store "Amazon.nl" --shipping 4.95 --free-threshold 50
spy add-store "Bol.com" --shipping 0 --free-threshold 20

# 3. Track URLs from different stores
spy track "https://www.amazon.nl/dp/B015OAQEHI" \
    -p 1 -s 1 --size 950 --unit ml

spy track "https://www.bol.com/nl/p/instituto-espanol-urea-body-lotion" \
    -p 1 -s 2 --size 950 --unit ml

# 4. Check current state
spy list products
spy list stores
spy list tracked

# 5. Run price extraction
spy extract "https://www.amazon.nl/dp/B015OAQEHI"
spy extract "https://www.bol.com/nl/p/instituto-espanol-urea-body-lotion"

# 6. Check price history
sqlite3 data/pricespy.db "SELECT product_name, price, currency, created_at FROM price_history ORDER BY created_at DESC;"
```
