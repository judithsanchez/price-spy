from app.core.config import settings
from app.storage.database import Database


class DatabaseConfig:
    """Database configuration manager."""

    _test_db_path: str | None = None

    @classmethod
    def get_path(cls) -> str:
        """Get the current database path."""
        return cls._test_db_path or settings.DATABASE_PATH

    @classmethod
    def set_test_path(cls, path: str | None) -> None:
        """Set a test database path override."""
        cls._test_db_path = path


def get_db() -> Database:
    """Get database connection."""
    db = Database(DatabaseConfig.get_path())
    db.initialize()
    return db


def set_test_db_path(path: str | None) -> None:
    """Set the database path for testing overrides."""
    DatabaseConfig.set_test_path(path)
