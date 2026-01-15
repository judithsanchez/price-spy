# Slice 1: The Manual Spy - Implementation Plan

## Overview

**Objective:** Build a CLI proof-of-concept that takes a URL, captures a screenshot using a stealth-configured browser, sends it to Gemini 2.5 Flash Vision API, and outputs structured price data as JSON.

**Success Criteria:**
- Navigates to Amazon.nl or Google Shopping without triggering CAPTCHA
- Captures a readable screenshot
- Returns valid JSON matching the defined schema
- All tests pass within the Docker/ARM64 environment

---

## 1. Project Structure

```
price-spy/
├── app/
│   ├── __init__.py
│   ├── cli.py              # Entry point, argument parsing
│   ├── core/
│   │   ├── __init__.py
│   │   ├── browser.py      # Playwright stealth browser logic
│   │   ├── vision.py       # Gemini API integration
│   │   └── models.py       # Pydantic data models
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py       # Structured logging configuration
│   └── config.py           # Environment/settings management
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── test_browser.py     # Browser module tests
│   ├── test_vision.py      # Vision API tests
│   └── test_cli.py         # End-to-end CLI tests
├── screenshots/            # Error screenshots saved here
├── infrastructure/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── pyproject.toml          # Project metadata + pytest config
└── spy.py                  # Main entry script (thin wrapper)
```

---

## 2. Module Specifications

### 2.1 `app/config.py` - Configuration Management

**Purpose:** Centralize all configuration using environment variables.

**Responsibilities:**
- Load `GEMINI_API_KEY` from environment (required)
- Define constants: viewport size (1920x1080), timeouts, locale settings
- Provide a `Settings` class/dataclass for type-safe access

**Environment Variables:**
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `SCREENSHOT_DIR` | No | `./screenshots` | Directory for error screenshots |
| `NAVIGATION_TIMEOUT` | No | `60000` | Page load timeout in ms |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

### 2.2 `app/utils/logger.py` - Structured Logging

**Purpose:** Provide consistent, structured logging across all modules.

**Responsibilities:**
- Configure Python's `logging` module with structured format
- Support JSON log format for production (easy parsing)
- Include contextual information: timestamp, module, level, message
- Log to stderr (stdout reserved for JSON output)

**Log Levels by Scenario:**
| Scenario | Level | Example Message |
|----------|-------|-----------------|
| Starting extraction | INFO | `Starting extraction for URL: ...` |
| Screenshot captured | DEBUG | `Screenshot saved: 1920x1080, 245KB` |
| API request sent | DEBUG | `Sending image to Gemini API` |
| Low confidence result | WARNING | `Low confidence score (0.35), result may be inaccurate` |
| Network timeout | ERROR | `Navigation timeout after 60s: URL` |
| CAPTCHA detected | ERROR | `CAPTCHA detected, screenshot saved for debugging` |
| API failure | ERROR | `Gemini API error: 429 Rate Limited` |

---

### 2.3 `app/core/models.py` - Data Models

**Purpose:** Define the data contract using Pydantic for validation and serialization.

**Models:**

```
ExtractionResult:
  - product_name: str
  - price: float
  - currency: str (3-letter ISO code)
  - store_name: str
  - page_type: Literal["single_product", "search_list"]
  - confidence_score: float (0.0 to 1.0)

ExtractionError:
  - error_type: str (e.g., "captcha_detected", "timeout", "api_error")
  - message: str
  - url: str
  - screenshot_path: Optional[str]
```

**Validation Rules:**
- `price` must be > 0
- `confidence_score` must be between 0.0 and 1.0
- `currency` must be exactly 3 uppercase letters

---

### 2.4 `app/core/browser.py` - Stealth Browser Module

**Purpose:** Navigate to URLs and capture screenshots while evading anti-bot detection.

**Responsibilities:**
- Initialize Playwright with Chromium (headless)
- Apply stealth configuration (as per SPECS_EXTRACTION_ENGINE.md)
- Navigate to URL with configurable timeout
- Wait for `networkidle` state
- Capture "above the fold" screenshot (1920x1200px)
- Detect CAPTCHA indicators (heuristic: page title contains "captcha", "robot", "verify")

