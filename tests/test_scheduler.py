"""Tests for the scheduler."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import tempfile
import os


class TestSchedulerConfig:
    """Tests for scheduler configuration."""

    def test_scheduler_default_config(self):
        """Scheduler should have sensible defaults."""
        from app.core.scheduler import get_scheduler_config

        config = get_scheduler_config()

        assert config["enabled"] is True
        assert config["hour"] == 8
        assert config["minute"] == 0
        assert config["max_concurrent"] == 10

    def test_scheduler_config_from_env(self):
        """Scheduler should read config from environment."""
        from app.core.scheduler import get_scheduler_config

        with patch.dict(os.environ, {
            "SCHEDULER_ENABLED": "false",
            "SCHEDULER_HOUR": "14",
            "SCHEDULER_MINUTE": "30",
            "MAX_CONCURRENT_EXTRACTIONS": "5"
        }):
            config = get_scheduler_config()

        assert config["enabled"] is False
        assert config["hour"] == 14
        assert config["minute"] == 30
        assert config["max_concurrent"] == 5


class TestSchedulerStatus:
    """Tests for scheduler status endpoint."""

    def test_scheduler_status_returns_200(self, client_with_scheduler):
        """GET /api/scheduler/status should return 200."""
        response = client_with_scheduler.get("/api/scheduler/status")
        assert response.status_code == 200

    def test_scheduler_status_includes_state(self, client_with_scheduler):
        """Status should include running state."""
        response = client_with_scheduler.get("/api/scheduler/status")
        data = response.json()

        assert "running" in data
        assert "next_run" in data
        assert "last_run" in data
        assert "items_count" in data

    def test_scheduler_run_now_triggers_extraction(self, client_with_scheduler):
        """POST /api/scheduler/run-now should trigger extraction."""
        with patch('app.core.scheduler.run_scheduled_extraction', new_callable=AsyncMock) as mock_run:
            response = client_with_scheduler.post("/api/scheduler/run-now")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"


class TestSchedulerRuns:
    """Tests for scheduler run logging."""

    def test_scheduler_run_logged_to_db(self, db_with_scheduler):
        """Scheduler runs should be logged to database."""
        from app.storage.repositories import SchedulerRunRepository

        repo = SchedulerRunRepository(db_with_scheduler)

        # Create a run
        run_id = repo.start_run(items_total=5)
        assert run_id is not None

        # Complete the run
        repo.complete_run(run_id, items_success=4, items_failed=1)

        # Verify
        run = repo.get_by_id(run_id)
        assert run is not None
        assert run["status"] == "completed"
        assert run["items_total"] == 5
        assert run["items_success"] == 4
        assert run["items_failed"] == 1

    def test_scheduler_get_last_run(self, db_with_scheduler):
        """Should be able to get the last scheduler run."""
        from app.storage.repositories import SchedulerRunRepository

        repo = SchedulerRunRepository(db_with_scheduler)

        # Create a run
        run_id = repo.start_run(items_total=3)
        repo.complete_run(run_id, items_success=3, items_failed=0)

        # Get last run
        last_run = repo.get_last_run()
        assert last_run is not None
        assert last_run["id"] == run_id


@pytest.fixture
def client_with_scheduler():
    """Create test client with scheduler initialized."""
    from app.api.main import app
    import app.api.main as main_module
    from app.storage.database import Database

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        db.initialize()
        db.close()

        original_db_path = main_module._test_db_path
        main_module._test_db_path = db_path

        yield TestClient(app)

        main_module._test_db_path = original_db_path

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def db_with_scheduler():
    """Create database with scheduler tables."""
    from app.storage.database import Database

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.initialize()

    yield db

    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)
