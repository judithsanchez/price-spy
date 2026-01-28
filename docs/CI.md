# CI & Quality Control Documentation

This document outlines the strict quality guardrails enforced in the Price Spy project.

## Local Guardrails (Pre-commit)

We use a local Git hook to enforce **Atomic Commits**.

*   **Rule**: You cannot stage more than **10 files** in a single commit.
*   **Reason**: Small, atomic commits are easier to review, revert, and track.
*   **Bypass**: If you have a valid reason to exceed this limit (e.g., a massive refactor), use the `--no-verify` (or `-n`) flag:
    ```bash
    git commit -m "Massive refactor" --no-verify
    ```

---

## CI Guardrails (GitHub Actions)

The `CI Quality Check` workflow runs on every Push and Pull Request. Several checks are **Strict Blockers**.

### 1. Blockers (Build Failure)

| Check | Failure Condition | How to Bypass (PR Label) |
| :--- | :--- | :--- |
| **Branch Naming** | Not matching `^(feat\|fix\|docs\|test\|refactor\|chore)/[a-z0-9-]+$` | `skip-branch` |
| **PR Size** | Total lines changed > 500 | `skip-size` |
| **Doc Sync** | Files in `app/` changed but no changes in `docs/` or `README.md` | `skip-docs` |
| **Test Coverage** | Total coverage < 80% | `skip-coverage` |
| **Linting/Types** | Ruff errors or Mypy errors | `skip-lint`, `skip-typing` |

### 2. Available Bypass Labels

Add these labels to your GitHub Pull Request to bypass specific checks:

*   `skip-all`: Disables all quality checks (Use with caution).
*   `skip-lint`: Skips Python formatting and linting (Ruff).
*   `skip-typing`: Skips static type checking (Mypy).
*   *   `skip-security`: Skips Bandit security scans and Pip-audit.
*   `skip-branch`: Allows non-conventional branch names.
*   `skip-size`: Allows PRs larger than 500 lines.
*   `skip-docs`: Allows code changes without documentation updates.
*   `skip-coverage`: Allows merging with < 80% test coverage.
*   `skip-tests`: Skips the test suite entirely.
*   `skip-mutation`: Skips Mutation Testing (mutmut).

## How to Apply Labels
1. Go to your Pull Request on GitHub.
2. Click the gear icon next to **Labels** on the right sidebar.
3. Select the desired `skip-*` labels.
4. CI will automatically re-run (or you can trigger it manually).
