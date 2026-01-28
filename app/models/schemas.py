"""Pydantic models for Price Spy data validation."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductInfo(BaseModel):
    """Validated product information extracted from Gemini."""

    model_config = ConfigDict(str_strip_whitespace=True)

    product_name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0, le=1_000_000)
    currency: str = Field(default="EUR", pattern=r"^([A-Z]{3}|N/A)$")
    store_name: str | None = Field(default=None)
    page_type: Literal["single_product", "search_results"]
    confidence: float = Field(..., ge=0.0, le=1.0, alias="confidence_score")
    is_blocked: bool = Field(
        default=False, description="Whether the page is blocked by a modal"
    )

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        """Round price to 2 decimal places."""
        return round(v, 2)


class ExtractionContext(BaseModel):
    """Context information passed to the AI to improve extraction accuracy."""

    product_name: str
    category: str | None = None
    is_size_sensitive: bool = False
    target_size: str | None = None
    quantity_size: float | None = None
    quantity_unit: str | None = None
    screenshot_path: str | None = None


class ErrorRecord(BaseModel):
    """Record for error logging."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: int | None = None
    error_type: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    url: str | None = None
    screenshot_path: str | None = None
    stack_trace: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PriceHistoryRecord(BaseModel):
    """Database record for price history."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    item_id: int | None = None
    product_name: str
    price: float
    currency: str = "EUR"
    is_available: bool = True
    confidence: float
    url: str
    store_name: str | None = None
    page_type: str | None = None
    notes: str | None = None
    original_price: float | None = None
    deal_type: str | None = None
    discount_percentage: float | None = None
    discount_fixed_amount: float | None = None
    deal_description: str | None = None
    available_sizes: str | None = Field(
        default=None, description="JSON string of available sizes"
    )
    is_size_matched: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Product(BaseModel):
    """Master product concept - what you buy."""

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    id: int | None = None
    name: str = Field(..., min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    purchase_type: Literal["recurring", "one_time"] = "recurring"
    target_price: float | None = Field(default=None, gt=0)
    target_unit: str | None = Field(default=None, max_length=20)
    planned_date: str | None = Field(
        default=None, max_length=20, description="Target purchase date (e.g. 2026-W05)"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProductCreate(BaseModel):
    """Request model for creating a product."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    purchase_type: Literal["recurring", "one_time"] = "recurring"
    target_price: float | None = Field(default=None, gt=0)
    target_unit: str | None = Field(default=None, max_length=20)
    planned_date: str | None = Field(default=None, max_length=20)


class ProductUpdate(BaseModel):
    """Request model for partially updating a product."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    purchase_type: Literal["recurring", "one_time"] | None = None
    target_price: float | None = Field(default=None, gt=0)
    target_unit: str | None = Field(default=None, max_length=20)
    planned_date: str | None = Field(default=None, max_length=20)


class ProductResponse(BaseModel):
    """Response model for product."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str | None = None
    purchase_type: str | None = None
    target_price: float | None = None
    target_unit: str | None = None
    planned_date: str | None = None
    created_at: datetime


class Store(BaseModel):
    """Store definition (Names only)."""

    model_config = ConfigDict(str_strip_whitespace=True)
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=100)


class StoreCreate(BaseModel):
    """Request model for creating a store."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100)


class StoreUpdate(BaseModel):
    """Request model for partially updating a store."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=100)


class StoreResponse(BaseModel):
    """Response model for store."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TrackedItem(BaseModel):
    """URL to track - linked to product and store."""

    model_config = ConfigDict(str_strip_whitespace=True)
    id: int | None = None
    product_id: int = Field(...)
    store_id: int = Field(...)
    url: str = Field(..., min_length=1)
    target_size: str | None = Field(default=None, max_length=50)
    quantity_size: float = Field(default=1.0, gt=0)
    quantity_unit: str = Field(..., min_length=1, max_length=20)
    items_per_lot: int = Field(default=1, ge=1)
    last_checked_at: datetime | None = None
    is_active: bool = True
    alerts_enabled: bool = True


class TrackedItemCreate(BaseModel):
    """Request model for creating a tracked item."""

    model_config = ConfigDict(str_strip_whitespace=True)
    product_id: int
    store_id: int
    url: str = Field(..., min_length=1)
    target_size: str | None = Field(default=None, max_length=50)
    quantity_size: float = Field(default=1.0, gt=0)
    quantity_unit: str = Field(..., min_length=1, max_length=20)
    items_per_lot: int = 1
    label_ids: list[int] | None = None


class TrackedItemUpdate(BaseModel):
    """Request model for partially updating a tracked item."""

    model_config = ConfigDict(str_strip_whitespace=True)
    product_id: int | None = None
    store_id: int | None = None
    url: str | None = None
    target_size: str | None = None
    quantity_size: float | None = None
    quantity_unit: str | None = None
    items_per_lot: int | None = None
    is_active: bool | None = None
    alerts_enabled: bool | None = None
    label_ids: list[int] | None = None


class TrackedItemResponse(BaseModel):
    """Response model for tracked item."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    store_id: int
    url: str
    target_size: str | None = None
    quantity_size: float
    quantity_unit: str
    items_per_lot: int
    last_checked_at: datetime | None = None
    is_active: bool
    alerts_enabled: bool
    labels: list["LabelResponse"] = []