**Stealth Configuration Checklist:**
- [ ] User-Agent: Windows Chrome 120
- [ ] Viewport: 1920x1080
- [ ] Locale: `nl-NL`
- [ ] Timezone: `Europe/Amsterdam`
- [ ] Geolocation permission: granted
- [ ] `navigator.webdriver`: masked to `false`
- [ ] Block tracking scripts (optional optimization)

**Function Signatures:**

```
async def create_stealth_context(playwright) -> BrowserContext
    """Create a browser context with stealth settings."""

async def capture_screenshot(url: str, context: BrowserContext) -> bytes
    """Navigate to URL and return screenshot as PNG bytes."""
    Raises: CaptchaDetectedError, NavigationTimeoutError

async def detect_captcha(page: Page) -> bool
    """Check if current page shows a CAPTCHA challenge."""
```

**Error Handling:**
- On timeout: raise `NavigationTimeoutError` with URL
- On CAPTCHA: save screenshot, raise `CaptchaDetectedError`
- Always close browser context in finally block

---

### 2.5 `app/core/vision.py` - Gemini Vision Module

**Purpose:** Send screenshots to Gemini 2.5 Flash and parse structured responses.

**Responsibilities:**
- Construct the extraction prompt (dual-mode: single product vs search list)
- Send image + prompt to Gemini API
- Parse JSON response and validate with Pydantic
- Handle API errors gracefully

**The Extraction Prompt:**
```
Act as a price extraction expert. Look at this screenshot of a webpage.
1. Identify if this is a Single Product Page or a Search Result List.
2. If it is a Single Product, find the current 'Buy Now' price.
3. If it is a Search List, find the price of the first/most relevant item.
4. Return ONLY a JSON object with:
   - product_name: string
   - price: float (numeric value only, no currency symbols)
   - currency: string (3-letter ISO code, e.g., "EUR")
   - store_name: string
   - page_type: "single_product" or "search_list"
   - confidence_score: float between 0.0 and 1.0
```

**Function Signatures:**

```
async def extract_price_data(image_bytes: bytes, api_key: str) -> ExtractionResult
    """Send image to Gemini and return parsed extraction result."""
    Raises: GeminiAPIError, ValidationError

def parse_gemini_response(response_text: str) -> ExtractionResult
    """Parse raw API response into validated model."""
```

**Error Handling:**
- API rate limit (429): raise with retry hint
- Invalid JSON response: raise `ValidationError` with raw response
- Network error: raise `GeminiAPIError` with details

---

### 2.6 `app/cli.py` - Command Line Interface

**Purpose:** Parse arguments, orchestrate extraction, and output results.

**Responsibilities:**
- Parse URL argument from command line
- Validate URL format
- Orchestrate: browser -> screenshot -> vision -> output
- Print JSON to stdout
- Print logs/warnings to stderr
- Return appropriate exit codes

