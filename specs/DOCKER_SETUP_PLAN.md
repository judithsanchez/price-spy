# Docker Setup Plan

## Overview

The Price Spy application must run inside a Docker container on a Raspberry Pi 5 (ARM64). This plan outlines the containerization strategy.

---

## 1. Requirements

| Requirement | Details |
|-------------|---------|
| Architecture | ARM64 (Raspberry Pi 5) |
| Base Image | `mcr.microsoft.com/playwright/python:v1.40.0-jammy` or `python:3.11-slim-bookworm` |
| Python | 3.10+ |
| Browser | Chromium (via Playwright) |
| Dependencies | playwright, aiohttp, python-dotenv, requests |

---

## 2. Dockerfile Strategy

### Option A: Playwright Official Image (Recommended for x86, may not work on ARM64)
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy
```
- Pre-installed browsers and dependencies
- May NOT have ARM64 support

### Option B: Build from Python Slim (ARM64 Compatible)
```dockerfile
FROM python:3.11-slim-bookworm
```
- Install Playwright and Chromium manually
- Requires system dependencies for Chromium
- ARM64 compatible

**Decision:** Use Option B for ARM64 compatibility.

---

## 3. System Dependencies for Playwright/Chromium

Chromium on ARM64 requires these packages:
```
libnss3
libnspr4
libatk1.0-0
libatk-bridge2.0-0
libcups2
libdrm2
libxkbcommon0
libxcomposite1
libxdamage1
libxfixes3
libxrandr2
libgbm1
libasound2
libpango-1.0-0
libcairo2
```

---

## 4. File Structure

```
infrastructure/
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

---

## 5. Dockerfile Outline

```dockerfile
FROM python:3.11-slim-bookworm

# Install system dependencies for Playwright/Chromium
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/
COPY pyproject.toml .

# Default command
CMD ["python", "-m", "pytest", "tests/", "-v"]
```

---

## 6. docker-compose.yml Outline

```yaml
version: "3.8"

services:
  price-spy:
    build:
      context: ..
      dockerfile: infrastructure/Dockerfile
    container_name: price_spy
    env_file:
      - ../.env
    volumes:
      - ../screenshots:/app/screenshots
    stdin_open: true
    tty: true
```

---

## 7. Commands

| Action | Command |
|--------|---------|
| Build | `docker compose -f infrastructure/docker-compose.yml build` |
| Run tests | `docker compose -f infrastructure/docker-compose.yml run --rm price-spy` |
| Run spy | `docker compose -f infrastructure/docker-compose.yml run --rm price-spy python spy.py "URL"` |
| Shell | `docker compose -f infrastructure/docker-compose.yml run --rm price-spy bash` |

---

## 8. Environment Variables

The `.env` file must be at project root with:
```
GEMINI_API_KEY=your_key_here
```

The container reads this via `env_file` in docker-compose.yml.

---

## 9. Testing Strategy

1. Build the container
2. Run `pytest` inside the container
3. Verify all tests pass (API key, browser screenshot, Gemini extraction)

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Playwright ARM64 Chromium issues | Use `playwright install chromium` which handles ARM64 |
| Large image size | Use slim base image, clean apt cache |
| Slow build on Pi | Build once, cache layers |

---

## 11. Definition of Done

- [ ] Dockerfile builds successfully on ARM64
- [ ] All tests pass inside container
- [ ] Can run `spy.py` from container with URL argument
- [ ] Screenshots persist to host via volume mount
