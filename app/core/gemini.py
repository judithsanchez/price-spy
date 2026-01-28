"""Gemini API configuration, rate limits, and provider management."""

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class GeminiModel(str, Enum):
    """Available Gemini models.

    See: https://ai.google.dev/gemini-api/docs/models
    """

    # Full models
    FLASH_2_5 = "gemini-2.5-flash"
    PRO_2_5 = "gemini-2.5-pro"

    # Lite models (faster, lower cost, higher limits)
    FLASH_2_5_LITE = "gemini-2.5-flash-lite"

    # Legacy
    FLASH_2_0 = "gemini-2.0-flash"
    FLASH_1_5 = "gemini-1.5-flash"


@dataclass
class RateLimits:
    """Rate limits for a model (Free Tier).

    See: https://ai.google.dev/gemini-api/docs/rate-limits
    RPD resets at midnight Pacific time.
    """

    rpm: int  # Requests per minute
    tpm: int  # Tokens per minute
    rpd: int  # Requests per day


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    model: GeminiModel
    description: str
    rate_limits: RateLimits
    supports_vision: bool = True
    supports_structured_output: bool = True
    priority: int = 0  # Lower = try first


# Paid Tier 1 rate limits
# Source: https://ai.google.dev/gemini-api/docs/rate-limits
RATE_LIMITS = {
    GeminiModel.PRO_2_5: RateLimits(rpm=5, tpm=250_000, rpd=100),
    GeminiModel.FLASH_2_5: RateLimits(rpm=1000, tpm=1_000_000, rpd=10000),
    GeminiModel.FLASH_2_5_LITE: RateLimits(rpm=4000, tpm=4_000_000, rpd=1000000),
    GeminiModel.FLASH_2_0: RateLimits(rpm=10, tpm=250_000, rpd=500),
    GeminiModel.FLASH_1_5: RateLimits(rpm=15, tpm=1_000_000, rpd=1500),
}


class GeminiModels:
    """Centralized Gemini model configuration for Price Spy.

    Usage:
        from app.core.gemini import GeminiModels

        config = GeminiModels.VISION_EXTRACTION
        url = GeminiModels.get_api_url(config, api_key)
        print(f"Daily limit: {config.rate_limits.rpd}")
    """

    # Primary model for vision tasks (best quality)
    VISION_EXTRACTION = ModelConfig(
        model=GeminiModel.FLASH_2_5,
        description="Screenshot price extraction (backup high-quality)",
        rate_limits=RATE_LIMITS[GeminiModel.FLASH_2_5],
        supports_vision=True,
        supports_structured_output=True,
        priority=1,
    )

    # Fallback for vision tasks (4x more daily requests)
    VISION_FALLBACK = ModelConfig(
        model=GeminiModel.FLASH_2_5_LITE,
        description="Screenshot extraction (default - cheaper/faster)",
        rate_limits=RATE_LIMITS[GeminiModel.FLASH_2_5_LITE],
        supports_vision=True,
        supports_structured_output=True,
        priority=0,
    )

    # For API testing (cheapest option)
    API_TEST = ModelConfig(
        model=GeminiModel.FLASH_2_5_LITE,
        description="Quick API key validation",
        rate_limits=RATE_LIMITS[GeminiModel.FLASH_2_5_LITE],
        supports_vision=False,
        supports_structured_output=True,
        priority=0,
    )

    # Text-only tasks
    TEXT_ONLY = ModelConfig(
        model=GeminiModel.FLASH_2_5_LITE,
        description="Text-only tasks (cheaper/faster)",
        rate_limits=RATE_LIMITS[GeminiModel.FLASH_2_5_LITE],
        supports_vision=False,
        supports_structured_output=True,
        priority=0,
    )

    # API Base URL
    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    # Vision-capable models in priority order (for fallback)
    # Default is now Lite model as requested
    VISION_MODELS: ClassVar[list[ModelConfig]] = [VISION_FALLBACK, VISION_EXTRACTION]

    @classmethod
    def get_config_by_model(cls, model_name: str) -> ModelConfig | None:
        """Get ModelConfig by model name string (e.g., 'gemini-2.5-flash')."""
        try:
            model = GeminiModel(model_name)
            # Check existing predefined configs
            configs = [
                cls.VISION_EXTRACTION,
                cls.VISION_FALLBACK,
                cls.TEXT_ONLY,
                cls.API_TEST,
            ]
            for config in configs:
                if config.model == model:
                    return config

            # Generic config for valid model
            if model in RATE_LIMITS:
                return ModelConfig(
                    model=model,
                    description=f"Generic config for {model_name}",
                    rate_limits=RATE_LIMITS[model],
                )
        except ValueError:
            pass
        return None

    @classmethod
    def get_api_url(cls, config: ModelConfig, api_key: str) -> str:
        """Build the API URL for a model config."""
        return f"{cls.API_BASE}/{config.model.value}:generateContent?key={api_key}"

    @classmethod
    def get_model_url(cls, model: GeminiModel, api_key: str) -> str:
        """Build the API URL for a specific model."""
        return f"{cls.API_BASE}/{model.value}:generateContent?key={api_key}"

    @classmethod
    def get_rate_limits(cls, model: GeminiModel) -> RateLimits:
        """Get rate limits for a model."""
        return RATE_LIMITS.get(model, RateLimits(rpm=5, tpm=100_000, rpd=50))


def is_rate_limit_error(error_message: str) -> bool:
    """Check if an error message indicates a rate limit (429)."""
    indicators = [
        "429",
        "quota",
        "rate limit",
        "resource_exhausted",
        "too many requests",
    ]
    error_lower = error_message.lower()
    return any(indicator in error_lower for indicator in indicators)
