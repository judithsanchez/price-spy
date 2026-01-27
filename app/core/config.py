from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration management for Price Spy.
    Loads values from environment variables and .env file.
    """

    # Core
    GEMINI_API_KEY: str
    DATABASE_PATH: str = "data/pricespy.db"

    # Scheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_HOUR: int = 8
    SCHEDULER_MINUTE: int = 0
    MAX_CONCURRENT_EXTRACTIONS: int = 10

    # Batch Processing
    BATCH_DELAY_SECONDS: float = 2.0

    # Email Reporting
    EMAIL_ENABLED: bool = False
    EMAIL_RECIPIENT: Optional[str] = None
    EMAIL_SENDER: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    EMAIL_DASHBOARD_URL: str = "http://localhost:8000"

    # Browser
    HEADLESS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


try:
    settings = Settings()
except Exception as e:
    # Fail fast if critical config is missing (like API Key)
    print(f"Configuration Error: {e}")
    # We might not want to exit here if we want to handle it gracefully in the app,
    # but for now, we'll let it be exposed.
    # Re-raising might be better but let's just make sure 'settings' exists
    raise
