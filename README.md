A professional-grade, visual-first price tracking system running on **Raspberry Pi 5**. This project uses computer vision (Gemini 2.5 Flash) and stealth browser automation (Playwright) to monitor prices without being blocked by anti-bot measures.

## 📁 Project Structure

- **`AGENTS.md`**: Context and instructions for AI thought partners.
- **`docs/`**:
  - `PRODUCT_VISION.md`: The long-term goals and philosophy.
  - `ROADMAP.md`: The iterative development stages (Slices).
  - `SPECS_EXTRACTION_ENGINE.md`: Technical details for the scraper.
- **`infrastructure/`**: Docker and environment configuration.
- **`app/`**: Python source code and test suites.

## 🛠 Tech Stack

- **Host:** Raspberry Pi 5 (ARM64)
- **OS:** Raspberry Pi OS / Ubuntu Jammy (Docker)
- **Language:** Python 3.10+
- **Automation:** Playwright (Chromium)
- **AI:** Google Gemini 2.5 Flash (Vision API)
- **Database:** SQLite (Planned for Slice 2)

## 🚀 Quick Start (Slice 1)

1. **Prerequisites**: Ensure Docker and Docker Compose are installed on your Pi.
2. **Configuration**: Create a `.env` file with your `GEMINI_API_KEY`.
3. **Build**: `docker compose build`
4. **Run**: `docker exec -it universal_price_spy python spy.py "URL_HERE"`

## 🧪 Quality Assurance

This project follows **Test-Driven Development (TDD)**. All features must be planned and documented in the `docs/` folder before implementation, followed by automated verification within the Docker environment.
