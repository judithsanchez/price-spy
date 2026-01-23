
import pytest
import os
import tempfile
from pathlib import Path
from app.core import config
from app.storage.database import Database

@pytest.fixture(scope="function", autouse=True)
def isolate_database(monkeypatch):
    """
    Automatically isolate database for all tests.
    Creates a temporary database file and overrides settings.DATABASE_PATH
    and environment variable DATABASE_PATH.
    """
    # Create temp file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # Override settings
    monkeypatch.setattr(config.settings, "DATABASE_PATH", path)
    # Override env var (for subprocess tests like test_cli.py)
    monkeypatch.setenv("DATABASE_PATH", path)
    
    # Initialize schema
    db = Database(path)
    db.initialize()
    db.close()
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)
