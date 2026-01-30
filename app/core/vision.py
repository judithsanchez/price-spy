"""Vision module for Gemini price extraction."""

import base64
import json
import re

import aiohttp

from app.core.gemini import GeminiModels, ModelConfig, is_rate_limit_error
from app.models.schemas import ExtractionContext, ExtractionResult, ProductInfo
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Constants for magic values
HTTP_OK = 200
PROMPT_PREVIEW_LEN = 500
MAX_ERROR_PREVIEW = 200


class GeminiAPIError(Exception):
    """Exception raised for Gemini API errors."""


# JSON Schema for Gemini structured outputs
EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "price": {"type": "number", "description": "The numeric price value"},
        "currency": {
            "type": "string",
            "description": "3-letter currency code (e.g., EUR, USD)",
        },
        "is_available": {
            "type": "boolean",
            "description": "Whether the product is in stock",
        },
        "product_name": {"type": "string", "description": "The name of the product"},
        "store_name": {
            "type": "string",
            "description": "The name of the store/retailer",
        },
        "is_blocked": {
            "type": "boolean",
            "description": "Whether the page is blocked by a modal",
        },
        "original_price": {
            "type": "number",
            "description": "The original price before any discount",
        },
        "deal_type": {
            "type": "string",
            "enum": [
                "bogo",
                "multibuy",
                "percentage_off",
                "fixed_amount_off",
                "second_unit_discount",
                "value_pack",
                "clearance",
                "none",
            ],
        },
        "discount_percentage": {
            "type": "number",
            "description": (
                "The percentage value of the discount (e.g., 20 for 20% off). "
                "Only fill if deal_type is percentage_off."
            ),
        },
        "discount_fixed_amount": {
            "type": "number",
            "description": (
                "The absolute currency value off (e.g., 5 for €5 off). "
                "Only fill if deal_type is fixed_amount_off."
            ),
        },
        "deal_description": {"type": "string"},
        "available_sizes": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "List of sizes currently in stock and selectable "
                "(e.g. ['28', '30', 'XS', 'M'])"
            ),
        },
        "is_size_matched": {
            "type": "boolean",
            "description": (
                "True if the price is confirmed to be for the target size, "
                "False if unknown but a price/discount exists."
            ),
        },
        "notes": {"type": "string"},
        "is_screenshot_faulty": {
            "type": "boolean",
            "description": (
                "Whether the screenshot is de-centered, cut off, or low quality "
                "(e.g., product or price is not fully visible)"
            ),
        },
    },
    "required": ["price", "currency", "is_available", "product_name"],
}


STRUCTURED_PROMPT = """Act as a price extraction expert.
Analyze this screenshot of a webpage.

Your task:
1. Identify if this is a Single Product Page or a Search Result List
2. Extract the price information, including original prices and any
   discounts or deals.

Return ONLY a valid JSON object with these exact fields:
{
    "product_name": "string (the product name)",
    "price": number (the price as a float, e.g., 19.99),
    "currency": "string (3-letter ISO code, e.g., EUR, USD)",
    "store_name": "string or null (the retailer name)",
    "page_type": "single_product" or "search_results",
    "is_available": boolean,
    "available_sizes": ["size1", "size2", ...],
    "original_price": number or null,
    "deal_type": "string or null",
    "deal_description": "string or null",
    "confidence_score": number (your confidence from 0.0 to 1.0),
    "is_blocked": boolean (true if a modal/consent banner blocks
major content),
    "is_size_matched": boolean (true if you are CERTAIN the price is for
the requested size),
    "is_screenshot_faulty": boolean (true if the screenshot is de-centered,
cut off, or unreadable)
}

Important for Clothing:
- Look for size selectors (labeled as 'Maat', 'Size', 'Mate', etc.).
- List only the sizes that appear to be IN STOCK (not greyed out or struck through).
- If multiple prices exist for different sizes, use the most prominent
  or 'starting at' price.

Important:
- If is_blocked is true, still try to extract what you can, but set is_blocked: true.
- CRITICAL: If a cookie banner, login screen, or modal covers the product or price, set is_blocked: true. 
- DO NOT set is_available: false just because you can't see the price due to a modal. 
- Only set is_available: false if you can clearly see "Out of Stock", "Sold Out", or a disabled "Add to Cart" button.
- If you CANNOT find the price or currency, use 0.0 for price and "N/A" for currency.
- ALWAYS extract the original price and strikethrough prices to detect discounts.

Return ONLY the JSON, no markdown, no explanation.
"""


