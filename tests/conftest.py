import os
import pytest
from fastapi.testclient import TestClient
from app.api.main import app
from app.api import deps
import tempfile


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Create a temporary database for testing."""
    # Create a temporary file for the database
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_pricespy_")
    os.close(fd)

    # Save original
    original_test_path = deps._test_db_path

    # Override the database path in deps
    deps._test_db_path = path

    yield path

    # Restore
    deps._test_db_path = original_test_path

    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def client():
    """Get a FastAPI TestClient."""
    with TestClient(app) as c:
        yield c
