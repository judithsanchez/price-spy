"""Rate limit tracking and provider fallback for AI APIs."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import pytz

from app.core.gemini import GeminiModel, GeminiModels, ModelConfig
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Pacific timezone for RPD reset (Google resets at midnight PT)
PACIFIC_TZ = pytz.timezone("America/Los_Angeles")


@dataclass
class UsageRecord:
    """Record of API usage for a model."""

    model: str
    date: str  # YYYY-MM-DD in Pacific time
    request_count: int
    last_request_at: datetime
    is_exhausted: bool = False


class RateLimitTracker:
    """Track API usage and manage rate limits.

    Stores usage in SQLite and provides fallback logic when limits are hit.

    Usage:
        tracker = RateLimitTracker(db)

        # Before making a request
        model = tracker.get_available_model(GeminiModels.VISION_MODELS)
        if not model:
            raise Exception("All models exhausted")

        # After successful request
        tracker.record_usage(model)

        # After rate limit error
        tracker.mark_exhausted(model)
    """

    def __init__(self, db):
        """Initialize tracker with database connection."""
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        """Create usage tracking table if not exists."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                date TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                last_request_at TEXT,
                is_exhausted INTEGER DEFAULT 0,
                UNIQUE(model, date)
            )
        """)
        self.db.commit()

    @staticmethod
    def _get_pacific_date() -> str:
        """Get current date in Pacific timezone (for RPD reset)."""
        now_pacific = datetime.now(PACIFIC_TZ)
        return now_pacific.strftime("%Y-%m-%d")

    def get_usage(self, model: GeminiModel) -> Optional[UsageRecord]:
        """Get today's usage for a model."""
        today = self._get_pacific_date()
        cursor = self.db.execute(
            "SELECT model, date, request_count, last_request_at, is_exhausted "
            "FROM api_usage WHERE model = ? AND date = ?",
            (model.value, today),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return UsageRecord(
            model=row[0],
            date=row[1],
            request_count=row[2],
            last_request_at=datetime.fromisoformat(row[3])
            if row[3]
            else datetime.now(timezone.utc),
            is_exhausted=bool(row[4]),
        )

    def record_usage(self, config: ModelConfig):
        """Record a successful API request."""
        today = self._get_pacific_date()
        now = datetime.now(timezone.utc).isoformat()

        params: tuple = (config.model.value, today, now, now)
        self.db.execute(
            """
            INSERT INTO api_usage (
                model, date, request_count,
                last_request_at, is_exhausted
            )
            VALUES (?, ?, 1, ?, 0)
            ON CONFLICT(model, date) DO UPDATE SET
                request_count = request_count + 1,
                last_request_at = ?
            """,
            params,
        )
        self.db.commit()

        usage = self.get_usage(config.model)
        logger.info(
            "API usage recorded",
            extra={
                "model": config.model.value,
                "daily_count": usage.request_count if usage else 1,
                "daily_limit": config.rate_limits.rpd,
            },
        )

    def mark_exhausted(self, config: ModelConfig):
        """Mark a model as exhausted for today."""
        today = self._get_pacific_date()
        now = datetime.now(timezone.utc).isoformat()

        params: tuple = (config.model.value, today, now, now)
        self.db.execute(
            """
            INSERT INTO api_usage (model, date, request_count,
                last_request_at, is_exhausted)
            VALUES (?, ?, 0, ?, 1)
            ON CONFLICT(model, date) DO UPDATE SET
                is_exhausted = 1,
                last_request_at = ?
            """,
            params,
        )
        self.db.commit()

        logger.warning(
            "Model marked as exhausted",
            extra={"model": config.model.value, "date": today},
        )

    def is_available(self, config: ModelConfig) -> bool:
        """Check if a model is available (not exhausted and under limit)."""
        usage = self.get_usage(config.model)

        if not usage:
            return True  # No usage today

        if usage.is_exhausted:
            return False

        # Check if under daily limit (with 10% buffer)
        limit = int(config.rate_limits.rpd * 0.9)
        return usage.request_count < limit

    def get_available_model(self, models: List[ModelConfig]) -> Optional[ModelConfig]:
        """Get first available model from list (sorted by priority).

        Args:
            models: List of ModelConfig to try in order

        Returns:
            First available ModelConfig, or None if all exhausted
        """
        sorted_models = sorted(models, key=lambda m: m.priority)

        for config in sorted_models:
            if self.is_available(config):
                return config

        logger.error(
            "All models exhausted", extra={"models": [m.model.value for m in models]}
        )
        return None

    def get_status(self) -> dict:
        """Get usage status for all models (for UI display)."""
        today = self._get_pacific_date()
        cursor = self.db.execute(
            "SELECT model, request_count, is_exhausted FROM api_usage WHERE date = ?",
            (today,),
        )

        status = {}
        for row in cursor.fetchall():
            model_name = row[0]
            # Find the model config to get limits
            for model in GeminiModel:
                if model.value == model_name:
                    limits = GeminiModels.get_rate_limits(model)
                    status[model_name] = {
                        "used": row[1],
                        "limit": limits.rpd,
                        "exhausted": bool(row[2]),
                        "remaining": max(0, limits.rpd - row[1]),
                    }
                    break

        return status

    def reset_exhausted(self, model: GeminiModel):
        """Manually reset exhausted flag for a model (for testing)."""
        today = self._get_pacific_date()
        self.db.execute(
            "UPDATE api_usage SET is_exhausted = 0 WHERE model = ? AND date = ?",
            (model.value, today),
        )
        self.db.commit()
