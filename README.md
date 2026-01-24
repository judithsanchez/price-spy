# Price Spy

A personal price tracking assistant that monitors online product prices and alerts you when they drop to your target. Uses AI-powered screenshot analysis to work on any website without getting blocked.

## What Does It Do?

1. **You add products** you want to track with a target price (the price you'd buy at)
2. **Every day at 8:00 AM**, Price Spy visits each product page and takes a screenshot
3. **AI reads the screenshot** and extracts the current price
4. **If the price hits your target**, you see a DEAL alert on the dashboard
5. **All prices are stored** so you can see trends over time

**Why screenshots?** Traditional scrapers get blocked by anti-bot measures. By using a real browser and AI vision, Price Spy works on virtually any website.

## Features

- **Visual Price Extraction** - Screenshots product pages and uses AI to extract prices
- **Stealth Browser** - Playwright with anti-detection measures to avoid CAPTCHAs
- **Web Dashboard** - Full CRUD UI for products, stores, and tracked items
- **Price Drop Alerts** - DEAL badge and alert banner when price ≤ target
- **Scheduled Extraction** - Daily automated price checking with configurable time
- **Daily Email Reports** - Get notified of deals found and extraction results
- **Smart Queue Management** - Limits concurrent extractions to respect API rate limits
- **Batch Extraction** - Extract all items at once via CLI or API
- **Unit Price Display** - Shows price per L/kg for easy comparison
- **Rate Limit Management** - Auto-fallback between Gemini models when quota exhausted
- **Extraction Logging** - Track all extraction attempts with success/error status
- **API Usage Tracking** - Monitor Gemini API quota usage per model

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Gemini API key from [Google AI Studio](https://aistudio.google.com/) (free tier works fine)

### 2. Configuration

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Build and Run

```bash
# Build the container (first time takes a few minutes)
docker compose -f infrastructure/docker-compose.yml build

# Start the service
docker compose -f infrastructure/docker-compose.yml up -d

# Open the dashboard
open http://localhost:8000
```

 Refresh the dashboard - you'll see sample products with prices, including a DEAL alert.

### 5. Database Safety

Price Spy has a built-in **Safety Guard** in the `Database` class. It specifically identifies if you are running in a test environment and explicitly blocks any connection to `data/pricespy.db`. This prevents accidental modification of your production data during automated tests.

To manage your production data state, use the SQL dump utility:
```bash
# Save current state to Git-friendly text file
python3 scripts/db_manager.py dump

# Restore database from the SQL dump
python3 scripts/db_manager.py restore
```

### 6. Run Tests

```bash
# Tests automatically use a disposable temporary database for isolation
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v
```

## Web Interface

Access the dashboard at `http://localhost:8000`:

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | View tracked items, trigger extractions, see deals |
| Products | `/products` | Manage products (name, category, target price) |
| Stores | `/stores` | Manage stores (name, shipping costs) |
| Tracked Items | `/tracked-items` | Link URLs to products and stores |
| Logs | `/logs` | View extraction logs and error logs with filters |

### Dashboard Features

- **Deal Alerts** - Green DEAL badge and alert banner when price ≤ target
- **Tracked Items Table** - View items with prices, unit prices, and target status
- **Spy Now Button** - Trigger extraction with real-time success/error feedback
- **Scheduled Spy Panel** - View next scheduled run, trigger manual runs, pause/resume
- **API Usage Panel** - See quota usage per Gemini model with progress bars
- **Extraction Logs Panel** - Recent extractions with status, price, and timing

## API Endpoints

### Items & Extraction
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/items` | List tracked items with prices |
| POST | `/api/extract/{id}` | Trigger price extraction for one item |
| POST | `/api/extract/all` | Trigger batch extraction for all items |

### Products
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/products` | List all products |
| POST | `/api/products` | Create product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |

### Stores
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stores` | List all stores |
| POST | `/api/stores` | Create store |
| PUT | `/api/stores/{id}` | Update store |
| DELETE | `/api/stores/{id}` | Delete store |

### Tracked Items
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tracked-items` | List all tracked items |
| POST | `/api/tracked-items` | Create tracked item |
| PUT | `/api/tracked-items/{id}` | Update tracked item |
| DELETE | `/api/tracked-items/{id}` | Delete tracked item |

### Monitoring
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/logs` | Extraction logs with filters (status, item_id, dates) |
| GET | `/api/logs/stats` | Today's extraction statistics |
| GET | `/api/errors` | Error logs with filters |
| GET | `/api/usage` | API usage per model |

### Scheduler
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/scheduler/status` | Scheduler status, next run, last run |
| POST | `/api/scheduler/run-now` | Trigger immediate extraction run |
| POST | `/api/scheduler/pause` | Pause scheduled extractions |
| POST | `/api/scheduler/resume` | Resume scheduled extractions |

### Email
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/email/status` | Email configuration status |
| POST | `/api/email/test` | Send test email to verify config |

The seed data logic is primarily for initial testing. For production state management, use the **SQL Dump** feature described below.

### Resetting Data

To start fresh:
```bash
# Remove the database (back it up first if needed!)
rm data/pricespy.db

# Restart the service (recreates empty database with core categories/labels)
docker compose -f infrastructure/docker-compose.yml restart
```

## CLI Commands

### Management CLI

```bash
# Seed test data for UI testing
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python -m app.cli seed-test-data

```bash
# Extract prices for all active tracked items
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python -m app.cli extract-all

# Extract with custom delay between items
docker compose -f infrastructure/docker-compose.yml run --rm price-spy python -m app.cli extract-all --delay 10
```

### Database Management (Production)

Manage your production data using SQL dumps. These are text-based, allowing you to see diffs in Git and avoid binary repository bloat.

```bash
# Create a SQL dump of your current database
python3 scripts/db_manager.py dump

# Restore Price Spy from a SQL dump (automatically creates a backup of current DB)
python3 scripts/db_manager.py restore
```

**Files:**
- `data/pricespy.db`: Your binary production database (ignored by Git)
- `data/pricespy_dump.sql`: Your version-controlled data state (tracked by Git)

### Legacy CLI (spy.py)

```bash
# Extract price from URL
python spy.py extract "https://www.amazon.nl/dp/B08N5WRWNW"

# Add a product to track
python spy.py add-product "Campina Slagroom" --category "Dairy" --target-price 2.50

# Add a store with shipping info
python spy.py add-store "Amazon.nl" --shipping 4.95 --free-threshold 50

# Track a URL (link to product and store)
python spy.py track "https://amazon.nl/..." --product-id 1 --store-id 1 --size 250 --unit ml

# List items
python spy.py list products
python spy.py list stores
python spy.py list tracked
```

## Project Structure

```
price-spy/
├── app/
│   ├── api/
│   │   └── main.py            # FastAPI application
│   ├── cli.py                 # CLI commands (seed-test-data, extract-all)
│   ├── core/
│   │   ├── browser.py         # Stealth browser screenshot capture
│   │   ├── vision.py          # Gemini price extraction
│   │   ├── gemini.py          # Model configuration & rate limits
│   │   ├── rate_limiter.py    # API usage tracking & fallback
│   │   ├── batch_extraction.py # Batch extraction for all items
│   │   ├── extraction_queue.py # Concurrent extraction with semaphore
│   │   ├── scheduler.py       # APScheduler daily extraction
│   │   ├── email_report.py    # Daily email report after extraction
│   │   ├── seeder.py          # Test data generation
│   │   └── price_calculator.py
│   ├── models/
│   │   └── schemas.py         # Pydantic data models
│   ├── storage/
│   │   ├── database.py        # SQLite schema
│   │   └── repositories.py    # Data access layer
│   ├── templates/             # Jinja2 HTML templates
│   └── utils/
│       └── logging.py         # Structured JSON logging
├── data/                      # SQLite database storage
├── screenshots/               # Captured screenshots
├── tests/                     # Test suites (199 tests)
├── infrastructure/            # Docker configuration
├── docs/                      # Documentation
├── specs/                     # Technical specifications
└── spy.py                     # Legacy CLI entry point
```

## Database Schema

SQLite database (`data/pricespy.db`):

| Table | Description |
|-------|-------------|
| `products` | Master product concepts (name, category, target_price) |
| `stores` | Store definitions with shipping rules |
| `tracked_items` | URLs linked to products and stores |
| `price_history` | Successful extractions with price and timestamp |
| `extraction_logs` | All extraction attempts (success/error) |
| `api_usage` | Daily API quota tracking per model |
| `scheduler_runs` | Scheduled extraction run history |
| `error_log` | General error logging |

## Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLite
- **Browser:** Playwright with Chromium (stealth mode)
- **AI:** Google Gemini 2.5 Flash/Lite (structured output)
- **Frontend:** Jinja2 templates, Tailwind CSS, Alpine.js
- **Infrastructure:** Docker, Docker Compose

## Scheduler (Automatic Daily Extraction)

Price Spy includes a built-in scheduler that automatically checks all your tracked items once per day.

### How It Works

```
08:00 AM (default) - Scheduler wakes up
                   - Queries database for items due for check
                   - Skips items already checked today (manual "Spy Now")
                   - Processes items in batches (max 10 concurrent)
                   - Saves prices to history
                   - Logs results to scheduler_runs table
                   - Sends daily email report (if configured)
                   - Sleeps until tomorrow
```

### Configuration

Set these environment variables in your `.env` file or Docker Compose:

| Variable | Default | Description |
|----------|---------|-------------|
| `SCHEDULER_ENABLED` | `true` | Enable/disable automatic scheduling |
| `SCHEDULER_HOUR` | `8` | Hour to run (0-23, in container's timezone) |
| `SCHEDULER_MINUTE` | `0` | Minute to run (0-59) |
| `MAX_CONCURRENT_EXTRACTIONS` | `10` | Max parallel API requests |

Example `.env` to run at 6:30 PM:
```bash
SCHEDULER_HOUR=18
SCHEDULER_MINUTE=30
```

### Smart Skip Feature

If you manually click "Spy Now" on an item, the scheduler won't check it again the same day:

| Action | Result |
|--------|--------|
| Manual check at 10:00 AM, scheduler at 8:00 PM | Item skipped (already checked today) |
| Manual check at 10:00 AM, scheduler at 8:00 AM next day | Item included (checked yesterday) |
| Item never checked | Always included |

This prevents wasting API quota on duplicate extractions.

### Queue Management

The scheduler uses an async semaphore to limit concurrent extractions:
- **Max 10 requests at once** (configurable)
- **Respects Gemini's 15 RPM limit** with safety margin
- **Continues on failure** - one failed item doesn't stop the others
- **Logs everything** - success/failure recorded per item

### Monitoring the Scheduler

**Dashboard panel** shows:
- Next scheduled run time
- Last run status (completed/failed, items processed)
- Number of items to check

**API endpoints:**
```bash
# Get status
curl http://localhost:8000/api/scheduler/status

# Trigger immediate run
curl -X POST http://localhost:8000/api/scheduler/run-now

# Pause scheduler
curl -X POST http://localhost:8000/api/scheduler/pause

# Resume scheduler
curl -X POST http://localhost:8000/api/scheduler/resume
```

**Database table** `scheduler_runs` stores run history:
```sql
SELECT * FROM scheduler_runs ORDER BY started_at DESC LIMIT 5;
```

## Daily Email Reports

Get a summary email after each scheduled extraction with deals found, prices checked, and any errors.

### Setup

Add these to your `.env` file:

```bash
# Required for email reports
EMAIL_ENABLED=true
EMAIL_RECIPIENT=you@email.com
EMAIL_SENDER=your_sender@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_sender@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_DASHBOARD_URL=http://your-pi-ip:8000
```

**Gmail Users:** Create an App Password at https://myaccount.google.com/apppasswords (requires 2FA enabled).

### Email Content

Each daily report includes:
- **Deals Found** - Items that hit your target price (highlighted green)
- **All Items Checked** - Price for each tracked item with status
- **Errors** - Any extraction failures
- **Summary** - Total counts and next scheduled run

### API Endpoints

```bash
# Check email configuration status
curl http://localhost:8000/api/email/status

# Send a test email
curl -X POST http://localhost:8000/api/email/test
```

### Disable Email Reports

Set `EMAIL_ENABLED=false` or leave email variables unconfigured.

## Rate Limiting

The system automatically manages Gemini API quotas:

- **Primary Model:** `gemini-2.5-flash` (250 requests/day)
- **Fallback Model:** `gemini-2.5-flash-lite` (1000 requests/day)

On 429 errors, the system automatically:
1. Marks the model as exhausted
2. Falls back to the next available model
3. Logs the failure for visibility

Quotas reset at midnight Pacific time.

## Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run tests
pytest tests/ -v -s
```

## Documentation

### Getting Started
- [User Guide](docs/USER_GUIDE.md) - How to use Price Spy (adding products, understanding the UI)
- [Raspberry Pi Setup](docs/RASPBERRY_PI_SETUP.md) - Step-by-step guide to run on a Pi

### Technical
- [Data Structure](docs/DATA_STRUCTURE.md) - Database schema and design
- [Roadmap](docs/ROADMAP.md) - Project milestones and progress
- [Product Vision](docs/PRODUCT_VISION.md) - High-level goals

## Test Coverage

**212 tests** covering:
- Database operations and repositories
- API endpoints (Products, Stores, Tracked Items, Logs, Batch Extraction)
- Scheduler and extraction queue
- Vision extraction with mocked Gemini API
- Price calculation and comparison logic
- Model configuration and validation
- Price drop alerts UI (DEAL badge)
- Test data seeding
- Batch extraction functionality
- Daily email reports
