"""Tests del servicio de clonado de voz."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from returns.result import Failure, Success

from voiceclone.config.settings import Settings
from voiceclone.domain.models import ClonedVoice
from voiceclone.services import voice_cloning


def _make_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_discover_samples_dir_inexistente(tmp_path: Path) -> None:
    result = voice_cloning.discover_samples(tmp_path / "no_existe")
    assert isinstance(result, Failure)


def test_discover_samples_sin_audios(tmp_path: Path) -> None:
    result = voice_cloning.discover_samples(_make_dir(tmp_path / "audios"))
    assert isinstance(result, Failure)


def test_discover_samples_filtra_y_ordena(tmp_path: Path) -> None:
    audios = _make_dir(tmp_path / "audios")
    (audios / "b.m4a").write_bytes(b"x")
    (audios / "a.mp3").write_bytes(b"x")
    (audios / "notas.txt").write_text("ignorar")  # extension no soportada
    result = voice_cloning.discover_samples(audios)
    assert isinstance(result, Success)
    nombres = [p.name for p in result.unwrap()]
    assert nombres == ["a.mp3", "b.m4a"]


def test_clone_voice_exito(
    tmp_path: Path,
    make_settings: Callable[..., Settings],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audios = _make_dir(tmp_path / "audios")
    (audios / "clip.m4a").write_bytes(b"x")
    settings = make_settings(audio_input_dir=audios)

    monkeypatch.setattr(
        voice_cloning.el,
        "create_instant_voice",
        lambda **_: Success(ClonedVoice(voice_id="voice_abc", name="Alexander")),
    )
    monkeypatch.setattr(voice_cloning, "save_voice_id", lambda _voice_id: Success(None))

    result = voice_cloning.clone_voice(MagicMock(), settings)
    assert isinstance(result, Success)
    assert result.unwrap().voice_id == "voice_abc"


def test_clone_voice_propaga_fallo_de_descubrimiento(
    tmp_path: Path,
    make_settings: Callable[..., Settings],
) -> None:
    settings = make_settings(audio_input_dir=tmp_path / "vacio")
    result = voice_cloning.clone_voice(MagicMock(), settings)
    assert isinstance(result, Failure)
