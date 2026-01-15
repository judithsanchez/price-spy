Product Vision: Universal Price Spy
1. Statement of Intent
The Universal Price Spy is a private, self-hosted price monitoring intelligence system designed to run on a Raspberry Pi 5. Its purpose is to bypass the technical barriers (anti-bot measures and complex HTML structures) of modern e-commerce sites like Amazon and Google Shopping using a "Visual-First" approach.

2. The Problem
Traditional price trackers rely on "scraping" the code (HTML) of a website. This is fragile because:

Websites frequently change their code structure, breaking the tracker.

Aggressive anti-bot services detect automated "code reading" and block the IP.

Complex sites (Javascript-heavy) require heavy resources to parse.

3. The Solution (The "Human-Like" Spy)
Instead of reading code, this tool sees the page just like a human does. By using a headless browser to take a screenshot and sending that image to Google Gemini 1.5 Flash, the system identifies prices based on visual context. If a human can see the price, the Spy can find it.

4. Core Values
Universal Compatibility: If it has a URL and a price tag, it can be tracked.

Stealth by Design: Operates within a Dockerized environment using specialized headers to blend in with standard Dutch consumer traffic.

Privacy-Centric: All data remains on the local Raspberry Pi 5. No third-party tracking services (other than the Gemini API call) are used.

Low Maintenance: No need to update "selectors" or "CSS paths" when a website changes its layout.

5. Future State (The "Dream" Product)
While starting as a manual CLI tool (Slice 1), the final product will:

Interface: Feature a clean, simple Web UI hosted on the Pi to manage tracked URLs.

Intelligence: Automatically detect price drops and "Buy Now" opportunities.

Connectivity: Integrate with Home Assistant to trigger local alerts (e.g., smart bulb color changes) and send mobile notifications via the HA app or email.
