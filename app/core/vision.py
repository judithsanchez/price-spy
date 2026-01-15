"""Vision module for Gemini price extraction."""

import base64
import aiohttp


SIMPLE_PROMPT = """Look at this screenshot of a product page.
Tell me the product name and price. Keep it short and simple."""


async def extract_product_info(image_bytes: bytes, api_key: str) -> str:
    """Send image to Gemini and return product name and price as free text."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SIMPLE_PROMPT},
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

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return text.strip()
