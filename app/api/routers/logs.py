from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.api.deps import get_db
from app.core.gemini import GeminiModels
from app.core.rate_limiter import RateLimitTracker
from app.storage.database import Database
from app.storage.repositories import ErrorLogRepository, ExtractionLogRepository

router = APIRouter(prefix="/api", tags=["Logs"])


class ExtractionLogResponse(BaseModel):
    """Response model for extraction log."""

    id: int
    tracked_item_id: int
    status: str
    model_used: str | None = None
    price: float | None = None
    currency: str | None = None
    error_message: str | None = None
    duration_ms: int | None = None
    created_at: str


class ErrorLogResponse(BaseModel):
    """Response model for error log."""

    id: int
    error_type: str
    message: str
    url: str | None = None
    screenshot_path: str | None = None
    stack_trace: str | None = None
    created_at: str


class ExtractionStatsResponse(BaseModel):
    """Response model for extraction statistics."""

    total_today: int
    success_count: int
    error_count: int
    avg_duration_ms: int


class ApiUsageResponse(BaseModel):
    """Response model for API usage per model."""

    model: str
    used: int
    limit: int
    remaining: int
    exhausted: bool


class ExtractionLogFilters(BaseModel):
    """Filters for extraction logs."""

    status: str | None = None
    item_id: int | None = None
    start_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    limit: int = Query(100, ge=1, le=1000)
    offset: int = Query(0, ge=0)


@router.get("/logs", response_model=list[ExtractionLogResponse])
async def get_extraction_logs(
    filters: Annotated[ExtractionLogFilters, Query()],
    db: Annotated[Database, Depends(get_db)],
):
    """Get recent extraction logs with optional filters."""
    try:
        repo = ExtractionLogRepository(db)
        logs = repo.get_all_filtered(
            filters=filters.model_dump(),
            limit=filters.limit,
            offset=filters.offset,
        )
        return [
            ExtractionLogResponse(
                id=int(log.id or 0),
                tracked_item_id=log.tracked_item_id,
                status=log.status,
                model_used=log.model_used,
                price=log.price,
                currency=log.currency,
                error_message=log.error_message,
                duration_ms=log.duration_ms,
                created_at=log.created_at.isoformat(),
            )
            for log in logs
        ]
    finally:
        db.close()


class ErrorLogFilters(BaseModel):
    """Filters for error logs."""

    error_type: str | None = None
    start_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    end_date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    limit: int = Query(100, ge=1, le=1000)
    offset: int = Query(0, ge=0)


@router.get("/errors", response_model=list[ErrorLogResponse])
async def get_error_logs(
    filters: Annotated[ErrorLogFilters, Query()],
    db: Annotated[Database, Depends(get_db)],
):
    """Get recent error logs with optional filters."""
    try:
        repo = ErrorLogRepository(db)
        logs = repo.get_all_filtered(
            filters=filters.model_dump(),
            limit=filters.limit,
            offset=filters.offset,
        )
        return [
            ErrorLogResponse(
                id=int(log.id or 0),
                error_type=log.error_type,
                message=log.message,
                url=log.url,
                screenshot_path=log.screenshot_path,
                stack_trace=log.stack_trace,
                created_at=log.created_at.isoformat(),
            )
            for log in logs
        ]
    finally:
        db.close()


@router.get("/logs/stats", response_model=ExtractionStatsResponse)
async def get_extraction_stats(
    db: Annotated[Database, Depends(get_db)],
):
    """Get extraction statistics for today."""
    try:
        repo = ExtractionLogRepository(db)
        stats = repo.get_stats()
        return ExtractionStatsResponse(**stats)
    finally:
        db.close()


@router.get("/usage", response_model=list[ApiUsageResponse])
async def get_api_usage(
    db: Annotated[Database, Depends(get_db)],
):
    """Get API usage for all models today."""
    try:
        tracker = RateLimitTracker(db)
        status = tracker.get_status()

        # Include all vision models even if not used today
        result = []
        for config in GeminiModels.VISION_MODELS:
            model_name = config.model.value
            if model_name in status:
                result.append(ApiUsageResponse(model=model_name, **status[model_name]))
            else:
                result.append(
                    ApiUsageResponse(
                        model=model_name,
                        used=0,
                        limit=config.rate_limits.rpd,
                        remaining=config.rate_limits.rpd,
                        exhausted=False,
                    )
                )
        return result
    finally:
        db.close()
