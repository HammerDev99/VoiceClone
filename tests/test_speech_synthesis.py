"""Tests del servicio de sintesis de voz (TTS)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from hypothesis import given
from hypothesis import strategies as st
from returns.result import Failure, Success

from voiceclone.config.settings import Settings
from voiceclone.domain.models import VoiceTuning
from voiceclone.services import speech_synthesis as ss


@pytest.mark.parametrize(
    ("fmt", "ext"),
    [
        ("mp3_44100_128", "mp3"),
        ("pcm_16000", "wav"),
        ("opus_48000_64", "opus"),
        ("ulaw_8000", "raw"),
        ("desconocido", "audio"),
    ],
)
def test_extension_for_format(fmt: str, ext: str) -> None:
    assert ss._extension_for_format(fmt) == ext


@given(st.text())
def test_slugify_siempre_seguro(text: str) -> None:
    slug = ss._slugify(text)
    assert slug  # nunca vacio
    assert len(slug) <= 30
    assert all(c.isalnum() or c == "-" for c in slug)


def test_synthesize_texto_vacio(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(voice_id="v1")
    result = ss.synthesize(MagicMock(), settings, "   ")
    assert isinstance(result, Failure)


def test_synthesize_sin_voice_id(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(voice_id=None)
    result = ss.synthesize(MagicMock(), settings, "Hola")
    assert isinstance(result, Failure)
    assert "VOICE_ID" in result.failure()


def test_synthesize_exito_escribe_archivo(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(voice_id="v1")
    monkeypatch.setattr(ss.el, "text_to_speech", lambda *_: Success(b"FAKEAUDIO"))

    result = ss.synthesize(MagicMock(), settings, "Hola mundo")
    assert isinstance(result, Success)
    generated = result.unwrap()
    assert generated.path.exists()
    assert generated.path.read_bytes() == b"FAKEAUDIO"
    assert generated.bytes_written == len(b"FAKEAUDIO")


def test_synthesize_propaga_fallo_de_api(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(voice_id="v1")
    monkeypatch.setattr(ss.el, "text_to_speech", lambda *_: Failure("api caida"))
    result = ss.synthesize(MagicMock(), settings, "Hola")
    assert isinstance(result, Failure)
    assert "api caida" in result.failure()


def test_resolve_tuning_explicito_gana(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(voice_preset="natural")
    explicito = VoiceTuning(stability=0.1, similarity_boost=0.2, style=0.3, speed=1.0)
    assert ss._resolve_tuning(settings, explicito) is explicito


def test_resolve_tuning_usa_preset_por_defecto(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(voice_preset="natural")
    tuning = ss._resolve_tuning(settings, None)
    assert isinstance(tuning, VoiceTuning)
    assert tuning.stability == 0.50


def test_resolve_tuning_preset_invalido_devuelve_none(
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(voice_preset="inexistente")
    assert ss._resolve_tuning(settings, None) is None


def test_synthesize_pasa_tuning_al_request(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(voice_id="v1")
    capturado: dict[str, object] = {}

    def _fake_tts(_client: object, request: object) -> Success[bytes]:
        capturado["request"] = request
        return Success(b"AUDIO")

    monkeypatch.setattr(ss.el, "text_to_speech", _fake_tts)
    tuning = VoiceTuning(stability=0.65, similarity_boost=0.85, style=0.1, speed=0.92)
    ss.synthesize(MagicMock(), settings, "Hola", tuning=tuning)
    assert capturado["request"].tuning == tuning  # type: ignore[attr-defined]


def test_synthesize_usa_output_path(
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    settings = make_settings(voice_id="v1")
    monkeypatch.setattr(ss.el, "text_to_speech", lambda *_: Success(b"AUDIO"))
    destino = tmp_path / "calibracion" / "calibracion_natural.mp3"
    result = ss.synthesize(MagicMock(), settings, "Hola", output_path=destino)
    assert isinstance(result, Success)
    assert result.unwrap().path == destino
    assert destino.exists()
