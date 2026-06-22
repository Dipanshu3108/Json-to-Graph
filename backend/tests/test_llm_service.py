import os

from app.services import llm_service


def test_models_map_has_all_providers() -> None:
    assert set(llm_service.MODELS.keys()) == {"anthropic", "openai", "gemini", "ollama"}


def test_timeout_is_numeric() -> None:
    assert isinstance(llm_service.TIMEOUT, float)


def test_provider_default_or_env() -> None:
    provider = os.getenv("LLM_PROVIDER", "anthropic")
    assert llm_service.PROVIDER == provider
