"""Gemini API configuration and model definitions."""

from enum import Enum
from dataclasses import dataclass


class GeminiModel(str, Enum):
    """Available Gemini models.

    See: https://ai.google.dev/gemini-api/docs/models
    """
    # Full models
    FLASH_2_5 = "gemini-2.5-flash"           # Best for complex tasks, vision
    PRO_2_5 = "gemini-2.5-pro"               # Highest capability

    # Lite models (faster, lower cost)
    FLASH_2_5_LITE = "gemini-2.5-flash-lite" # Faster, cheaper, still has vision

    # Legacy
    FLASH_2_0 = "gemini-2.0-flash"
    FLASH_1_5 = "gemini-1.5-flash"


@dataclass
class ModelConfig:
    """Configuration for a specific use case."""
    model: GeminiModel
    description: str
    supports_vision: bool = True
    supports_structured_output: bool = True


class GeminiModels:
    """Centralized Gemini model configuration for Price Spy.

    Usage:
        from app.core.gemini import GeminiModels

        model = GeminiModels.VISION_EXTRACTION
        url = GeminiModels.get_api_url(model, api_key)
    """

    # Model assignments for different tasks
    VISION_EXTRACTION = ModelConfig(
        model=GeminiModel.FLASH_2_5,
        description="Screenshot price extraction with structured output",
        supports_vision=True,
        supports_structured_output=True,
    )

    API_TEST = ModelConfig(
        model=GeminiModel.FLASH_2_5_LITE,
        description="Quick API key validation (no vision needed)",
        supports_vision=False,
        supports_structured_output=True,
    )

    TEXT_ONLY = ModelConfig(
        model=GeminiModel.FLASH_2_5_LITE,
        description="Text-only tasks (cheaper/faster)",
        supports_vision=False,
        supports_structured_output=True,
    )

    # API Base URL
    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    @classmethod
    def get_api_url(cls, config: ModelConfig, api_key: str) -> str:
        """Build the API URL for a model config.

        Args:
            config: ModelConfig instance
            api_key: Gemini API key

        Returns:
            Full API URL for generateContent endpoint
        """
        return f"{cls.API_BASE}/{config.model.value}:generateContent?key={api_key}"

    @classmethod
    def get_model_url(cls, model: GeminiModel, api_key: str) -> str:
        """Build the API URL for a specific model.

        Args:
            model: GeminiModel enum value
            api_key: Gemini API key

        Returns:
            Full API URL for generateContent endpoint
        """
        return f"{cls.API_BASE}/{model.value}:generateContent?key={api_key}"
