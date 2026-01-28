from app.core.config import Settings


def test_settings_explicit_values():
    # Pass values directly to bypass .env for this test
    settings = Settings(
        DATABASE_PATH="test_explicit.db",
        MAX_CONCURRENT_EXTRACTIONS=7,
        GEMINI_API_KEY="test_key",
    )
    assert settings.DATABASE_PATH == "test_explicit.db"
    assert settings.MAX_CONCURRENT_EXTRACTIONS == 7  # noqa: PLR2004
    assert settings.GEMINI_API_KEY == "test_key"


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", "test_env.db")
    monkeypatch.setenv("MAX_CONCURRENT_EXTRACTIONS", "5")
    # We must ensure .env doesn't interfere if it exists
    # But Settings() usually prioritizes env vars over .env
    settings = Settings()
    assert settings.DATABASE_PATH == "test_env.db"
    assert settings.MAX_CONCURRENT_EXTRACTIONS == 5  # noqa: PLR2004