async def extract_product_info(image_bytes: bytes, api_key: str) -> ProductInfo | str:
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
                    {"inline_data": {"mime_type": "image/png", "data": image_base64}},
                ]
            }
        ]
    }

    logger.info("Sending image to Gemini API", extra={"image_size": len(image_bytes)})

    async with aiohttp.ClientSession() as session:
        timeout = aiohttp.ClientTimeout(total=60)
        async with session.post(url, json=payload, timeout=timeout) as response:
            if response.status != HTTP_OK:
                error_text = await response.text()
                logger.error(
                    "Gemini API error",
                    extra={
                        "status": response.status,
                        "error": error_text[:MAX_ERROR_PREVIEW],
                    },
                )
                msg = f"Gemini API error {response.status}: {error_text}"
                raise GeminiAPIError(msg)

            data = await response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    try:
        # Clean up markdown code blocks if present
        text = text.removeprefix("```json")
        text = text.removeprefix("```")
        text = text.strip()
        text = text.removesuffix("```")
        text = text.strip()
        parsed = json.loads(text)
        product_info = ProductInfo(**parsed)
    except Exception as e:
        logger.warning(
            "Failed to parse structured response, returning raw text",
            extra={"error": str(e)},
        )
        return text
    logger.info(
        "Price extracted successfully",
        extra={
            "product": product_info.product_name[:50],
            "price": product_info.price,
            "confidence": product_info.confidence,
        },
    )
    return product_info


def get_extraction_prompt(context: ExtractionContext | None = None) -> str:
    """Generate a refined extraction prompt based on context."""
    target_info = ""
    size_guidance = ""

    if context:
        target_info = (
            f"\nTARGET PRODUCT: {context.product_name} | "
            f"CATEGORY: {context.category or 'General'}\n"
        )

        if context.is_size_sensitive and context.target_size:
            target_info += (
                f"TARGET SIZE: {context.target_size} (This is a CLOTHING/SHOE item)\n"
            )
            size_guidance = (
                f"- This item is SIZE-SENSITIVE. You are looking for size "
                f"'{context.target_size}'.\n"
                f"- If size '{context.target_size}' is NOT selectable, is greyed out, "
                "or explicitly marked "
                "as 'Out of Stock', set is_available to false.\n"
                f"- If you see the price but cannot confirm it is for size "
                f"'{context.target_size}',\n"
                "set is_size_matched to false but still report the price and "
                "is_available=true\n"
                "if it looks like a general sale.\n"
                "- ALWAYS favor reporting a price with is_size_matched=false over "
                "reporting 'Out of Stock'\n"
                "if a discount is visible.\n"
            )
        elif context.quantity_size and context.quantity_unit:
            target_info += (
                f"TARGET VOLUME/SIZE: {context.quantity_size} {context.quantity_unit}\n"
            )
            size_guidance = (
                "- Verify the product matches the volume/size "
                f"'{context.quantity_size} {context.quantity_unit}'.\n"
                "- If the page shows a different size (e.g., in a list of results),\n"
                "prioritize finding the exact match.\n"
            )
        if context.target_size:
            target_info += f"TARGET SIZE: {context.target_size}\n"
            size_guidance = (
                f"- Look specifically for the version/size '{context.target_size}'.\n"
            )

    return f"""Act as a professional Personal Shopping Assistant. {target_info}
Analyze this webpage screenshot to extract pricing and availability information.

RULES:
- THE CURRENT PRICE: numeric value only.
  If multiple prices exist for different sizes and yours isn't selected,
  use the 'starting at' price or the most prominent price.
- Currency code: 3-letter ISO (EUR, USD, etc.).
- is_available: Boolean.
{size_guidance}- product_name: The name as shown on the site.
- store_name: The retailer name.
- is_blocked: Boolean (true if a cookie/consent modal blocks the view).
- is_screenshot_faulty: Boolean (true if the screenshot is de-centered,
  cut off, or unreadable).
- Original price: Only if a clear previous price is shown (strikethrough).
  ALWAYS look for this to detect discounts.
- Deal type: Choose from 'bogo', 'multibuy', 'percentage_off', 'fixed_amount_off',
  'second_unit_discount', 'value_pack', 'clearance', or 'none'.
- Discount: Extract percentage or fixed amount if applicable.
- deal_description: E.g., '1+1 gratis' or '20% off with code'.
- General Notes: Mention if the price is a general discount
  but you couldn't confirm the target size price.
- IMPORTANT: If a cookie banner, login screen, or login wall blocks the content, set is_blocked: true.
- DO NOT report as "Out of Stock" if the page is simply blocked. Assume available but blocked.
- IMPORTANT: If price is not immediately top-center, look for a STICKY BOTTOM BAR or
  "Add to Cart" button area. Fashion mobile sites often place the price there.

Return ONLY valid JSON. If is_blocked is true, provide your best guess.
If fields are missing, use 0.0 for price and "N/A" for currency.
"""


