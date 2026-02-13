"""Tests for providers module."""
import pytest
from orchestrator.providers import (
    ProviderType,
    ProviderConfig,
    ProviderManager,
    ProviderResponse,
    PROVIDER_MODELS,
    TASK_ROUTING,
)


class TestProviderType:
    def test_openai_value(self):
        assert ProviderType.OPENAI.value == "openai"

    def test_gemini_value(self):
        assert ProviderType.GEMINI.value == "gemini"

    def test_anthropic_value(self):
        assert ProviderType.ANTHROPIC.value == "anthropic"


class TestProviderConfig:
    def test_create(self):
        config = ProviderConfig(provider=ProviderType.OPENAI, api_key="sk-test")
        assert config.provider == ProviderType.OPENAI
        assert config.api_key == "sk-test"

    def test_defaults(self):
        config = ProviderConfig(provider=ProviderType.OPENAI)
        assert config.api_key == ""
        assert config.base_url == ""
        assert config.default_model == ""
        assert config.enabled is True
        assert config.extra == {}


class TestProviderResponse:
    def test_create(self):
        resp = ProviderResponse(content="Hello", model="gpt-5.3-codex")
        assert resp.content == "Hello"
        assert resp.model == "gpt-5.3-codex"

    def test_defaults(self):
        resp = ProviderResponse(content="test")
        assert resp.model == ""
        assert resp.provider == ProviderType.OPENAI
        assert resp.tokens_used == 0
        assert resp.success is True
        assert resp.error == ""


class TestProviderModels:
    def test_has_openai(self):
        assert ProviderType.OPENAI in PROVIDER_MODELS

    def test_has_gemini(self):
        assert ProviderType.GEMINI in PROVIDER_MODELS

    def test_has_anthropic(self):
        assert ProviderType.ANTHROPIC in PROVIDER_MODELS

    def test_openai_tiers(self):
        models = PROVIDER_MODELS[ProviderType.OPENAI]
        assert "fast" in models
        assert "standard" in models
        assert "powerful" in models

    def test_gemini_models(self):
        models = PROVIDER_MODELS[ProviderType.GEMINI]
        assert "gemini-2.5-flash" in models["fast"]

    def test_anthropic_models(self):
        models = PROVIDER_MODELS[ProviderType.ANTHROPIC]
        assert "claude" in models["standard"]


class TestTaskRouting:
    def test_has_code(self):
        assert "code" in TASK_ROUTING

    def test_has_analysis(self):
        assert "analysis" in TASK_ROUTING

    def test_has_design(self):
        assert "design" in TASK_ROUTING

    def test_has_reasoning(self):
        assert "reasoning" in TASK_ROUTING

    def test_routes_to_valid_providers(self):
        for task_type, provider in TASK_ROUTING.items():
            assert isinstance(provider, ProviderType)


