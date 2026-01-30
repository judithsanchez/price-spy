# Development Rules

**⚠️ STRICT COMPLIANCE:** Any deviation from the validation rules (linting, type checking, tests) via suppression mechanisms (e.g., `noqa`, `type: ignore`, `skip_issues`) is **FORBIDDEN** unless explicit permission is granted by the USER.


- **Workflow:** Always use Test-Driven Development (TDD). Write the test first, verify failure, then implement.
- **Documentation:** Only update documentation (READMEs, logs, etc.) at the **end** of a completed task. Do not update docs for every incremental step.
- **Conciseness:** Be extremely brief. Skip conversational fillers and summaries of completed tool calls.
- **Permissions:** Do not ask for confirmation for read-only commands (ls, cat, grep, find).
- **Task Execution:** If a task has multiple logical steps, execute them sequentially without stopping to report progress unless an error occurs.
- **Database changes:** Do not make changes to the database schema without first having a migration strategy and checking how can it affect the current stored data.
- **Database Safety:** All tests must use a disposable temporary database. Connecting to `data/pricespy.db` during tests is strictly blocked by a safety guard in the `Database` class.
- **Database Versioning:** Use `python3 scripts/db_manager.py dump` to version the current data state in Git via `data/pricespy_dump.sql`. Binary `.db` files must NEVER be committed.
- **Database Migrations:** Place new `.sql` migrations in `migrations/`. Run them using `python3 scripts/db_manager.py migrate`. Applied migrations are tracked in the `_migrations` table.
- **DeepSource Configuration:** Do NOT add `skip_issues` or `ignore_issues` to `.deepsource.toml`. These must be managed via the DeepSource Dashboard UI.
- **Linting & Quality:** 
    - **Ruff** is the primary linter and formatter.
    - **Pylint** is maintained for `pylint-parity` checks in `app/`.
    - **Docstrings** are explicitly disabled across all linters (`D` rules in Ruff, `missing-docstring` in Pylint).
- **Useful Commands (Docker):**
    - **Run Tests:** `docker compose -f infrastructure/docker-compose.yml run --rm price-spy pytest`
    - **Lint & Format:** `docker compose -f infrastructure/docker-compose.yml run --rm price-spy sh -c "ruff check . && ruff format ."`
    - **Type Check:** `docker compose -f infrastructure/docker-compose.yml run --rm price-spy mypy .`
    - **Security Scan:** `docker compose -f infrastructure/docker-compose.yml run --rm price-spy bandit -r app/ --skip B101`
    - **Dependency Audit:** `docker compose -f infrastructure/docker-compose.yml run --rm price-spy pip-audit`
    - **Database Cleanup:** `docker compose -f infrastructure/docker-compose.yml run --rm price-spy python3 scripts/db_manager.py cleanup`
    - **Run Migrations:** `docker compose -f infrastructure/docker-compose.yml run --rm price-spy python3 scripts/db_manager.py migrate`
    - **Pre-commit:** If running locally, `pre-commit run --all-files` (requires local environment). Recommendation: Use Docker commands above for consistency.

- **DevOps Workflow:**
    - **Development:** Work on a branch in WSL/Local. Push and create a PR to `main`.
    - **Deployment:** Once merged, run `./scripts/deploy.sh` on the Raspberry Pi to sync and restart.
    - **DB Sync:** Run `./scripts/sync_prod_db.sh` on WSL to pull the latest production data for local testing.
- **Commit:** Before pushing make sure to rebase

## DevContainer Setup (Recommended)
This project is configured for **DevContainers**, allowing you to code inside the Docker environment.

**How to use:**
1.  Open the project in VS Code (or a compatible IDE).
2.  Click "Reopen in Container" when prompted.
3.  **Result**: You are now "inside" the `price-spy` container.
    -   **Python**: Uses the container's python (no venv needed).
    -   **Terminal**: Running `python` runs it in the container.
    -   **Running App**: `uvicorn` starts automatically via `docker-compose`.

**Working inside DevContainer:**
-   **Run Tests:** `pytest` (Directly! No need for `docker compose run...`)
-   **Lint:** `ruff check .`
-   **Type Check:** `mypy .`
-   **Git Commits:**
    -   The `pre-commit` hooks are configured for the *Host* machine (they call `docker compose`).
    -   Inside DevContainer, run checks manually (`ruff`, `mypy`) before committing.
    -   If hooks fail (due to missing docker socket), use `git commit --no-verify` and rely on CI/Host checks.