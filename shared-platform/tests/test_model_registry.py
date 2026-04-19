import pytest

from llm_gateway.model_registry import ModelConfig, ModelRegistry


def test_register_and_get():
    registry = ModelRegistry()
    config = ModelConfig(provider="openai", model_name="gpt-4o")
    registry.register("gpt4o", config)
    result = registry.get("gpt4o")
    assert result is not None
    assert result.provider == "openai"
    assert result.model_name == "gpt-4o"


def test_get_returns_none_for_unknown_alias():
    registry = ModelRegistry()
    assert registry.get("nonexistent-model") is None


def test_require_raises_key_error_for_unknown_alias():
    registry = ModelRegistry()
    with pytest.raises(KeyError, match="not registered"):
        registry.require("ghost-model")


def test_require_returns_registered_config():
    registry = ModelRegistry()
    config = ModelConfig(
        provider="anthropic",
        model_name="claude-sonnet-4-6",
        supports_tools=True,
        supports_json_mode=True,
    )
    registry.register("claude", config)
    result = registry.require("claude")
    assert result.supports_tools is True
    assert result.supports_json_mode is True


def test_model_config_defaults_are_false():
    config = ModelConfig(provider="gemini", model_name="gemini-pro")
    assert config.supports_tools is False
    assert config.supports_json_mode is False
    assert config.supports_vision is False


def test_register_overwrites_existing_alias():
    registry = ModelRegistry()
    registry.register("model", ModelConfig(provider="openai", model_name="gpt-3.5-turbo"))
    registry.register("model", ModelConfig(provider="openai", model_name="gpt-4o"))
    assert registry.require("model").model_name == "gpt-4o"
