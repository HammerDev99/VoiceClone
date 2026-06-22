"""Fixtures compartidas para los tests."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from voiceclone.config.settings import Settings


@pytest.fixture
def make_settings(tmp_path: Path) -> Callable[..., Settings]:
    """Factory de ``Settings`` con valores de prueba y overrides opcionales."""

    def _factory(**overrides: object) -> Settings:
        defaults: dict[str, object] = {
            "elevenlabs_api_key": "sk_test_key",
            "elevenlabs_model_id": "eleven_multilingual_v2",
            "elevenlabs_output_format": "mp3_44100_128",
            "anthropic_api_key": "",
            "anthropic_model": "claude-opus-4-8",
            "anthropic_temperature": None,
            "voice_name": "Alexander",
            "voice_id": None,
            "voice_preset": "calido_sereno",
            "audio_input_dir": tmp_path / "audios",
            "audio_output_dir": tmp_path / "output",
            "log_level": "INFO",
        }
        defaults.update(overrides)
        return Settings(**defaults)  # type: ignore[arg-type]

    return _factory
