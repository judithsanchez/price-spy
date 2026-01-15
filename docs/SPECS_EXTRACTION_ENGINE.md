## 1. Goal
Reliably capture a visual snapshot of any product or search page and extract structured price data using Gemini 1.5 Flash, while remaining undetected by anti-bot systems.

## 2. Stealth Browser Recipe (The "Masquerade")
To avoid CAPTCHAs on Amazon/Google, the Chromium instance must be configured with the following "Human-Like" traits:

### Context Configuration
* **User-Agent:** `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
* **Viewport:** 1920x1080 (Full HD desktop).
* **Locale:** `nl-NL`
* **Timezone:** `Europe/Amsterdam`
* **Permissions:** Grant `geolocation` to ensure Dutch pricing and shipping are shown.

### Detection Evasion
* **Automation Masking:** Set `navigator.webdriver` to `false`.
* **Resource Loading:** Allow all CSS and Images (Gemini needs the images), but block tracking scripts (e.g., Google Analytics) to save Pi CPU.

## 3. Visual Capture Strategy
1. **Trigger:** Receive URL via CLI.
2. **Navigation:** Go to URL with a timeout of 60 seconds.
3. **Wait Strategy:** Use `networkidle` to ensure all price overlays and currency symbols have loaded.
4. **Snapshot:** Capture a high-quality PNG of the "Above the Fold" area (top 1200px) where the price usually lives.

## 4. AI Vision Prompt (The "Dual-Mode" Logic)
The engine will send the following prompt to Gemini 1.5 Flash along with the screenshot:

> "Act as a price extraction expert. Look at this screenshot of a webpage.
> 1. Identify if this is a **Single Product Page** or a **Search Result List**.
> 2. If it is a Single Product, find the current 'Buy Now' price.
> 3. If it is a Search List, find the price of the first/most relevant item.
> 4. Return ONLY a JSON object with: product_name, price (float), currency (3-letter code), store_name, page_type, and confidence_score (0.0 to 1.0)."

## 5. Verification Contract (TDD)
A test is successful if the engine:
* Navigates to a test URL without triggering a CAPTCHA.
* Saves a readable `.png` to the `/screenshots` folder.
* Returns a valid JSON object that matches the defined schema.
