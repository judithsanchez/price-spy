
from fastapi.testclient import TestClient
from app.api.main import app, get_db
from app.models.schemas import ExtractionLog
from app.storage.repositories import ExtractionLogRepository
import pytest
from datetime import datetime, timedelta

client = TestClient(app)

@pytest.fixture
def test_db():
    db = get_db()
    db.initialize()
    yield db
    db.close()


def test_get_extraction_logs(test_db):
    """
    GIVEN a database with extraction logs
    WHEN a GET request is made to /api/logs
    THEN the response should contain a list of logs
    """
    # Arrange
    repo = ExtractionLogRepository(test_db)
    repo.insert(ExtractionLog(tracked_item_id=1, status="success", model_used="flash", price=10.0, currency="USD", duration_ms=100))
    repo.insert(ExtractionLog(tracked_item_id=2, status="error", error_message="Test error", duration_ms=200))

    # Act
    response = client.get("/api/logs")

    # Assert
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 2
    assert logs[0]["tracked_item_id"] == 2 # Most recent first
    assert logs[1]["tracked_item_id"] == 1


def test_get_extraction_logs_with_limit(test_db):
    """
    GIVEN a database with multiple extraction logs
    WHEN a GET request is made to /api/logs with a limit
    THEN the response should contain the limited number of logs
    """
    # Arrange
    repo = ExtractionLogRepository(test_db)
    for i in range(5):
        repo.insert(ExtractionLog(tracked_item_id=i, status="success"))

    # Act
    response = client.get("/api/logs?limit=3")

    # Assert
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3


def test_get_extraction_logs_with_status_filter(test_db):
    """
    GIVEN a database with success and error logs
    WHEN a GET request is made to /api/logs with a status filter
    THEN the response should only contain logs with that status
    """
    # Arrange
    repo = ExtractionLogRepository(test_db)
    repo.insert(ExtractionLog(tracked_item_id=1, status="success"))
    repo.insert(ExtractionLog(tracked_item_id=2, status="error"))
    repo.insert(ExtractionLog(tracked_item_id=3, status="success"))

    # Act
    response = client.get("/api/logs?status=error")

    # Assert
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["status"] == "error"
    assert logs[0]["tracked_item_id"] == 2

def test_get_extraction_logs_with_item_id_filter(test_db):
    """
    GIVEN a database with logs for multiple items
    WHEN a GET request is made to /api/logs with an item_id filter
    THEN the response should only contain logs for that item
    """
    # Arrange
    repo = ExtractionLogRepository(test_db)
    repo.insert(ExtractionLog(tracked_item_id=1, status="success"))
    repo.insert(ExtractionLog(tracked_item_id=2, status="error"))
    repo.insert(ExtractionLog(tracked_item_id=1, status="success"))

    # Act
    response = client.get("/api/logs?item_id=1")

    # Assert
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 2
    assert all(log["tracked_item_id"] == 1 for log in logs)

def test_get_extraction_logs_with_date_filters(test_db):
    """
    GIVEN a database with logs from different dates
    WHEN a GET request is made to /api/logs with date filters
    THEN the response should only contain logs within that date range
    """
    # Arrange
    repo = ExtractionLogRepository(test_db)
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)

    # This is a bit of a hack to manually set the created_at timestamp
    # In a real scenario, the DB would handle this.
    conn = test_db.get_connection()
    conn.execute(
        "INSERT INTO extraction_logs (tracked_item_id, status, created_at) VALUES (?, ?, ?)",
        (1, "success", yesterday.isoformat())
    )
    conn.execute(
        "INSERT INTO extraction_logs (tracked_item_id, status, created_at) VALUES (?, ?, ?)",
        (2, "success", today.isoformat())
    )
    conn.commit()
    conn.close()


    # Act
    start_date = (today - timedelta(hours=1)).strftime('%Y-%m-%d')
    end_date = (today + timedelta(hours=1)).strftime('%Y-%m-%d')
    response = client.get(f"/api/logs?start_date={start_date}&end_date={end_date}")

    # Assert
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["tracked_item_id"] == 2
