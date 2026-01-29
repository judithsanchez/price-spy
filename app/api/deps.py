from app.core.config import settings
from app.storage.database import Database

# Test database path override (used in tests)
_test_db_path: str | None = None


def get_db() -> Database:
    """Get database connection."""
    db = Database(_test_db_path) if _test_db_path else Database(settings.DATABASE_PATH)

    db.initialize()
    return db


def set_test_db_path(path: str | None) -> None:
    """Set the database path for testing overrides."""
    global _test_db_path  # noqa: PLW0603
    _test_db_path = path