class PriceComparison(BaseModel):
    """Price comparison result."""

    current_price: float = Field(..., gt=0)
    previous_price: float | None = Field(default=None, gt=0)
    price_change: float | None = None
    price_change_percent: float | None = None
    volume_price: float | None = Field(default=None, gt=0)
    volume_unit: str | None = Field(default=None, max_length=20)
    is_price_drop: bool = False
    is_deal: bool = False
    original_price: float | None = None
    deal_type: str | None = None
    discount_percentage: float | None = None
    discount_fixed_amount: float | None = None
    deal_description: str | None = None


class ExtractionResult(BaseModel):
    """Guaranteed structured output from Gemini.

    This model represents the structured JSON response from Gemini
    when using response_mime_type: "application/json".
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    price: float = Field(..., ge=0, le=1_000_000, description="Numeric price value")
    currency: str = Field(default="EUR", pattern=r"^([A-Z]{3}|N/A)$")
    is_available: bool = Field(..., description="In stock status")
    product_name: str = Field(..., min_length=1)
    store_name: str | None = Field(default=None)
    notes: str | None = Field(default=None, description="AI notes/observations")
    is_blocked: bool = Field(
        default=False, description="Whether the page is blocked by a modal"
    )
    original_price: float | None = Field(
        default=None, ge=0, description="Original price before discount"
    )
    deal_type: str | None = Field(
        default=None, max_length=50, description="The type of promotion detected"
    )
    discount_percentage: float | None = Field(
        default=None, description="The percentage value of the discount"
    )
    discount_fixed_amount: float | None = Field(
        default=None, description="The absolute currency value off"
    )
    deal_description: str | None = Field(
        default=None, description="Brief description of the deal"
    )
    available_sizes: list[str] = Field(
        default_factory=list, description="List of sizes currently in stock"
    )
    is_size_matched: bool = Field(
        default=True,
        description="Whether the extracted price is confirmed for the target size",
    )
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        """Round price to 2 decimal places."""
        return round(v, 2)


class ExtractionLog(BaseModel):
    """Log entry for extraction attempts (success or failure)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: int | None = None
    tracked_item_id: int
    status: Literal["success", "error"] = "success"
    model_used: str | None = None
    price: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, pattern=r"^([A-Z]{3}|N/A)$")
    error_message: str | None = Field(default=None, max_length=2000)
    duration_ms: int | None = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Category(BaseModel):
    """Category definition for products."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: int | None = None
    name: str = Field(..., min_length=1, max_length=100)
    is_size_sensitive: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CategoryCreate(BaseModel):
    """Request model for creating/updating a category."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100)
    is_size_sensitive: bool = False


class CategoryUpdate(BaseModel):
    """Request model for partially updating a category."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_size_sensitive: bool | None = None


class CategoryResponse(BaseModel):
    """Response model for category."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    is_size_sensitive: bool = False
    created_at: datetime


class Label(BaseModel):
    """Label for tracked items."""

    model_config = ConfigDict(str_strip_whitespace=True)
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=50)
    created_at: datetime | None = None


class LabelCreate(BaseModel):
    """Request model for creating a label."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=50)


class LabelUpdate(BaseModel):
    """Request model for partially updating a label."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=50)


class LabelResponse(BaseModel):
    """Response model for label."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    created_at: datetime


class Unit(BaseModel):
    """Unit definition for measurements."""

    model_config = ConfigDict(str_strip_whitespace=True)
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=20)


class UnitCreate(BaseModel):
    """Request model for creating a unit."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=20)


class UnitUpdate(BaseModel):
    """Request model for partially updating a unit."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=20)


class UnitResponse(BaseModel):
    """Response model for unit."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class PurchaseType(BaseModel):
    """Purchase type definition (recurring, etc)."""

    model_config = ConfigDict(str_strip_whitespace=True)
    id: int | None = None
    name: str = Field(..., min_length=1, max_length=50)


class PurchaseTypeCreate(BaseModel):
    """Request model for creating a purchase type."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=50)


class PurchaseTypeUpdate(BaseModel):
    """Request model for partially updating a purchase type."""

    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=50)


class PurchaseTypeResponse(BaseModel):
    """Response model for purchase type."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
