import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import deps
from app.api.main import app


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Create a temporary database for testing."""
    # Create a temporary file for the database
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_pricespy_")
    os.close(fd)

    # Save original
    # Save original (assumed None/default for tests)
    # We rely on set_test_db_path to restore it to None
    pass

    # Override the database path in deps
    deps.set_test_db_path(path)

    yield path

    # Restore
    deps.set_test_db_path(None)

    # Cleanup
    # Cleanup
    if Path(path).exists():
        Path(path).unlink()


@pytest.fixture
def client():
    """Get a FastAPI TestClient."""
    with TestClient(app) as c:
        yield c
