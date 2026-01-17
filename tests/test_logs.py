
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)

def test_logs_page_renders():
    """
    GIVEN a running FastAPI application
    WHEN a GET request is made to /logs
    THEN the response status code should be 200
    AND the response should contain the text "Extraction Logs"
    """
    response = client.get("/logs")
    assert response.status_code == 200
    assert "Extraction Logs" in response.text
