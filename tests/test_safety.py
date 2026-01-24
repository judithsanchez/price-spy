import pytest
from app.storage.database import Database

def test_production_db_safety():
    """Verify that connecting to production DB during tests raises RuntimeError."""
    db = Database("data/pricespy.db")
    with pytest.raises(RuntimeError) as excinfo:
        db._connect()
    assert "SAFETY BLOCK" in str(excinfo.value)
