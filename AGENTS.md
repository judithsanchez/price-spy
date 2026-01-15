## 1. Project Overview
* **Mission:** A stealthy, visual-first price tracker.
* **Tech Stack:** Raspberry Pi 5 (ARM64), Docker, Python 3.10+, Playwright (Chromium), Gemini 2.5 Flash (Vision API).
* **Methodology:** Using screenshots + Computer Vision to bypass anti-bot measures.

## 2. Infrastructure Constraints
* **Host OS:** Raspberry Pi OS.
* **Architecture:** ARM64 (All Docker images/binaries MUST be compatible).
* **Environment:** Everything runs inside Docker containers.
* **Remote Access:** Secured via Tailscale.

## 3. Development & Quality Standards (TDD)
We follow a strict **Test-Driven Development (TDD)** approach to ensure amazing quality:
* **Plan:** Before any code is written, define the logic and the "test scenario" (Red phase).
* **Document:** Record the feature specs and the expected test outcome in the `/docs` folder.
* **Confirm:** Run tests within the Docker container to verify success (Green phase) before proceeding to refactoring or the next slice.

## 4. Operational Workflow for AI Agents
For every task, the AI must follow this "Plan-Document-Confirm" cycle:
1.  **Plan:** Propose the technical logic and the specific tests (unit/integration) to be written first.
2.  **Document:** Provide the Markdown text for the relevant spec file or roadmap update.
3.  **Confirm:** Detail the verification steps (e.g., specific `pytest` commands) to prove the feature works as intended within the Pi/Docker environment.

## 5. Architectural Principles
* **Professional Grade:** Maintain a clean, modular structure. 
* **Small Iterations:** No massive refactors; grow the product one verified test at a time.
* **Hardware Sensitivity:** Suggestions must be optimized for the Raspberry Pi 5's resource limits and ARM64 architecture.
