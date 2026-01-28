import os

from app.api import deps


def test_get_db_test_path(test_db):
    # This should already be set by conftest
    assert deps._test_db_path == test_db
    db = deps.get_db()
    assert db.db_path == test_db
    assert os.path.exists(test_db)
