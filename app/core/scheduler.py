"""Scheduler for automated price extraction."""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.email_report import send_daily_report
from app.core.extraction_queue import get_queue_summary, process_extraction_queue
from app.storage.database import Database
from app.storage.repositories import (
    SchedulerRunRepository,
    TrackedItemRepository,
)

# Global scheduler instance
# Global scheduler state
_state: Dict[str, Any] = {
    "scheduler": None,
    "last_run_result": {},
}


def get_scheduler_config() -> Dict[str, Any]:
    """Get scheduler configuration from environment."""
    return {
        "enabled": settings.SCHEDULER_ENABLED,
        "hour": settings.SCHEDULER_HOUR,
        "minute": settings.SCHEDULER_MINUTE,
        "max_concurrent": settings.MAX_CONCURRENT_EXTRACTIONS,
    }


async def run_scheduled_extraction() -> Dict[str, Any]:
    """Run the scheduled extraction job."""

    db = Database(settings.DATABASE_PATH)
    db.initialize()

    try:
        tracked_repo = TrackedItemRepository(db)
        scheduler_repo = SchedulerRunRepository(db)

        # Get items due for check (active and not checked today)
        items = tracked_repo.get_due_for_check()

        if not items:
            _state["last_run_result"] = {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
                "items_total": 0,
                "items_success": 0,
                "items_failed": 0,
                "message": "No items due for check (all already checked today)",
            }
            return _state["last_run_result"]

        # Start run log
        run_id = scheduler_repo.start_run(items_total=len(items))

        # Process queue
        results = await process_extraction_queue(items, db)
        summary = get_queue_summary(results)

        # Complete run log
        scheduler_repo.complete_run(
            run_id,
            items_success=summary["success_count"],
            items_failed=summary["error_count"],
        )

        # Send daily email report
        email_sent = False
        try:
            email_sent = send_daily_report(summary["results"], db)
        except Exception as e:
            print(f"Failed to send email report: {e}")

        _state["last_run_result"] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
            "items_total": summary["total"],
            "items_success": summary["success_count"],
            "items_failed": summary["error_count"],
            "email_sent": email_sent,
        }
        return _state["last_run_result"]

    except Exception as e:
        _state["last_run_result"] = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "error": str(e),
        }
        return _state["last_run_result"]
    finally:
        db.close()


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global scheduler instance."""
    return _state["scheduler"]


def get_scheduler_status() -> Dict[str, Any]:
    """Get current scheduler status."""

    config = get_scheduler_config()

    if _state["scheduler"] is None:
        return {
            "running": False,
            "enabled": config["enabled"],
            "next_run": None,
            "last_run": _state["last_run_result"],
            "items_count": 0,
            "config": config,
        }

    # Get next run time
    job = _state["scheduler"].get_job("daily_extraction")
    next_run = None
    is_paused = False
    if job:
        if job.next_run_time:
            next_run = job.next_run_time.isoformat()
        else:
            is_paused = True

    # Get items count
    items_count = 0
    try:
        db_path = os.getenv("DATABASE_PATH", "data/pricespy.db")
        db = Database(db_path)
        db.initialize()
        try:
            repo = TrackedItemRepository(db)
            items_count = len(repo.get_active())
        finally:
            db.close()
    except Exception:
        logging.getLogger(__name__).debug("Failed to get active items count")
        pass

    return {
        "running": _state["scheduler"].running,
        "enabled": config["enabled"],
        "paused": is_paused,
        "next_run": next_run,
        "last_run": _state["last_run_result"],
        "items_count": items_count,
        "config": config,
    }


def start_scheduler():
    """Start the scheduler."""
    config = get_scheduler_config()

    if not config["enabled"]:
        return None

    scheduler = AsyncIOScheduler()

    # Add daily extraction job
    scheduler.add_job(
        run_scheduled_extraction,
        CronTrigger(hour=config["hour"], minute=config["minute"]),
        id="daily_extraction",
        replace_existing=True,
        name="Daily Price Extraction",
    )

    scheduler.start()
    _state["scheduler"] = scheduler
    return scheduler


def stop_scheduler():
    """Stop the scheduler."""
    if _state["scheduler"] and _state["scheduler"].running:
        _state["scheduler"].shutdown()


def pause_scheduler():
    """Pause the daily extraction job."""
    if _state["scheduler"]:
        _state["scheduler"].pause_job("daily_extraction")


def resume_scheduler():
    """Resume the daily extraction job."""
    if _state["scheduler"]:
        _state["scheduler"].resume_job("daily_extraction")


async def trigger_run_now():
    """Trigger an immediate extraction run."""
    return await run_scheduled_extraction()


@asynccontextmanager
async def lifespan_scheduler(_app):
    """FastAPI lifespan context manager for scheduler."""
    start_scheduler()
    yield
    stop_scheduler()
