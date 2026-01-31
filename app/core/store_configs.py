from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from app.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class StoreConfig:
    """Configuration for store-specific browser behavior."""

    domain_keyword: str
    cookie_click_targets: list[str] = field(default_factory=list)
    cookie_hide_selectors: list[str] = field(default_factory=list)
    custom_interaction: (
        Callable[[Any, str | None], Coroutine[Any, Any, None]] | None
    ) = None


# Store-specific configurations
STORE_CONFIGS: dict[str, StoreConfig] = {}


def register_store(config: StoreConfig):
    """Register a store configuration."""
    STORE_CONFIGS[config.domain_keyword] = config


# --- Specialized Interactions ---


async def handle_zalando_interaction(page, target_size: str | None = None):
    """Specialized interaction for Zalando to handle size selection."""
    logger.info("Handling Zalando interaction (target_size: %s)", target_size)

    async def find_button(selectors):
        for s in selectors:
            try:
                btn = page.locator(s).first
                if await btn.is_visible(timeout=3000):
                    return btn
            except Exception as e:
                logger.debug("Button selector '%s' failed: %s", s, e)
                continue
        return None

    try:
        # 1. Trigger size picker
        btn = await find_button(
            [
                'button[data-testid="pdp-size-picker-trigger"]',
                'button[data-testid="pdp-size-selector-trigger"]',
                'button:has-text("Maat kiezen")',
                'button:has-text("Select size")',
            ]
        )

        if btn:
            await btn.scroll_into_view_if_needed()
            await btn.click()
            await page.wait_for_timeout(1000)

            if target_size:
                # 2. Select specific size
                opt = await find_button(
                    [
                        f'button[data-testid*="size"]:has-text("{target_size}")',
                        f'button:has-text("{target_size}")',
                    ]
                )
                if opt:
                    await opt.click()
                    await page.wait_for_timeout(2000)
    except Exception:
        logger.exception("Zalando interaction failed")


# --- Registry Initialization ---

register_store(
    StoreConfig(
        domain_keyword="decathlon",
        cookie_click_targets=[
            "#didomi-notice-agree-button",
            'button:has-text("Akkoord en sluiten")',
        ],
        cookie_hide_selectors=["#didomi-host"],
    )
)

register_store(
    StoreConfig(domain_keyword="zalando", custom_interaction=handle_zalando_interaction)
)
