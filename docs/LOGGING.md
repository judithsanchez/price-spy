# Price Spy Logging System

Price Spy maintains a comprehensive logging system to monitor AI performance, track operational health, and manage API quotas.

## 1. Logging Categories

The system distinguishes between three main levels of operational history:

### A. Extraction Logs (`extraction_logs` table)
Tracks every individual attempt by the AI to read a price from a URL.
- **Trigger**: Every manual or scheduled extraction.
- **Purpose**: Monitor the success rate of different AI models and debug specific URL failures.
- **Key Data**: `status` (success/error), `model_used`, `duration_ms`, and `error_message` for failures.

### B. System Error Logs (`error_log` table)
Captures application-level exceptions, configuration errors, and unexpected crashes.
- **Trigger**: Unhandled FastAPI exceptions, Pydantic validation failures, or explicit `logger.error()` calls.
- **Purpose**: Centralized debugging for developers.
- **Key Data**: `error_type`, `message`, `stack_trace`, and optional `url`.

### C. Scheduler Run Logs (`scheduler_runs` table)
Tracks high-level execution of the background crawler.
- **Trigger**: Start and completion of the daily scheduled task.
- **Purpose**: Verify that the daily crawl ran successfully and see how many items were processed.
- **Key Data**: `items_total`, `items_success`, `items_failed`.

## 2. Technical Implementation

### The Global Error Logger
Price Spy uses a dedicated utility in `app/core/error_logger.py` to persist critical errors to the database. This utility is integrated into:
1.  **FastAPI Middleware**: Catch-all handlers for 500 errors and 422 validation errors.
2.  **Standard Logging Hook**: Our custom `JSONFormatter` in `app/utils/logging.py` is configured to automatically call the database logger for any log message with level `ERROR` or above.

### Usage in Code
To log an error that should appear in the UI:
```python
import logging
logger = logging.getLogger(__name__)

# This will be printed to console AND saved to the database error_log table
logger.error("Something went wrong!", extra={"db_error_type": "api_failure"})
```

## 3. Quota Management (`api_usage` table)

To stay within the free tier of the Gemini API (e.g., 15 Requests Per Minute / 1,500 Per Day), the system uses the `RateLimitTracker`.
- **Function**: Increments usage counts before every AI call.
- **Behavior**: If a model hits its limit (RPD), it is marked as "exhausted" for the remainder of the UTC day, and the system automatically falls back to secondary models if available.

## 4. Viewing Logs

All logs are accessible via the internal API or the Web UI:
- **API**: `GET /api/logs` and `GET /api/errors`
- **UI**: Navigate to the "Logs" section in the dashboard to see extraction statistics and recent error reports.
