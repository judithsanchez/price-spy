"""Pydantic models for Price Spy data validation."""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProductInfo(BaseModel):
    """Validated product information extracted from Gemini."""

    model_config = ConfigDict(str_strip_whitespace=True)

    product_name: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., gt=0, le=1_000_000)
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    store_name: Optional[str] = Field(default=None, max_length=100)
    page_type: Literal["single_product", "search_results"]
    confidence: float = Field(..., ge=0.0, le=1.0, alias="confidence_score")

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
    confidence: float
    url: str
    store_name: Optional[str] = None
    page_type: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
