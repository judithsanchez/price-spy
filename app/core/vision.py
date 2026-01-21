"""Vision module for Gemini price extraction."""

import base64
import json
import aiohttp
from typing import Union, Optional, Tuple

from app.models.schemas import ProductInfo, ExtractionResult
from app.utils.logging import get_logger
from app.core.gemini import GeminiModels

logger = get_logger(__name__)


# JSON Schema for Gemini structured outputs
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "price": {"type": "number", "description": "The numeric price value"},
        "currency": {"type": "string", "description": "3-letter currency code (e.g., EUR, USD)"},
        "is_available": {"type": "boolean", "description": "Whether the product is in stock"},
        "product_name": {"type": "string", "description": "The name of the product"},
        "store_name": {"type": "string", "description": "The name of the store/retailer"},
        "is_blocked": {"type": "boolean", "description": "Whether the page is blocked by a cookie consent modal or login wall"}
    },
    "required": ["price", "currency", "is_available", "product_name"]
}


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
    "confidence_score": number (your confidence from 0.0 to 1.0),
    "is_blocked": boolean (true if a modal/consent banner blocks major content)
}

Important:
- If is_blocked is true, still try to extract what you can, but set is_blocked: true.

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
    url = GeminiModels.get_api_url(GeminiModels.VISION_EXTRACTION, api_key)

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


STRUCTURED_OUTPUT_PROMPT = """Extract price information from this product page screenshot.

Analyze the image and extract:
- The current price (numeric value only)
- Currency code (EUR, USD, GBP, etc.)
- Whether the product is in stock (available to buy)
- The product name
- The store/retailer name (if visible)
- Whether the page is blocked by a cookie consent modal (is_blocked: boolean)

Return the data as JSON. If is_blocked is true, provide the best guess for other fields.
"""


from app.core.gemini import ModelConfig, is_rate_limit_error


async def _call_gemini_api(
    image_bytes: bytes,
    api_key: str,
    config: ModelConfig
) -> ExtractionResult:
    """Make a single API call to Gemini with the given model config."""
    url = GeminiModels.get_api_url(config, api_key)
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": STRUCTURED_OUTPUT_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_base64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": EXTRACTION_SCHEMA
        }
    }

    logger.info(
        "Sending image to Gemini API",
        extra={"model": config.model.value, "image_size": len(image_bytes)}
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=60) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(
                    "Gemini API error",
                    extra={"status": response.status, "model": config.model.value}
                )
                raise Exception(f"Gemini API error {response.status}: {error_text}")

            data = await response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    result = ExtractionResult.model_validate_json(text)

    logger.info(
        "Extraction successful",
        extra={
            "model": config.model.value,
            "product": result.product_name[:50],
            "price": result.price
        }
    )

    return result


from typing import Tuple

async def extract_with_structured_output(
    image_bytes: bytes,
    api_key: str,
    tracker=None,
    preferred_model: Optional[str] = None
) -> Tuple[ExtractionResult, str]:
    """
    Extract price using Gemini's structured output mode with automatic fallback.

    Tries models in priority order, falling back on rate limit errors.
    If a tracker is provided, records usage and marks exhausted models.
    If preferred_model is provided, it is tried first.

    Args:
        image_bytes: Screenshot image data
        api_key: Gemini API key
        tracker: Optional RateLimitTracker for usage tracking
        preferred_model: Optional model name to try first

    Returns:
        Tuple of (ExtractionResult, model_name) with price info and model used

    Raises:
        Exception: If all models fail or are exhausted
    """
    models_to_try = list(GeminiModels.VISION_MODELS)

    # If preferred_model provided, move it to the front
    if preferred_model:
        config = GeminiModels.get_config_by_model(preferred_model)
        if config:
            # Remove if already in list to avoid duplicates
            models_to_try = [config] + [m for m in models_to_try if m.model.value != preferred_model]
        else:
            logger.warning(f"Preferred model '{preferred_model}' not found, using defaults")

    # If tracker provided, filter to available models
    if tracker:
        available = tracker.get_available_model(models_to_try)
        if available:
            # Reorder to put available first, but maintain priority
            models_to_try = [available] + [m for m in models_to_try if m != available]
        else:
            raise Exception("All Gemini models exhausted for today. Try again tomorrow.")

    last_error = None

    for config in models_to_try:
        try:
            result = await _call_gemini_api(image_bytes, api_key, config)

            # Record successful usage
            if tracker:
                tracker.record_usage(config)

            return result, config.model.value

        except Exception as e:
            last_error = e
            error_msg = str(e)

            # Check if rate limited
            if is_rate_limit_error(error_msg):
                logger.warning(
                    "Rate limit hit, trying fallback",
                    extra={"model": config.model.value}
                )
                if tracker:
                    tracker.mark_exhausted(config)
                continue  # Try next model

            # Non-rate-limit error, don't try fallback
            raise

    # All models failed
    raise last_error or Exception("All models failed")
