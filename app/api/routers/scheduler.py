from typing import Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.core.scheduler import (
    get_scheduler_status,
    trigger_run_now,
    pause_scheduler,
    resume_scheduler,
)

router = APIRouter(
    prefix="/api/scheduler",
    tags=["Scheduler"]
)

class SchedulerStatusResponse(BaseModel):
    """Response model for scheduler status."""
    running: bool
    enabled: bool
    paused: bool
    next_run: Optional[str] = None
    last_run: Optional[dict] = None
    items_count: int
    config: dict

class SchedulerRunResponse(BaseModel):
    """Response model for scheduler run trigger."""
    status: str
    message: Optional[str] = None

@router.get("/status", response_model=SchedulerStatusResponse)
async def scheduler_status():
    """Get current scheduler status."""
    status = get_scheduler_status()
    return SchedulerStatusResponse(**status)

@router.post("/run-now", response_model=SchedulerRunResponse)
async def scheduler_run_now(background_tasks: BackgroundTasks):
    """Trigger an immediate extraction run."""
    background_tasks.add_task(trigger_run_now)
    return SchedulerRunResponse(
        status="started",
        message="Extraction run started in background"
    )

@router.post("/pause", response_model=SchedulerRunResponse)
async def scheduler_pause():
    """Pause the scheduler."""
    pause_scheduler()
    return SchedulerRunResponse(
        status="paused",
        message="Scheduler paused"
    )

@router.post("/resume", response_model=SchedulerRunResponse)
async def scheduler_resume():
    """Resume the scheduler."""
    resume_scheduler()
    return SchedulerRunResponse(
        status="resumed",
        message="Scheduler resumed"
    )
