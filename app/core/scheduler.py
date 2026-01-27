"""Scheduler for automated price extraction."""

import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None
_last_run_result: Optional[Dict[str, Any]] = None


from app.core.config import settings

def get_scheduler_config() -> Dict[str, Any]:
    """Get scheduler configuration from environment."""
    return {
        "enabled": settings.SCHEDULER_ENABLED,
        "hour": settings.SCHEDULER_HOUR,
        "minute": settings.SCHEDULER_MINUTE,
        "max_concurrent": settings.MAX_CONCURRENT_EXTRACTIONS,
    }


async def run_scheduled_extraction():
    """Run the scheduled extraction job."""
    global _last_run_result

    from app.storage.database import Database
    from app.storage.repositories import TrackedItemRepository, SchedulerRunRepository
    from app.core.extraction_queue import process_extraction_queue, get_queue_summary

    db = Database(settings.DATABASE_PATH)
    db.initialize()

    try:
        tracked_repo = TrackedItemRepository(db)
        scheduler_repo = SchedulerRunRepository(db)

        # Get items due for check (active and not checked today)
        items = tracked_repo.get_due_for_check()

        if not items:
            _last_run_result = {
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "status": "completed",
                "items_total": 0,
                "items_success": 0,
                "items_failed": 0,
                "message": "No items due for check (all already checked today)"
            }
            return _last_run_result

        # Start run log
        run_id = scheduler_repo.start_run(items_total=len(items))

        # Process queue
        results = await process_extraction_queue(items, db)
        summary = get_queue_summary(results)

        # Complete run log
        scheduler_repo.complete_run(
            run_id,
            items_success=summary["success_count"],
            items_failed=summary["error_count"]
        )

        # Send daily email report
        email_sent = False
        try:
            from app.core.email_report import send_daily_report
            email_sent = send_daily_report(summary["results"], db)
        except Exception as e:
            print(f"Failed to send email report: {e}")

        _last_run_result = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
            "items_total": summary["total"],
            "items_success": summary["success_count"],
            "items_failed": summary["error_count"],
            "email_sent": email_sent,
        }

        return _last_run_result

    except Exception as e:
        _last_run_result = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": "failed",
            "error": str(e)
        }
        return _last_run_result

    finally:
        db.close()


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global scheduler instance."""
    return _scheduler


def get_scheduler_status() -> Dict[str, Any]:
    """Get current scheduler status."""
    global _scheduler, _last_run_result

    config = get_scheduler_config()

    if _scheduler is None:
        return {
            "running": False,
            "enabled": config["enabled"],
            "next_run": None,
            "last_run": _last_run_result,
            "items_count": 0,
            "config": config
        }

    # Get next run time
    job = _scheduler.get_job("daily_extraction")
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
        from app.storage.database import Database
        from app.storage.repositories import TrackedItemRepository

        db_path = os.getenv("DATABASE_PATH", "data/pricespy.db")
        db = Database(db_path)
        db.initialize()
        try:
            repo = TrackedItemRepository(db)
            items_count = len(repo.get_active())
        finally:
            db.close()
    except Exception:
        pass

    return {
        "running": _scheduler.running,
        "enabled": config["enabled"],
        "paused": is_paused,
        "next_run": next_run,
        "last_run": _last_run_result,
        "items_count": items_count,
        "config": config
    }


def start_scheduler():
    """Start the scheduler."""
    global _scheduler

    config = get_scheduler_config()

    if not config["enabled"]:
        return

    _scheduler = AsyncIOScheduler()

    # Add daily extraction job
    _scheduler.add_job(
        run_scheduled_extraction,
        CronTrigger(hour=config["hour"], minute=config["minute"]),
        id="daily_extraction",
        replace_existing=True,
        name="Daily Price Extraction"
    )

    _scheduler.start()


def stop_scheduler():
    """Stop the scheduler."""
    global _scheduler

    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        _scheduler = None


def pause_scheduler():
    """Pause the daily extraction job."""
    global _scheduler
    if _scheduler:
        _scheduler.pause_job("daily_extraction")


def resume_scheduler():
    """Resume the daily extraction job."""
    global _scheduler
    if _scheduler:
        _scheduler.resume_job("daily_extraction")


async def trigger_run_now():
    """Trigger an immediate extraction run."""
    return await run_scheduled_extraction()


@asynccontextmanager
async def lifespan_scheduler(app):
    """FastAPI lifespan context manager for scheduler."""
    start_scheduler()
    yield
    stop_scheduler()
