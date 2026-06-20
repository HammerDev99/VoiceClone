"""Tests del servicio de conversacion (capa persona/Claude)."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from returns.result import Failure, Success

from voiceclone.config.settings import Settings
from voiceclone.domain.models import ConversationTurn
from voiceclone.domain.persona import alexander_persona
from voiceclone.services import conversation


def test_to_message_params_estructura() -> None:
    history = [
        ConversationTurn(role="user", content="hola"),
        ConversationTurn(role="assistant", content="te recuerdo"),
    ]
    params = conversation._to_message_params(history, "como estas")
    assert params[0] == {"role": "user", "content": "hola"}
    assert params[1] == {"role": "assistant", "content": "te recuerdo"}
    assert params[-1] == {"role": "user", "content": "como estas"}


def test_generate_reply_mensaje_vacio(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(anthropic_api_key="sk-ant-test")
    result = conversation.generate_reply(settings, alexander_persona(), [], "   ")
    assert isinstance(result, Failure)


def test_generate_reply_sin_anthropic_key(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(anthropic_api_key="")
    result = conversation.generate_reply(settings, alexander_persona(), [], "hola")
    assert isinstance(result, Failure)
    assert "ANTHROPIC_API_KEY" in result.failure()


def test_generate_reply_exito(
    make_settings: Callable[..., Settings], monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = make_settings(anthropic_api_key="sk-ant-test")
    monkeypatch.setattr(conversation.ac, "build_client", lambda _key: Success(MagicMock()))
    monkeypatch.setattr(
        conversation.ac, "generate_message", lambda **_: Success("Hola, soy Alexander.")
    )
    result = conversation.generate_reply(settings, alexander_persona(), [], "te extrano")
    assert isinstance(result, Success)
    assert "Alexander" in result.unwrap()


def test_generate_reply_propaga_fallo_de_cliente(
    make_settings: Callable[..., Settings], monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = make_settings(anthropic_api_key="sk-ant-test")
    monkeypatch.setattr(conversation.ac, "build_client", lambda _key: Failure("init falló"))
    result = conversation.generate_reply(settings, alexander_persona(), [], "hola")
    assert isinstance(result, Failure)


def test_generate_reply_propaga_fallo_de_generacion(
    make_settings: Callable[..., Settings], monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = make_settings(anthropic_api_key="sk-ant-test")
    monkeypatch.setattr(conversation.ac, "build_client", lambda _key: Success(MagicMock()))
    monkeypatch.setattr(conversation.ac, "generate_message", lambda **_: Failure("api caida"))
    result = conversation.generate_reply(settings, alexander_persona(), [], "hola")
    assert isinstance(result, Failure)
    assert "api caida" in result.failure()
