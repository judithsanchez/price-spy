"""Pydantic models for Price Spy data validation."""

from datetime import datetime, timezone
from typing import Literal, Optional, List

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProductInfo(BaseModel):
    """Validated product information extracted from Gemini."""

    model_config = ConfigDict(str_strip_whitespace=True)

    product_name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0, le=1_000_000)
    currency: str = Field(default="EUR", pattern=r"^([A-Z]{3}|N/A)$")
    store_name: Optional[str] = Field(default=None)
    page_type: Literal["single_product", "search_results"]
    confidence: float = Field(..., ge=0.0, le=1.0, alias="confidence_score")
    is_blocked: bool = Field(default=False, description="Whether the page is blocked by a modal")

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        """Round price to 2 decimal places."""
        return round(v, 2)


class ExtractionContext(BaseModel):
    """Context information passed to the AI to improve extraction accuracy."""
    product_name: str
    category: Optional[str] = None
    is_size_sensitive: bool = False
    target_size: Optional[str] = None
    quantity_size: Optional[float] = None
    quantity_unit: Optional[str] = None


class ErrorRecord(BaseModel):
    """Record for error logging."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: Optional[int] = None
    error_type: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    url: Optional[str] = None
    screenshot_path: Optional[str] = None
    stack_trace: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PriceHistoryRecord(BaseModel):
    """Database record for price history."""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    item_id: Optional[int] = None
    product_name: str
    price: float
    currency: str = "EUR"
    is_available: bool = True
    confidence: float
    url: str
    store_name: Optional[str] = None
    page_type: Optional[str] = None
    notes: Optional[str] = None
    original_price: Optional[float] = None
    deal_type: Optional[str] = None
    discount_percentage: Optional[float] = None
    discount_fixed_amount: Optional[float] = None
    deal_description: Optional[str] = None
    available_sizes: Optional[str] = Field(default=None, description="JSON string of available sizes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Product(BaseModel):
    """Master product concept - what you buy."""

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(default=None, max_length=100)
    purchase_type: Literal["recurring", "one_time"] = "recurring"
    target_price: Optional[float] = Field(default=None, gt=0)
    target_unit: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductCreate(BaseModel):
    """Request model for creating a product."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    purchase_type: Literal["recurring", "one_time"] = "recurring"
    target_price: Optional[float] = Field(default=None, gt=0)
    target_unit: Optional[str] = Field(default=None, max_length=20)


class ProductUpdate(BaseModel):
    """Request model for partially updating a product."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[str] = Field(default=None, max_length=100)
    purchase_type: Optional[Literal["recurring", "one_time"]] = None
    target_price: Optional[float] = Field(default=None, gt=0)
    target_unit: Optional[str] = Field(default=None, max_length=20)


class ProductResponse(BaseModel):
    """Response model for product."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str] = None
    purchase_type: Optional[str] = None
    target_price: Optional[float] = None
    target_unit: Optional[str] = None
    created_at: datetime


class Store(BaseModel):
    """Store definition (Names only)."""
    model_config = ConfigDict(str_strip_whitespace=True)
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)


class StoreCreate(BaseModel):
    """Request model for creating a store."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100)


class StoreUpdate(BaseModel):
    """Request model for partially updating a store."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class StoreResponse(BaseModel):
    """Response model for store."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TrackedItem(BaseModel):
    """URL to track - linked to product and store."""
    model_config = ConfigDict(str_strip_whitespace=True)
    id: Optional[int] = None
    product_id: int = Field(...)
    store_id: int = Field(...)
    url: str = Field(..., min_length=1)
    target_size: Optional[str] = Field(default=None, max_length=50)
    quantity_size: float = Field(default=1.0, gt=0)
    quantity_unit: str = Field(..., min_length=1, max_length=20)
    items_per_lot: int = Field(default=1, ge=1)
    last_checked_at: Optional[datetime] = None
    is_active: bool = True
    alerts_enabled: bool = True


class TrackedItemCreate(BaseModel):
    """Request model for creating a tracked item."""
    model_config = ConfigDict(str_strip_whitespace=True)
    product_id: int
    store_id: int
    url: str = Field(..., min_length=1)
    target_size: Optional[str] = Field(default=None, max_length=50)
    quantity_size: float = Field(default=1.0, gt=0)
    quantity_unit: str = Field(..., min_length=1, max_length=20)
    items_per_lot: int = 1
    label_ids: Optional[List[int]] = None


class TrackedItemUpdate(BaseModel):
    """Request model for partially updating a tracked item."""
    model_config = ConfigDict(str_strip_whitespace=True)
    product_id: Optional[int] = None
    store_id: Optional[int] = None
    url: Optional[str] = None
    target_size: Optional[str] = None
    quantity_size: Optional[float] = None
    quantity_unit: Optional[str] = None
    items_per_lot: Optional[int] = None
    is_active: Optional[bool] = None
    alerts_enabled: Optional[bool] = None
    label_ids: Optional[List[int]] = None


class TrackedItemResponse(BaseModel):
    """Response model for tracked item."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    store_id: int
    url: str
    target_size: Optional[str] = None
    quantity_size: float
    quantity_unit: str
    items_per_lot: int
    last_checked_at: Optional[datetime] = None
    is_active: bool
    alerts_enabled: bool
    labels: List["LabelResponse"] = []


