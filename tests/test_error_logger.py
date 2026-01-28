import pytest
from app.core.error_logger import log_error_to_db
from app.storage.database import Database
from app.storage.repositories import ErrorLogRepository

def test_log_error_to_db_integration(test_db, monkeypatch):
    from app.core.config import settings
    # Redirect error logger to test database
    monkeypatch.setattr(settings, "DATABASE_PATH", test_db)
    
    log_error_to_db(
        error_type="test_error",
        message="test failure message",
        url="http://test.com",
        include_stack=False
    )
    
    # Verify in DB
    db = Database(test_db)
    repo = ErrorLogRepository(db)
    errors = repo.get_recent(limit=1)
    
    assert len(errors) > 0
    latest = errors[0]
    assert latest.error_type == "test_error"
    assert latest.message == "test failure message"
    assert latest.url == "http://test.com"
