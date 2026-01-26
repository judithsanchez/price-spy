# AI Price Extraction (The "Brain")

Price Spy uses a visual-first approach to price tracking. Instead of parsing fragile HTML, it uses Gemini AI to "see" the page just as a human would.

## 1. Structured Output (The Schema)

To ensure consistency, the system forces the AI to return data in a strict JSON format via the `EXTRACTION_SCHEMA` in `app/core/vision.py`.

### Schema Fields
- **price**: The numeric selling price.
- **currency**: ISO 3-letter code (EUR, USD, etc.).
- **is_available**: Whether the specific item is in stock and purchasable.
- **product_name**: The name extracted from the page.
- **store_name**: The name of the retailer.
- **original_price**: Pre-discount price (if visible).
- **available_sizes**: A list of all selectable sizes found on the page.
- **is_blocked**: True if a cookie banner or modal is obstructing the view.

## 2. Context-Aware Prompting

The system doesn't just send a screenshot; it sends an **Extraction Context** to tell the AI exactly what to look for. This prevents the AI from picking up the "wrong" products in a search list or recommendation panel.

### Injected Context
Before calling the AI, the script fetches:
1.  **Search Target**: The name of the product you expect to find.
2.  **Specific Size**: Your target size (e.g., "M", "42", "500ml").
3.  **Category**: Whether the item is "Size Sensitive" (Clothing/Shoes).

## 3. Size Sensitivity Nuances

One of the most powerful features is the handling of availability based on size.

### Case A: Clothing & Shoes (Size-Sensitive)
When a category is marked as size-sensitive, the prompt instructs the AI:
- **Rule**: If the user's `target_size` (e.g., "Size M") is greyed out, has a strikethrough, or is otherwise not selectable, the AI MUST return `is_available: false`.
- **Nuance**: Even if the product is "in stock" for other sizes (e.g., XL is available), if *your* size is out, the Price Spy considers the item unavailable for you.

### Case B: Volume-Based Items (Bottles/Packs)
For items like beverages or cleaning supplies:
- **Rule**: The AI verifies that the item on the page matches the `quantity_size` (e.g., 500) and `quantity_unit` (e.g., "ml").
- **Nuance**: This prevents the system from triggering a "Price Drop" deal if it accidentally captures a smaller, cheaper bottle of the same product.

## 4. Technical Workflow

1.  **Stealth Capture**: Playwright takes a screenshot using a consumer-grade User-Agent.
2.  **Context Assembly**: `schemas.ExtractionContext` is populated from the DB.
3.  **Prompt Generation**: `get_extraction_prompt(context)` builds the personalized instructions.
4.  **API Call**: The image + prompt + schema are sent to Gemini.
5.  **Validation**: The response is validated using Pydantic before being saved to `price_history`.

## 5. Rate Limiting & Fallback

The system tracks every request in the `api_usage` table. If `gemini-2.5-flash` hits its rate limit (429), the system automatically falls back to `gemini-2.5-flash-lite` to ensure your daily tracking isn't interrupted.
