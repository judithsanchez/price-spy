# Slice 12: Final Refactor & Maintenance

**STATUS: PLANNED** 📅 (January 2026)

## Overview

**Objective:** Finalize the transition to a service-oriented architecture, modularize the CLI, and implement essential maintenance tasks for disk space management.

## 1. Modularize CLI
**Problem:** `spy.py` is a monolithic file containing both orchestration logic and CLI boilerplate.
**Solution:** Move command implementations to `app/cli/commands.py`.

### Changes:
- [ ] Create `app/cli/commands.py`.
- [ ] Move `cmd_extract`, `cmd_check`, `cmd_track`, etc., to the new module.
- [ ] Refactor `spy.py` to be a thin entry point using `argparse` and calling the modular commands.

## 2. Introduce Service Layer
**Problem:** API routes and CLI commands directly manipulate repositories, leading to duplicate logic for extraction orchestration and validation.
**Solution:** Centralize logic in `app/services/`.

### Changes:
- [ ] Create `app/services/extraction_service.py`:
    - Orchestrate: Screenshot -> Vision -> DB Save -> Comparison.
- [ ] Create `app/services/tracking_service.py`:
    - Orchestrate: Product/Store validation -> TrackedItem creation.
- [ ] Update `app/api/main.py` and `app/cli/commands.py` to use these services.

## 3. Vision Cleanup
**Problem:** Redundant extraction functions in `vision.py`.
**Solution:** Remove legacy code and standardize.

### Changes:
- [ ] Remove `extract_product_info`.
- [ ] Ensure all callers (new services) use `extract_with_structured_output`.

## 4. Screenshot Cleanup
**Problem:** Long-term use will fill disk space with thousands of historical screenshots.
**Solution:** Implement a cleanup task or policy.

### Changes:
- [ ] Implement `app/services/maintenance_service.py`.
- [ ] Add `cleanup_old_screenshots()`:
    - Keep only the latest N screenshots per item OR screenshots from the last M days.
- [ ] Integrate cleanup into the daily scheduler run.

## 5. Production Data Management [DONE]
**Problem:** Committing binary `.db` files is bad practice; seed scripts are not suitable for production state management.
**Solution:** Implement SQL dumps for Git-friendly state versioning and remove seeder logic.

### Changes:
- [x] Update `.gitignore` to exclude binary Databases and backups.
- [x] Remove `app/core/seeder.py` and seed scripts.
- [x] Implement `scripts/db_manager.py` for SQL dump/restore.
- [x] Document production backup procedures in README.md.
- [x] Implement database safety guard for tests.

---

## Definition of Done
- [ ] CLI logic is modular and `spy.py` is under 100 lines.
- [ ] Service layer handles all coordination between extraction and storage.
- [ ] Legacy vision extraction code is removed.
- [ ] A scheduled task automatically removes old screenshots.
- [ ] All tests pass.
