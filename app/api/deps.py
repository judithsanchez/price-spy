from typing import Optional

from app.storage.database import Database

# Test database path override (used in tests)
_test_db_path: Optional[str] = None


def get_db() -> Database:
    """Get database connection."""
    global _test_db_path
    if _test_db_path:
        db = Database(_test_db_path)
    else:
        from app.core.config import settings

        db = Database(settings.DATABASE_PATH)

    db.initialize()
    return db
