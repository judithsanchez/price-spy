import json
import logging
import io
from app.utils.logging import get_logger, JSONFormatter

def test_json_formatter_basic():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["message"] == "test message"
    assert data["level"] == "INFO"
    assert data["logger"] == "test_logger"
    assert "timestamp" in data

def test_json_formatter_extra_fields():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=".", lineno=1,
        msg="msg", args=(), exc_info=None
    )
    record.custom_field = "custom_value"
    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["custom_field"] == "custom_value"

def test_get_logger_integration():
    stream = io.StringIO()
    logger = get_logger("test_integration", stream=stream)
    logger.info("integration test")
    
    output = stream.getvalue()
    data = json.loads(output)
    assert data["message"] == "integration test"
    assert data["logger"] == "test_integration"
