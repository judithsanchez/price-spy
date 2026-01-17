# Price Spy

A professional-grade, visual-first price tracking system. Uses computer vision (Gemini 2.5 Flash) and stealth browser automation (Playwright) to monitor prices without being blocked by anti-bot measures.

## Features

- **Visual Price Extraction** - Screenshots product pages and uses AI to extract prices
- **Stealth Browser** - Playwright with anti-detection measures to avoid CAPTCHAs
- **Web Dashboard** - Full CRUD UI for products, stores, and tracked items
- **Rate Limit Management** - Auto-fallback between Gemini models when quota exhausted
- **Extraction Logging** - Track all extraction attempts with success/error status
- **API Usage Tracking** - Monitor Gemini API quota usage per model

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 2. Configuration

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Build and Run

```bash
# Build the container
docker compose -f infrastructure/docker-compose.yml build

# Start the service
docker compose -f infrastructure/docker-compose.yml up -d

# Access the web UI
open http://localhost:8000
```

### 4. Run Tests

```bash
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/ -v
```

## Web Interface

Access the dashboard at `http://localhost:8000`:

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | View tracked items, trigger extractions, see logs |
| Products | `/products` | Manage products (name, category, target price) |
| Stores | `/stores` | Manage stores (name, shipping costs) |
| Tracked Items | `/tracked-items` | Link URLs to products and stores |

### Dashboard Features

- **Tracked Items Table** - View all items with current prices and target status
- **Spy Now Button** - Trigger extraction with real-time success/error feedback
- **API Usage Panel** - See quota usage per Gemini model with progress bars
- **Extraction Logs Panel** - Recent extractions with status, price, and timing

## API Endpoints

### Items & Extraction
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/items` | List tracked items with prices |
| POST | `/api/extract/{id}` | Trigger price extraction |

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
| GET | `/api/logs` | Recent extraction logs |
| GET | `/api/logs/stats` | Today's extraction statistics |
| GET | `/api/usage` | API usage per model |

## CLI Commands

The CLI is still available for scripting:

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
│   ├── core/
│   │   ├── browser.py         # Stealth browser screenshot capture
│   │   ├── vision.py          # Gemini price extraction
│   │   ├── gemini.py          # Model configuration & rate limits
│   │   ├── rate_limiter.py    # API usage tracking & fallback
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
├── tests/                     # Test suites (157 tests)
├── infrastructure/            # Docker configuration
├── docs/                      # Documentation
├── specs/                     # Technical specifications
└── spy.py                     # CLI entry point
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
| `error_log` | General error logging |

## Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLite
- **Browser:** Playwright with Chromium (stealth mode)
- **AI:** Google Gemini 2.5 Flash/Lite (structured output)
- **Frontend:** Jinja2 templates, Tailwind CSS, Alpine.js
- **Infrastructure:** Docker, Docker Compose

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

- [Roadmap](docs/ROADMAP.md) - Project milestones and progress
- [Product Vision](docs/PRODUCT_VISION.md) - High-level goals
- [Data Structure](docs/DATA_STRUCTURE.md) - Database design
- [Usage Guide](docs/USAGE_GUIDE.md) - Detailed usage instructions

## Test Coverage

**157 tests** covering:
- Database operations and repositories
- API endpoints (Products, Stores, Tracked Items, Logs)
- Vision extraction with mocked Gemini API
- Price calculation and comparison logic
- Model configuration and validation
