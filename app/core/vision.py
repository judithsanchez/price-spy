"""Vision module for Gemini price extraction."""

import base64
import json
import aiohttp
from typing import Union

from app.models.schemas import ProductInfo
from app.utils.logging import get_logger

logger = get_logger(__name__)


STRUCTURED_PROMPT = """Act as a price extraction expert. Analyze this screenshot of a webpage.

Your task:
1. Identify if this is a Single Product Page or a Search Result List
2. Extract the price information

Return ONLY a valid JSON object with these exact fields:
{
    "product_name": "string (the product name)",
    "price": number (the price as a float, e.g., 19.99),
    "currency": "string (3-letter ISO code, e.g., EUR, USD)",
    "store_name": "string or null (the retailer name)",
    "page_type": "single_product" or "search_results",
    "confidence_score": number (your confidence from 0.0 to 1.0)
}

Important:
- Return ONLY the JSON, no markdown, no explanation
- Price must be a number, not a string
- Use "EUR" for euros, "USD" for dollars, etc.
"""


async def extract_product_info(image_bytes: bytes, api_key: str) -> Union[ProductInfo, str]:
    """
    Send image to Gemini and return validated ProductInfo.

    Returns ProductInfo if JSON parsing succeeds, otherwise returns raw text.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": STRUCTURED_PROMPT},
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

    logger.info("Sending image to Gemini API", extra={"image_size": len(image_bytes)})

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=60) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(
                    "Gemini API error",
                    extra={"status": response.status, "error": error_text[:200]}
                )
                raise Exception(f"Gemini API error {response.status}: {error_text}")

            data = await response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Try to parse as JSON and validate with Pydantic
    try:
        # Clean up markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        parsed = json.loads(text)
        product_info = ProductInfo(**parsed)

        logger.info(
            "Price extracted successfully",
            extra={
                "product": product_info.product_name[:50],
                "price": product_info.price,
                "confidence": product_info.confidence
            }
        )

        return product_info

    except (json.JSONDecodeError, Exception) as e:
        logger.warning(
            "Failed to parse structured response, returning raw text",
            extra={"error": str(e)}
        )
        return text
