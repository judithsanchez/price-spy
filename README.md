A professional-grade, visual-first price tracking system running on **Raspberry Pi 5**. This project uses computer vision (Gemini 2.5 Flash) and stealth browser automation (Playwright) to monitor prices without being blocked by anti-bot measures.

## Project Structure

```
price-spy/
├── app/                    # Python source code
│   ├── core/
│   │   ├── browser.py      # Stealth browser screenshot capture
│   │   ├── vision.py       # Gemini price extraction
│   │   └── price_calculator.py  # Volume price & comparison logic
│   ├── models/
│   │   └── schemas.py      # Pydantic data models
│   ├── storage/
│   │   ├── database.py     # SQLite connection management
│   │   └── repositories.py # Data access layer
│   └── utils/
│       └── logging.py      # Structured JSON logging
├── data/                   # SQLite database storage
├── tests/                  # Test suites (70 tests)
├── infrastructure/         # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                   # Documentation
├── specs/                  # Technical specifications
├── spy.py                  # CLI entry point
└── .env                    # Environment variables (not committed)
```

## Tech Stack

- **Host:** Raspberry Pi 5 (ARM64)
- **Container:** Docker with Python 3.11-slim-bookworm
- **Automation:** Playwright (Chromium)
- **AI:** Google Gemini 2.5 Flash (Vision API)
- **Database:** SQLite (price history and error logging)
- **Validation:** Pydantic v2

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 2. Configuration

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. Build the Container

```bash
docker compose -f infrastructure/docker-compose.yml build
```

### 4. Run Tests

```bash
docker compose -f infrastructure/docker-compose.yml run --rm price-spy
```

### 5. Run Individual Tests

```bash
# Test API key works
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/test_api_key.py -v -s

# Test browser screenshot capture
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/test_browser.py -v -s

# Test Gemini price extraction
docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest tests/test_vision.py -v -s
```

### 6. CLI Commands

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

# Example extract output (with price comparison):
# Product: INSTITUTO ESPAÑOL Urea lotion dispenser 950 ml
# Price: EUR 13.4
# Store: Amazon.nl
# Confidence: 100%
# Unit price: EUR 14.11/L
# Price change: ↓ 0.50 (-3.6%)
# *** PRICE DROP DETECTED ***
```

### 7. Interactive Shell

```bash
docker compose -f infrastructure/docker-compose.yml run --rm price-spy bash
```

## Development (Without Docker)

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

## Quality Assurance

This project follows **Test-Driven Development (TDD)**:

1. **RED** - Write a failing test first
2. **GREEN** - Implement code to make the test pass
3. **REFACTOR** - Clean up while keeping tests green

All features must be planned and documented in `specs/` before implementation.

## Data Persistence

All data is stored in SQLite (`data/pricespy.db`):

- **products** - Master product concepts (what you buy)
- **stores** - Store definitions with shipping rules
- **tracked_items** - URLs linked to products and stores
- **price_history** - Successful extractions with price, confidence, timestamp
- **error_log** - Failed extractions with error type, message, and stack trace

Logs are output as structured JSON to stderr for easy parsing.