class PriceComparison(BaseModel):
    """Price comparison result."""

    current_price: float = Field(..., gt=0)
    previous_price: Optional[float] = Field(default=None, gt=0)
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    volume_price: Optional[float] = Field(default=None, gt=0)
    volume_unit: Optional[str] = Field(default=None, max_length=20)
    is_price_drop: bool = False
    is_deal: bool = False
    original_price: Optional[float] = None
    deal_type: Optional[str] = None
    discount_percentage: Optional[float] = None
    discount_fixed_amount: Optional[float] = None
    deal_description: Optional[str] = None


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
    store_name: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None, description="AI notes/observations")
    is_blocked: bool = Field(default=False, description="Whether the page is blocked by a modal")
    original_price: Optional[float] = Field(default=None, ge=0, description="Original price before discount")
    deal_type: Optional[str] = Field(default=None, max_length=50, description="The type of promotion detected")
    discount_percentage: Optional[float] = Field(default=None, description="The percentage value of the discount")
    discount_fixed_amount: Optional[float] = Field(default=None, description="The absolute currency value off")
    deal_description: Optional[str] = Field(default=None, description="Brief description of the deal")
    available_sizes: list[str] = Field(default_factory=list, description="List of sizes currently in stock")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        """Round price to 2 decimal places."""
        return round(v, 2)


class ExtractionLog(BaseModel):
    """Log entry for extraction attempts (success or failure)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: Optional[int] = None
    tracked_item_id: int
    status: Literal["success", "error"] = "success"
    model_used: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, pattern=r"^([A-Z]{3}|N/A)$")
    error_message: Optional[str] = Field(default=None, max_length=2000)
    duration_ms: Optional[int] = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Category(BaseModel):
    """Category definition for products."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    is_size_sensitive: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CategoryCreate(BaseModel):
    """Request model for creating/updating a category."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100)
    is_size_sensitive: bool = False


class CategoryUpdate(BaseModel):
    """Request model for partially updating a category."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    is_size_sensitive: Optional[bool] = None


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
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=50)
    created_at: Optional[datetime] = None


class LabelCreate(BaseModel):
    """Request model for creating a label."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=50)


class LabelUpdate(BaseModel):
    """Request model for partially updating a label."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)


class LabelResponse(BaseModel):
    """Response model for label."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    created_at: datetime




class Unit(BaseModel):
    """Unit definition for measurements."""
    model_config = ConfigDict(str_strip_whitespace=True)
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=20)


class UnitCreate(BaseModel):
    """Request model for creating a unit."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=20)


class UnitUpdate(BaseModel):
    """Request model for partially updating a unit."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Optional[str] = Field(default=None, min_length=1, max_length=20)


class UnitResponse(BaseModel):
    """Response model for unit."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class PurchaseType(BaseModel):
    """Purchase type definition (recurring, etc)."""
    model_config = ConfigDict(str_strip_whitespace=True)
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=50)


class PurchaseTypeCreate(BaseModel):
    """Request model for creating a purchase type."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=50)


class PurchaseTypeUpdate(BaseModel):
    """Request model for partially updating a purchase type."""
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)


class PurchaseTypeResponse(BaseModel):
    """Response model for purchase type."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
