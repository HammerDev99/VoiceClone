"""Tests del cliente de infraestructura de Anthropic (con SDK mockeado)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from returns.result import Failure, Success

from voiceclone.infrastructure import anthropic_client as ac


class _DummyTextBlock:
    """Imita un TextBlock de Anthropic (tiene atributo .text)."""

    def __init__(self, text: str) -> None:
        self.text = text


def test_build_client_rechaza_key_vacia() -> None:
    assert isinstance(ac.build_client("   "), Failure)


def test_build_client_ok() -> None:
    assert isinstance(ac.build_client("sk-ant-fake"), Success)


def _client_con_contenido(blocks: list[object]) -> MagicMock:
    client = MagicMock()
    client.messages.create.return_value = MagicMock(content=blocks)
    return client


def test_generate_message_exito(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ac, "TextBlock", _DummyTextBlock)
    client = _client_con_contenido([_DummyTextBlock("Hola, soy Alexander.")])
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100)
    assert isinstance(result, Success)
    assert "Alexander" in result.unwrap()


def test_generate_message_sin_texto_es_fallo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ac, "TextBlock", _DummyTextBlock)
    client = _client_con_contenido([])
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100)
    assert isinstance(result, Failure)


def test_generate_message_maneja_excepcion() -> None:
    client = MagicMock()
    client.messages.create.side_effect = RuntimeError("boom")
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100)
    assert isinstance(result, Failure)


def test_generate_message_solo_envia_parametros_soportados(monkeypatch: pytest.MonkeyPatch) -> None:
    # El SDK 1.x de Anthropic ya no acepta 'temperature' (ni top_p/top_k).
    monkeypatch.setattr(ac, "TextBlock", _DummyTextBlock)
    client = _client_con_contenido([_DummyTextBlock("ok")])
    ac.generate_message(client, "claude-opus-4-8", "system", [], 100)
    _, kwargs = client.messages.create.call_args
    assert set(kwargs) == {"model", "max_tokens", "system", "messages"}


def test_generate_message_no_acepta_temperature() -> None:
    with pytest.raises(TypeError):
        ac.generate_message(MagicMock(), "claude-opus-4-8", "system", [], 100, 0.4)  # type: ignore[call-arg]


def test_generate_message_no_reintenta_ante_errores() -> None:
    client = MagicMock()
    client.messages.create.side_effect = RuntimeError("overloaded")
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100)
    assert isinstance(result, Failure)
    assert client.messages.create.call_count == 1
