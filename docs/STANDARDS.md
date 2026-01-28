# Coding Standards & Development Rules

This document consolidates all coding standards, workflow rules, and quality guardrails for the Price Spy project.

## 1. Development Workflow

### Test-Driven Development (TDD)
- **Rule**: Always write the test first, verify it fails, then implement the logic to make it pass.
- Use `pytest` for testing.

### Documentation Timing
- **Rule**: Only update documentation (READMEs, `docs/`, logs) at the **end** of a completed task.
- Avoid incremental documentation updates to prevent cluttering commits.

### Atomic Commits
- **Rule**: A single commit should not exceed **10 modified files**.
- **Reason**: Small commits are easier to track and revert.
- **Bypass**: Use `git commit -m "..." --no-verify` to bypass this local hook if necessary.

---

## 2. Coding Standards

### Static Typing
- **Rule**: Strict type annotations are required for all source code.
- **Verification**: `mypy . --ignore-missing-imports` must return no errors.
- **Practices**: Use `Optional`, `List`, `Dict`, and `Any` from `typing` where appropriate. Ensure null safety for database returns and API inputs.

### Linting & Formatting
- **Rule**: Code must be formatted using **Ruff**.
- **Verification**: `ruff format --check .` and `ruff check .`
- **Correction**: Run `ruff format .` and `ruff check --fix .` locally before pushing.

### Logic & Safety
- **Exception Handling**: Avoid bare `except:` blocks; always specify the exception type.
- **Path Handling**: Always use `Path` from `pathlib` for file operations.
- **Timezone Safety**: Use `datetime.now(timezone.utc)` for all timestamps.

---

## 3. Database Guidelines

### Schema Changes
- **Rule**: Do not change the database schema without a migration strategy and checking the impact on existing data.

### Database Safety during Tests
- **Rule**: All tests **must** use a disposable temporary database.
- **Safety**: Connecting to the production/development `data/pricespy.db` during tests is strictly blocked in the `Database` class.

### Versioning
- **Rule**: Binary `.db` files must **NEVER** be committed to Git.
- **Versioning**: Use `python3 scripts/db_manager.py dump` to version the current data state into `data/pricespy_dump.sql`.

---

## 4. CI & Quality Guardrails

The CI pipeline enforces the following strict blockers on every Pull Request:

| Guardrail | Requirement | Bypass Label |
| :--- | :--- | :--- |
| **Branch Naming** | `^(feat\|fix\|docs\|test\|refactor\|chore)/[a-z0-9-]+$` | `skip-branch` |
| **PR Size** | Total lines changed < 500 | `skip-size` |
| **Doc Sync** | `app/` changes must be accompanied by `docs/` or `README.md` updates | `skip-docs` |
| **Coverage** | Total test coverage must be ≥ 80% | `skip-coverage` |
| **Static Analysis** | Zero Ruff / Mypy errors | `skip-lint` / `skip-typing` |

> [!NOTE]
> Bypass labels (e.g., `skip-all`, `skip-tests`) can be applied to PRs on GitHub to ignore these rules in exceptional cases.
