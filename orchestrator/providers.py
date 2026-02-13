"""
Multi-provider abstraction for Oh My Codex.
Supports OpenAI (default), with interfaces for Gemini and Anthropic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderType(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    provider: ProviderType
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""
    enabled: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderResponse:
    """Unified response from any provider."""
    content: str
    model: str = ""
    provider: ProviderType = ProviderType.OPENAI
    tokens_used: int = 0
    success: bool = True
    error: str = ""


# Default model mappings per provider
PROVIDER_MODELS: dict[ProviderType, dict[str, str]] = {
    ProviderType.OPENAI: {
        "fast": "gpt-5.3-codex-spark",
        "standard": "gpt-5.2-codex",
        "powerful": "gpt-5.3-codex",
    },
    ProviderType.GEMINI: {
        "fast": "gemini-2.5-flash",
        "standard": "gemini-2.5-pro",
        "powerful": "gemini-2.5-pro",
    },
    ProviderType.ANTHROPIC: {
        "fast": "claude-haiku-4-5-20251001",
        "standard": "claude-sonnet-4-5-20250929",
        "powerful": "claude-opus-4-6",
    },
}

# Task-to-provider routing recommendations
TASK_ROUTING: dict[str, ProviderType] = {
    "code": ProviderType.OPENAI,
    "analysis": ProviderType.OPENAI,
    "design": ProviderType.GEMINI,
    "creative": ProviderType.GEMINI,
    "reasoning": ProviderType.ANTHROPIC,
    "review": ProviderType.ANTHROPIC,
}


class ProviderManager:
    """Manages multiple AI providers."""

    def __init__(self) -> None:
        self._providers: dict[ProviderType, ProviderConfig] = {}
        self._default: ProviderType = ProviderType.OPENAI

    def register(self, config: ProviderConfig) -> None:
        """Register a provider."""
        self._providers[config.provider] = config

    def set_default(self, provider: ProviderType) -> None:
        """Set the default provider."""
        self._default = provider

    def get_default(self) -> ProviderType:
        """Get the default provider type."""
        return self._default

    def get_provider(self, provider: ProviderType | None = None) -> ProviderConfig | None:
        """Get provider config."""
        pt = provider or self._default
        return self._providers.get(pt)

    def list_providers(self) -> list[ProviderConfig]:
        """List all registered providers."""
        return list(self._providers.values())

    def get_enabled_providers(self) -> list[ProviderConfig]:
        """List enabled providers."""
        return [p for p in self._providers.values() if p.enabled]

    def get_model(self, tier: str = "standard", provider: ProviderType | None = None) -> str:
        """Get model name for a tier from a provider."""
        pt = provider or self._default
        models = PROVIDER_MODELS.get(pt, {})
        return models.get(tier, models.get("standard", ""))

    def route_task(self, task_type: str) -> ProviderType:
        """Route a task type to the best provider."""
        recommended = TASK_ROUTING.get(task_type, self._default)
        # Only use if the provider is registered and enabled
        config = self._providers.get(recommended)
        if config and config.enabled:
            return recommended
        return self._default

    def is_available(self, provider: ProviderType) -> bool:
        """Check if a provider is registered and enabled."""
        config = self._providers.get(provider)
        return config is not None and config.enabled
