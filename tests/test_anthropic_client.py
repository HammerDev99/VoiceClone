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
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100, 0.4)
    assert isinstance(result, Success)
    assert "Alexander" in result.unwrap()


def test_generate_message_sin_texto_es_fallo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ac, "TextBlock", _DummyTextBlock)
    client = _client_con_contenido([])
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100, 0.4)
    assert isinstance(result, Failure)


def test_generate_message_maneja_excepcion() -> None:
    client = MagicMock()
    client.messages.create.side_effect = RuntimeError("boom")
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100, 0.4)
    assert isinstance(result, Failure)


def test_generate_message_envia_temperature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ac, "TextBlock", _DummyTextBlock)
    client = _client_con_contenido([_DummyTextBlock("ok")])
    ac.generate_message(client, "claude-opus-4-8", "system", [], 100, 0.4)
    _, kwargs = client.messages.create.call_args
    assert kwargs["temperature"] == 0.4


def test_generate_message_omite_temperature_si_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ac, "TextBlock", _DummyTextBlock)
    client = _client_con_contenido([_DummyTextBlock("ok")])
    ac.generate_message(client, "claude-opus-4-8", "system", [], 100, None)
    _, kwargs = client.messages.create.call_args
    assert "temperature" not in kwargs


def test_generate_message_reintenta_sin_temperature_si_deprecada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ac, "TextBlock", _DummyTextBlock)
    client = MagicMock()
    ok = MagicMock(content=[_DummyTextBlock("hola")])
    # 1ra llamada: el modelo rechaza temperature; 2da (sin temperature): exito.
    client.messages.create.side_effect = [
        Exception("temperature is deprecated for this model"),
        ok,
    ]
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100, 0.4)
    assert isinstance(result, Success)
    assert result.unwrap() == "hola"
    assert client.messages.create.call_count == 2
    _, kwargs_reintento = client.messages.create.call_args_list[1]
    assert "temperature" not in kwargs_reintento


def test_generate_message_no_reintenta_si_error_no_es_de_temperature() -> None:
    client = MagicMock()
    client.messages.create.side_effect = RuntimeError("overloaded")
    result = ac.generate_message(client, "claude-opus-4-8", "system", [], 100, 0.4)
    assert isinstance(result, Failure)
    assert client.messages.create.call_count == 1  # no reintenta en otros errores