class TestProviderManager:
    def test_register(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI, api_key="key"))
        assert mgr.get_provider(ProviderType.OPENAI) is not None

    def test_get_provider(self):
        mgr = ProviderManager()
        config = ProviderConfig(provider=ProviderType.GEMINI, api_key="key")
        mgr.register(config)
        retrieved = mgr.get_provider(ProviderType.GEMINI)
        assert retrieved is not None
        assert retrieved.api_key == "key"

    def test_get_provider_default(self):
        mgr = ProviderManager()
        config = ProviderConfig(provider=ProviderType.OPENAI)
        mgr.register(config)
        retrieved = mgr.get_provider()
        assert retrieved is not None

    def test_get_provider_nonexistent(self):
        mgr = ProviderManager()
        assert mgr.get_provider(ProviderType.GEMINI) is None

    def test_list_providers(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI))
        mgr.register(ProviderConfig(provider=ProviderType.GEMINI))
        assert len(mgr.list_providers()) == 2

    def test_list_providers_empty(self):
        mgr = ProviderManager()
        assert mgr.list_providers() == []

    def test_enabled_providers(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI, enabled=True))
        mgr.register(ProviderConfig(provider=ProviderType.GEMINI, enabled=False))
        assert len(mgr.get_enabled_providers()) == 1

    def test_get_enabled_providers(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI, enabled=True))
        mgr.register(ProviderConfig(provider=ProviderType.GEMINI, enabled=False))
        enabled = mgr.get_enabled_providers()
        assert len(enabled) == 1
        assert enabled[0].provider == ProviderType.OPENAI

    def test_default(self):
        mgr = ProviderManager()
        assert mgr.get_default() == ProviderType.OPENAI
        mgr.set_default(ProviderType.GEMINI)
        assert mgr.get_default() == ProviderType.GEMINI

    def test_set_default(self):
        mgr = ProviderManager()
        mgr.set_default(ProviderType.GEMINI)
        assert mgr.get_default() == ProviderType.GEMINI

    def test_get_default(self):
        mgr = ProviderManager()
        assert mgr.get_default() == ProviderType.OPENAI

    def test_get_model(self):
        mgr = ProviderManager()
        model = mgr.get_model("fast", ProviderType.OPENAI)
        assert "spark" in model or "codex" in model

    def test_get_model_standard(self):
        mgr = ProviderManager()
        model = mgr.get_model("standard", ProviderType.OPENAI)
        assert "gpt" in model or "codex" in model

    def test_get_model_fast(self):
        mgr = ProviderManager()
        model = mgr.get_model("fast", ProviderType.ANTHROPIC)
        assert "haiku" in model or "claude" in model

    def test_get_model_gemini(self):
        mgr = ProviderManager()
        model = mgr.get_model("fast", ProviderType.GEMINI)
        assert "gemini" in model

    def test_get_model_powerful(self):
        mgr = ProviderManager()
        model = mgr.get_model("powerful", ProviderType.GEMINI)
        assert "gemini" in model

    def test_get_model_default_provider(self):
        mgr = ProviderManager()
        mgr.set_default(ProviderType.OPENAI)
        model = mgr.get_model("standard")
        assert model != ""

    def test_get_model_unknown_tier(self):
        mgr = ProviderManager()
        model = mgr.get_model("unknown", ProviderType.OPENAI)
        assert model != ""

    def test_route_task_default(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI))
        result = mgr.route_task("code")
        assert result == ProviderType.OPENAI

    def test_route_task_to_registered(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI))
        mgr.register(ProviderConfig(provider=ProviderType.GEMINI))
        result = mgr.route_task("design")
        assert result == ProviderType.GEMINI

    def test_route_task_registered(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.ANTHROPIC, enabled=True))
        provider = mgr.route_task("reasoning")
        assert provider == ProviderType.ANTHROPIC

    def test_route_task_fallback(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI))
        result = mgr.route_task("design")
        assert result == ProviderType.OPENAI

    def test_route_task_unregistered(self):
        mgr = ProviderManager()
        mgr.set_default(ProviderType.OPENAI)
        provider = mgr.route_task("design")
        assert provider == ProviderType.OPENAI

    def test_route_task_disabled(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.GEMINI, enabled=False))
        mgr.set_default(ProviderType.OPENAI)
        provider = mgr.route_task("design")
        assert provider == ProviderType.OPENAI

    def test_route_task_unknown(self):
        mgr = ProviderManager()
        provider = mgr.route_task("unknown_task")
        assert provider == mgr.get_default()

    def test_is_available(self):
        mgr = ProviderManager()
        assert mgr.is_available(ProviderType.OPENAI) is False
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI))
        assert mgr.is_available(ProviderType.OPENAI) is True

    def test_is_available_registered(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI, enabled=True))
        assert mgr.is_available(ProviderType.OPENAI) is True

    def test_is_available_unregistered(self):
        mgr = ProviderManager()
        assert mgr.is_available(ProviderType.GEMINI) is False

    def test_is_available_disabled(self):
        mgr = ProviderManager()
        mgr.register(ProviderConfig(provider=ProviderType.OPENAI, enabled=False))
        assert mgr.is_available(ProviderType.OPENAI) is False

    def test_provider_models_complete(self):
        for pt in ProviderType:
            assert pt in PROVIDER_MODELS
            assert "fast" in PROVIDER_MODELS[pt]
            assert "standard" in PROVIDER_MODELS[pt]
