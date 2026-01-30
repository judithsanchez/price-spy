from app.core.gemini import GeminiModel, GeminiModels
from app.core.rate_limiter import RateLimitTracker
from app.storage.database import Database


def test_rate_limiter_available_logic(test_db):
    db = Database(test_db)
    tracker = RateLimitTracker(db)

    config = GeminiModels.VISION_EXTRACTION

    # Initially available
    assert tracker.is_available(config) is True

    # Mark exhausted
    tracker.mark_exhausted(config)
    assert tracker.is_available(config) is False

    # Reset
    tracker.reset_exhausted(config.model)
    assert tracker.is_available(config) is True


def test_get_available_model_logic(test_db):
    db = Database(test_db)
    tracker = RateLimitTracker(db)

    # Mocking a scenario where first model is exhausted
    models = GeminiModels.VISION_MODELS  # [VISION_FALLBACK, VISION_EXTRACTION]

    # Fallback (priority 0) should be returned first
    selected = tracker.get_available_model(models)
    assert selected is not None
    assert selected.model == GeminiModel.FLASH_2_5_LITE

    # Mark fallback exhausted
    tracker.mark_exhausted(selected)

    # Now extraction (priority 1) should be returned
    new_selected = tracker.get_available_model(models)
    assert new_selected is not None
    assert new_selected.model == GeminiModel.FLASH_2_5