**CLI Signature:**
```
python spy.py <URL> [--save-screenshot] [--verbose]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `URL` | Yes | Product or search page URL |
| `--save-screenshot` | No | Force save screenshot even on success |
| `--verbose` | No | Enable DEBUG level logging |

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (network, parsing) |
| 2 | CAPTCHA detected |
| 3 | API error (rate limit, auth) |
| 4 | Invalid URL |

**Output Contract:**

Success (stdout):
```json
{
  "product_name": "Example Product",
  "price": 29.99,
  "currency": "EUR",
  "store_name": "Amazon.nl",
  "page_type": "single_product",
  "confidence_score": 0.92
}
```

Low Confidence (stdout + stderr warning):
```
stderr: WARNING - Low confidence score (0.35), result may be inaccurate
stdout: {"product_name": "...", "confidence_score": 0.35, ...}
```

Error (stderr + exit code):
```
stderr: ERROR - CAPTCHA detected, screenshot saved to ./screenshots/error_1705356000.png
exit code: 2
```

---

## 3. Test Plan (TDD)

### 3.1 Unit Tests

**`tests/test_browser.py`:**
- `test_stealth_context_has_correct_user_agent`
- `test_stealth_context_has_dutch_locale`
- `test_stealth_context_has_amsterdam_timezone`
- `test_capture_screenshot_returns_png_bytes`
- `test_detect_captcha_returns_true_for_captcha_page`
- `test_navigation_timeout_raises_error`

**`tests/test_vision.py`:**
- `test_parse_valid_json_response`
- `test_parse_invalid_json_raises_error`
- `test_validation_rejects_negative_price`
- `test_validation_rejects_invalid_currency_code`
- `test_validation_rejects_confidence_out_of_range`

**`tests/test_models.py`:**
- `test_extraction_result_serializes_to_json`
- `test_extraction_error_includes_screenshot_path`

### 3.2 Integration Tests

**`tests/test_cli.py`:**
- `test_cli_with_valid_url_returns_json` (mock Gemini)
- `test_cli_with_invalid_url_exits_code_4`
- `test_cli_saves_screenshot_on_error`
- `test_cli_warns_on_low_confidence`

### 3.3 End-to-End Tests (Manual Verification)

Run within Docker container:
```bash
# Test Amazon.nl product page
docker exec -it universal_price_spy python spy.py "https://www.amazon.nl/dp/B08N5WRWNW"

# Test Google Shopping search
docker exec -it universal_price_spy python spy.py "https://www.google.nl/shopping/search?q=airpods"
```

**Verification Checklist:**
- [ ] No CAPTCHA triggered
- [ ] Valid JSON output
- [ ] Confidence score > 0.5
- [ ] Price value is reasonable
- [ ] Screenshot NOT saved (success case)

---

## 4. Dependencies

**requirements.txt:**
```
playwright>=1.40.0
google-generativeai>=0.3.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

**Playwright Browser Install:**
```bash
playwright install chromium
```

---

## 5. Docker Considerations (ARM64)

- Base image must support ARM64: `python:3.10-slim-bookworm`
- Playwright Chromium has ARM64 binaries available
- Install system dependencies: `libnss3`, `libatk1.0-0`, etc.
- Set environment: `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`

---

## 6. Implementation Order

Following TDD "Red-Green-Refactor" cycle:

### Phase 1: Foundation
1. Create `app/config.py` with Settings class
2. Create `app/utils/logger.py` with structured logging
3. Create `app/core/models.py` with Pydantic models
4. Write tests for models (`test_models.py`)
5. Verify tests pass

### Phase 2: Browser Module
1. Write `test_browser.py` tests (RED)
2. Implement `app/core/browser.py` (GREEN)
3. Refactor for clarity

### Phase 3: Vision Module
1. Write `test_vision.py` tests (RED)
2. Implement `app/core/vision.py` (GREEN)
3. Refactor for clarity

### Phase 4: CLI Integration
1. Write `test_cli.py` tests (RED)
2. Implement `app/cli.py` (GREEN)
3. Create `spy.py` wrapper script
4. Refactor for clarity

### Phase 5: Docker & E2E
1. Update Dockerfile for all dependencies
2. Build and run in Docker
3. Execute manual E2E tests
4. Document any issues for Slice 2

---

## 7. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| CAPTCHA triggered | Medium | High | Tune stealth settings, add delays between requests |
| Gemini rate limiting | Low | Medium | Implement exponential backoff, document limits |
| ARM64 compatibility issues | Low | High | Test early in Docker on actual Pi |
| Screenshot too large for API | Low | Medium | Compress PNG, crop to above-fold only |

---

## 8. Definition of Done

Slice 1 is complete when:
- [ ] All unit tests pass (`pytest`)
- [ ] Integration tests pass with mocked Gemini
- [ ] E2E test succeeds on Amazon.nl within Docker
- [ ] E2E test succeeds on Google Shopping within Docker
- [ ] No CAPTCHA triggers in 5 consecutive runs
- [ ] Documentation updated with actual usage examples
- [ ] Code reviewed for security (no hardcoded secrets)
