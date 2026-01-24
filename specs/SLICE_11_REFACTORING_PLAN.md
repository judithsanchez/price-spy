# Slice 11: Refactoring & Architecture Improvements

**STATUS: SUPERSEDED** ✅ (Updated January 2026)

> [!IMPORTANT]
> The remaining tasks from this refactoring plan have been migrated to [SLICE_12_FINAL_REFACTOR_AND_CLEANUP.md](file:///home/judithvsanchezc/Desktop/dev/price-spy/specs/SLICE_12_FINAL_REFACTOR_AND_CLEANUP.md) for better focus.

## 1. Assessment
After analyzing the current codebase, I have identified 5 key areas that offer high-impact improvements with manageable effort. These changes target technical debt, code duplication, and configuration management.

### Identified Opportunities

1.  **Modularize the CLI (`spy.py`)**
    *   **Context:** `spy.py` is currently a monolithic script (~400 lines) handling argument parsing, database connections, and business logic for all commands.
    *   **Impact:** High. It hinders testability and makes adding new commands risky.
    *   **Difficulty:** Easy.

2.  **Centralize Configuration (`app/core/config.py`)** [DONE]
3.  **Unify Vision Extraction Logic (`app/core/vision.py`)** [PARTIAL - Structured output implemented]
4.  **Extract Email Templates (`app/templates/`)** [DONE]

5.  **Create a Service Layer**
    *   **Context:** The CLI interacts directly with Repositories. Business logic (like orchestration of tracking setup) is embedded in the CLI command functions.
    *   **Impact:** High. Prevents logic reuse (e.g., if we add a Web API later).
    *   **Difficulty:** Medium.

## 2. Reasoning
The primary goal of this refactoring slice is to transition `price-spy` from a "script-based" architecture to a "application-based" architecture.

*   **Testability:** Moving logic out of `spy.py` and into Services/Commands allows for easier unit testing without mocking `sys.argv`.
*   **Robustness:** Centralized configuration with Pydantic ensures the app fails fast on startup if configuration is invalid, rather than crashing mid-operation.
*   **Maintainability:** Decoupling HTML generation from Python logic (Jinja2) allowing for easier UI updates.
*   **Extensibility:** a Service layer paves the way for future interfaces (like a REST API) to use the exact same business logic as the CLI.

## 3. Implementation Plan

This plan is ordered by dependency and impact.

### Phase 1: Foundation (Config & Vision) [IN PROGRESS]
1.  **Create `app/core/config.py`** [DONE]
    *   Implement `Settings` class using `pydantic-settings`.
    *   Define validation for `GEMINI_API_KEY`, `DATABASE_URL`, `SMTP_*`.
    *   Replace all `os.getenv` calls with `settings.attribute`.
2.  **Refactor `vision.py`** [PENDING]
    *   Deprecate `extract_product_info`.
    *   Standardize `extract_with_structured_output` as the single entry point.
    *   Ensure consistent return types (`ExtractionResult`).

### Phase 2: Separation of Concerns (Templates & CLI) [IN PROGRESS]
3.  **Email Templates** [DONE]
    *   Create `app/templates/email/daily_report.html` and `daily_report.txt`.
    *   Refactor `email_report.py` to use `jinja2` for rendering.
4.  **Modularize CLI** [PENDING]
    *   Create `app/cli/commands.py` (or individual modules).
    *   Move function implementations (`cmd_extract`, `cmd_track`, etc.) to the new module.
    *   Update `spy.py` to simply import and call these functions.

### Phase 3: Architecture (Service Layer) [PENDING]
5.  **Introduce Service Layer**:
    *   Create `app/services/` directory.
    *   Implement `TrackingService` (handles product/store validation + tracking creation).
    *   Implement `ExtractionService` (handles screenshot -> vision -> db flow).
    *   Update CLI commands to depend on Services instead of Repositories.
