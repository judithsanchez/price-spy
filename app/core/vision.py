"""Vision module for Gemini price extraction."""

import base64
import json
import aiohttp


EXTRACTION_PROMPT = """Act as a price extraction expert. Look at this screenshot of a webpage.
1. Identify if this is a Single Product Page or a Search Result List.
2. If it is a Single Product, find the current 'Buy Now' price.
3. If it is a Search List, find the price of the first/most relevant item.
4. Return ONLY a JSON object with:
   - product_name: string
   - price: float (numeric value only, no currency symbols)
   - currency: string (3-letter ISO code, e.g., "EUR")
   - store_name: string
   - page_type: "single_product" or "search_list"
   - confidence_score: float between 0.0 and 1.0

Return ONLY the JSON object, no other text."""


async def extract_price_data(image_bytes: bytes, api_key: str) -> dict:
    """Send image to Gemini and return extracted price data."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    # Encode image as base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": EXTRACTION_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=60) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Gemini API error {response.status}: {error_text}")

            data = await response.json()

    # Extract text response
    text = data["candidates"][0]["content"]["parts"][0]["text"]

    # Parse JSON from response (handle markdown code blocks)
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    result = json.loads(text)
    return result
