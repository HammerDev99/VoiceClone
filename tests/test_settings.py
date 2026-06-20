"""Tests de carga y persistencia de configuracion."""

from __future__ import annotations

from pathlib import Path

import pytest
from returns.result import Failure, Success

from voiceclone.config.settings import load_settings, save_voice_id


def _write_env(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_load_settings_falla_sin_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    env = _write_env(tmp_path / ".env", "ELEVENLABS_API_KEY=\n")
    result = load_settings(env_path=env)
    assert isinstance(result, Failure)
    assert "ELEVENLABS_API_KEY" in result.failure()


def test_load_settings_exito(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("ELEVENLABS_API_KEY", "VOICE_ID", "ANTHROPIC_API_KEY", "VOICE_NAME"):
        monkeypatch.delenv(var, raising=False)
    env = _write_env(
        tmp_path / ".env",
        "ELEVENLABS_API_KEY=sk_real\nVOICE_NAME=Alexander\nVOICE_ID=voice_123\n",
    )
    result = load_settings(env_path=env)
    assert isinstance(result, Success)
    settings = result.unwrap()
    assert settings.elevenlabs_api_key == "sk_real"
    assert settings.voice_name == "Alexander"
    assert settings.voice_id == "voice_123"
    assert settings.has_voice_id is True
    assert settings.has_anthropic is False


def test_load_settings_temperature_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for var in ("ELEVENLABS_API_KEY", "ANTHROPIC_TEMPERATURE"):
        monkeypatch.delenv(var, raising=False)
    env = _write_env(tmp_path / ".env", "ELEVENLABS_API_KEY=sk_real\n")
    result = load_settings(env_path=env)
    assert isinstance(result, Success)
    assert result.unwrap().anthropic_temperature == 0.4


def test_load_settings_temperature_desde_entorno(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_TEMPERATURE", "0.7")
    env = _write_env(tmp_path / ".env", "ELEVENLABS_API_KEY=sk_real\n")
    result = load_settings(env_path=env)
    assert isinstance(result, Success)
    assert result.unwrap().anthropic_temperature == 0.7


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [("1.8", 1.0), ("-0.5", 0.0), ("no-es-numero", 0.4)],
)
def test_load_settings_temperature_se_normaliza(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, crudo: str, esperado: float
) -> None:
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_TEMPERATURE", crudo)
    env = _write_env(tmp_path / ".env", "ELEVENLABS_API_KEY=sk_real\n")
    result = load_settings(env_path=env)
    assert isinstance(result, Success)
    assert result.unwrap().anthropic_temperature == esperado


def test_save_voice_id_agrega_cuando_no_existe(tmp_path: Path) -> None:
    env = _write_env(tmp_path / ".env", "ELEVENLABS_API_KEY=sk_real\n")
    result = save_voice_id("voice_999", env_path=env)
    assert isinstance(result, Success)
    assert "VOICE_ID=voice_999" in env.read_text(encoding="utf-8")


def test_save_voice_id_reemplaza_existente(tmp_path: Path) -> None:
    env = _write_env(tmp_path / ".env", "VOICE_ID=viejo\nLOG_LEVEL=INFO\n")
    save_voice_id("voice_nuevo", env_path=env)
    content = env.read_text(encoding="utf-8")
    assert "VOICE_ID=voice_nuevo" in content
    assert "viejo" not in content
    assert "LOG_LEVEL=INFO" in content  # no rompe otras lineas


def test_save_voice_id_rechaza_vacio(tmp_path: Path) -> None:
    env = _write_env(tmp_path / ".env", "")
    result = save_voice_id("   ", env_path=env)
    assert isinstance(result, Failure)
