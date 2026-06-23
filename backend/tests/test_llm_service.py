import os

from app.services import llm_service


def test_kimi_model_is_configured() -> None:
    assert llm_service.MODEL


def test_timeout_is_numeric() -> None:
    assert isinstance(llm_service.TIMEOUT, float)


def test_base_url_has_default() -> None:
    assert llm_service.BASE_URL
