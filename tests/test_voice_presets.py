"""Tests de los presets de afinado de voz."""

from __future__ import annotations

import dataclasses

import pytest
from returns.result import Failure, Success

from voiceclone.domain.models import VoiceTuning
from voiceclone.domain.voice_presets import (
    DEFAULT_PRESET,
    PRESETS,
    get_preset,
    preset_names,
)


def test_default_preset_existe() -> None:
    assert DEFAULT_PRESET in PRESETS


def test_preset_names_ordenados_y_completos() -> None:
    nombres = preset_names()
    assert nombres == sorted(PRESETS)
    assert set(nombres) == {"natural", "calido_sereno"}


def test_get_preset_valido() -> None:
    result = get_preset("calido_sereno")
    assert isinstance(result, Success)
    assert isinstance(result.unwrap(), VoiceTuning)


def test_get_preset_case_insensitive() -> None:
    assert isinstance(get_preset("  Natural  "), Success)


def test_get_preset_invalido() -> None:
    result = get_preset("inexistente")
    assert isinstance(result, Failure)
    assert "Disponibles" in result.failure()


def test_tuning_es_inmutable() -> None:
    tuning = get_preset("natural").unwrap()
    with pytest.raises(dataclasses.FrozenInstanceError):
        tuning.stability = 0.9  # type: ignore[misc]


@pytest.mark.parametrize("name", list(PRESETS))
def test_todos_los_presets_en_rango(name: str) -> None:
    t = PRESETS[name]
    assert 0.0 <= t.stability <= 1.0
    assert 0.0 <= t.similarity_boost <= 1.0
    assert 0.0 <= t.style <= 1.0
    assert 0.7 <= t.speed <= 1.2
