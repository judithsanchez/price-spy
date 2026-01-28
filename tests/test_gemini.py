from app.core.gemini import GeminiModel, GeminiModels


def test_gemini_models_retrieval():
    config = GeminiModels.get_config_by_model(GeminiModel.FLASH_1_5.value)
    assert config is not None
    assert config.model == GeminiModel.FLASH_1_5
    # Flash 1.5 should have rpd of 1500
    assert config.rate_limits.rpd == 1500  # noqa: PLR2004


def test_vision_models_list():
    vision_models = GeminiModels.VISION_MODELS
    assert len(vision_models) > 0
    # All vision models should have supports_vision=True
    for model_config in vision_models:
        assert model_config.supports_vision is True


def test_api_url_build():
    config = GeminiModels.VISION_EXTRACTION
    url = GeminiModels.get_api_url(config, "dummy_key")
    assert "dummy_key" in url
    assert config.model.value in url
