from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_db
from app.core.rate_limiter import RateLimitTracker
from app.core.gemini import GeminiModels
from app.storage.repositories import ExtractionLogRepository, ErrorLogRepository

router = APIRouter(prefix="/api", tags=["Logs"])


class ExtractionLogResponse(BaseModel):
    """Response model for extraction log."""

    id: int
    tracked_item_id: int
    status: str
    model_used: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: str


class ErrorLogResponse(BaseModel):
    """Response model for error log."""

    id: int
    error_type: str
    message: str
    url: Optional[str] = None
    screenshot_path: Optional[str] = None
    stack_trace: Optional[str] = None
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


@router.get("/logs", response_model=List[ExtractionLogResponse])
async def get_extraction_logs(
    status: Optional[str] = None,
    item_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db=Depends(get_db),
):
    """Get recent extraction logs with optional filters."""
    try:
        repo = ExtractionLogRepository(db)
        logs = repo.get_all_filtered(
            status=status,
            item_id=item_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
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


@router.get("/errors", response_model=List[ErrorLogResponse])
async def get_error_logs(
    error_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db=Depends(get_db),
):
    """Get recent error logs with optional filters."""
    try:
        repo = ErrorLogRepository(db)
        logs = repo.get_all_filtered(
            error_type=error_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
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
async def get_extraction_stats(db=Depends(get_db)):
    """Get extraction statistics for today."""
    try:
        repo = ExtractionLogRepository(db)
        stats = repo.get_stats()
        return ExtractionStatsResponse(**stats)
    finally:
        db.close()


@router.get("/usage", response_model=List[ApiUsageResponse])
async def get_api_usage(db=Depends(get_db)):
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