def _extract_json(text: str) -> str:
    """Extract the first valid JSON block from text."""
    # Find anything between first { and last }
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


async def _call_gemini_api(
    image_bytes: bytes,
    api_key: str,
    config: ModelConfig,
    context: ExtractionContext | None = None,
) -> ExtractionResult:
    """Make a single API call to Gemini with the given model config."""
    url = GeminiModels.get_api_url(config, api_key)
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt_text = get_extraction_prompt(context)

    # Log the prompt and context (including screenshot path)
    log_extras = {"model": config.model.value, "image_size": len(image_bytes)}
    if context and context.screenshot_path:
        log_extras["screenshot_path"] = context.screenshot_path

    logger.info(
        "Sending request to Gemini API",
        extra={
            **log_extras,
            "prompt_sample": prompt_text[:PROMPT_PREVIEW_LEN] + "..."
            if len(prompt_text) > PROMPT_PREVIEW_LEN
            else prompt_text,
        },
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": "image/png", "data": image_base64}},
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": EXTRACTION_SCHEMA,
        },
    }

    async with aiohttp.ClientSession() as session:
        timeout = aiohttp.ClientTimeout(total=60)
        async with session.post(url, json=payload, timeout=timeout) as response:
            if response.status != HTTP_OK:
                error_text = await response.text()
                logger.error(
                    "Gemini API error",
                    extra={"status": response.status, "model": config.model.value},
                )
                msg = f"Gemini API error {response.status}: {error_text}"
                raise GeminiAPIError(msg)

            data = await response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Log raw response
    logger.info(
        "Received raw response from Gemini",
        extra={"model": config.model.value, "raw_response": text},
    )

    json_text = _extract_json(text)
    result = ExtractionResult.model_validate_json(json_text)

    logger.info(
        "Extraction successful",
        extra={
            "model": config.model.value,
            "product": result.product_name[:50],
            "price": result.price,
        },
    )

    return result


async def extract_with_structured_output(
    image_bytes: bytes,
    api_key: str,
    tracker=None,
    context: ExtractionContext | None = None,
) -> tuple[ExtractionResult, str]:
    """
    Extract price using Gemini's structured output mode with automatic fallback.

    Tries models in priority order, falling back on rate limit errors.
    If a tracker is provided, records usage and marks exhausted models.

    Args:
        image_bytes: Screenshot image data
        api_key: Gemini API key
        tracker: Optional RateLimitTracker for usage tracking

    Returns:
        Tuple of (ExtractionResult, model_name) with price info and model used

    Raises:
        Exception: If all models fail or are exhausted
    """
    models_to_try = list(GeminiModels.VISION_MODELS)

    # If tracker provided, filter to available models
    if tracker:
        available = tracker.get_available_model(models_to_try)
        if not available:
            msg = "All Gemini models exhausted for today. Try again tomorrow."
            raise GeminiAPIError(msg)

        # Reorder to put available first, but maintain priority
        models_to_try = [available] + [m for m in models_to_try if m != available]

    last_error = None

    for config in models_to_try:
        try:
            result = await _call_gemini_api(image_bytes, api_key, config, context)
        except Exception as e:
            last_error = e
            error_msg = str(e)

            # Check if rate limited
            if is_rate_limit_error(error_msg):
                logger.warning(
                    "Rate limit hit, trying fallback",
                    extra={"model": config.model.value},
                )
                if tracker:
                    tracker.mark_exhausted(config)
                continue  # Try next model

            # Non-rate-limit error, don't try fallback
            raise
        # Record successful usage
        if tracker:
            tracker.record_usage(config)

        return result, config.model.value

    # All models failed
    raise last_error or Exception("All models failed")
