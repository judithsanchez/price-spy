
import asyncio
import os
import base64
import json
import aiohttp
from app.core.config import settings
from app.core.browser import capture_screenshot
from app.core.gemini import GeminiModels

PROMO_PROMPT = """Analyze this product page screenshot from Etos.
Identify any active promotions, discounts, or deals.

Specifically look for:
1. Current Price
2. Original Price (if strike-through price exists)
3. Deal type (e.g., 'Discount', 'BOGO', '1+1 gratis', '2e halve prijs', '3 voor 10', etc.)
4. Promotion end date (if mentioned)
5. Any other conditions (e.g., 'Only for members')

Return the response as a JSON object with these fields:
- current_price: float
- original_price: float or null
- deal_type: string or null
- deal_description: string or null
- end_date: string or null
- is_member_only: boolean
- model_used: string
"""

async def test_promo_extraction(url):
    print(f"Capturing screenshot: {url}")
    screenshot = await capture_screenshot(url)
    
    image_base64 = base64.b64encode(screenshot).decode("utf-8")
    
    api_key = settings.GEMINI_API_KEY
    model_config = GeminiModels.VISION_EXTRACTION
    api_url = GeminiModels.get_api_url(model_config, api_key)
    
    payload = {
        "contents": [{
            "parts": [
                {"text": PROMO_PROMPT},
                {"inline_data": {"mime_type": "image/png", "data": image_base64}}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    print("Asking Gemini about promotions...")
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, timeout=60) as response:
            data = await response.json()
            
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    print("\n--- PROMOTION EXTRACTION RESULT ---")
    print(text)
    print("-----------------------------------\n")

if __name__ == "__main__":
    url = "https://www.etos.nl/producten/andrelon-pink-big-volume-droogshampoo-250-ml-120258111.html"
    asyncio.run(test_promo_extraction(url))
