"""Tests for Gemini model configuration."""

import pytest
from app.core.gemini import GeminiModel, GeminiModels, ModelConfig


class TestGeminiConfig:
    """Tests for GeminiModels configuration."""

    def test_model_enum_values(self):
        """Model enum should have correct string values."""
        assert GeminiModel.FLASH_2_5.value == "gemini-2.5-flash"
        assert GeminiModel.FLASH_2_5_LITE.value == "gemini-2.5-flash-lite"

    def test_vision_extraction_uses_flash(self):
        """Vision extraction should use full flash model."""
        config = GeminiModels.VISION_EXTRACTION
        assert config.model == GeminiModel.FLASH_2_5
        assert config.supports_vision is True

    def test_api_test_uses_lite(self):
        """API testing should use lite model."""
        config = GeminiModels.API_TEST
        assert config.model == GeminiModel.FLASH_2_5_LITE

    def test_get_api_url_format(self):
        """API URL should be correctly formatted."""
        url = GeminiModels.get_api_url(GeminiModels.VISION_EXTRACTION, "test-key")
        assert "gemini-2.5-flash:generateContent" in url
        assert "key=test-key" in url

    def test_get_model_url_format(self):
        """Model URL should be correctly formatted."""
        url = GeminiModels.get_model_url(GeminiModel.FLASH_2_5_LITE, "my-key")
        assert "gemini-2.5-flash-lite:generateContent" in url
        assert "key=my-key" in url

    def test_all_configs_have_models(self):
        """All model configs should have valid models."""
        configs = [
            GeminiModels.VISION_EXTRACTION,
            GeminiModels.API_TEST,
            GeminiModels.TEXT_ONLY,
        ]
        for config in configs:
            assert isinstance(config, ModelConfig)
            assert isinstance(config.model, GeminiModel)
            assert config.description
