"""Pydantic models for Price Spy data validation."""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProductInfo(BaseModel):
    """Validated product information extracted from Gemini."""

    model_config = ConfigDict(str_strip_whitespace=True)

    product_name: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., ge=0, le=1_000_000)
    currency: str = Field(default="EUR", pattern=r"^([A-Z]{3}|N/A)$")
    store_name: Optional[str] = Field(default=None, max_length=100)
    page_type: Literal["single_product", "search_results"]
    confidence: float = Field(..., ge=0.0, le=1.0, alias="confidence_score")
    is_blocked: bool = Field(default=False, description="Whether the page is blocked by a modal")

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        """Round price to 2 decimal places."""
        return round(v, 2)


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
    product_name: str
    price: float
    currency: str = "EUR"
    is_available: bool = True
    confidence: float
    url: str
    store_name: Optional[str] = None
    page_type: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Product(BaseModel):
    """Master product concept - what you buy."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(default=None, max_length=100)
    purchase_type: Literal["recurring", "one_time"] = "recurring"
    target_price: Optional[float] = Field(default=None, gt=0)
    preferred_unit_size: Optional[str] = Field(default=None, max_length=50)
    current_stock: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Store(BaseModel):
    """Store definition with shipping rules."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    shipping_cost_standard: float = Field(default=0, ge=0)
    free_shipping_threshold: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=500)


class TrackedItem(BaseModel):
    """URL to track - linked to product and store."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: Optional[int] = None
    product_id: int = Field(...)
    store_id: int = Field(...)
    url: str = Field(..., min_length=1)
    item_name_on_site: Optional[str] = Field(default=None, max_length=300)
    quantity_size: float = Field(..., gt=0)
    quantity_unit: str = Field(..., min_length=1, max_length=20)
    items_per_lot: int = Field(default=1, ge=1)
    preferred_model: Optional[str] = Field(default=None, max_length=50)
    last_checked_at: Optional[datetime] = None
    is_active: bool = True
    alerts_enabled: bool = True


class PriceComparison(BaseModel):
    """Price comparison result."""

    current_price: float = Field(..., gt=0)
    previous_price: Optional[float] = Field(default=None, gt=0)
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    volume_price: Optional[float] = Field(default=None, gt=0)
    volume_unit: Optional[str] = Field(default=None, max_length=20)
    is_price_drop: bool = False


class ExtractionResult(BaseModel):
    """Guaranteed structured output from Gemini.

    This model represents the structured JSON response from Gemini
    when using response_mime_type: "application/json".
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    price: float = Field(..., ge=0, le=1_000_000, description="Numeric price value")
    currency: str = Field(default="EUR", pattern=r"^([A-Z]{3}|N/A)$")
    is_available: bool = Field(..., description="In stock status")
    product_name: str = Field(..., min_length=1, max_length=500)
    store_name: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=1000, description="AI notes/observations")
    is_blocked: bool = Field(default=False, description="Whether the page is blocked by a modal")
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
    price: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = Field(default=None, pattern=r"^[A-Z]{3}$")
    error_message: Optional[str] = Field(default=None, max_length=2000)
    duration_ms: Optional[int] = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
