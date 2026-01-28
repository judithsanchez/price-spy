from app.core.config import settings
from app.storage.database import Database

# Test database path override (used in tests)
_test_db_path: str | None = None


def get_db() -> Database:
    """Get database connection."""
    if _test_db_path:
        db = Database(_test_db_path)
    else:
        db = Database(settings.DATABASE_PATH)

    db.initialize()
    return db
