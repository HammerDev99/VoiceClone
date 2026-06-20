"""Tests de la persona de Alexander."""

from __future__ import annotations

import dataclasses

import pytest

from voiceclone.domain.persona import alexander_persona, voice_description


def test_persona_identidad() -> None:
    persona = alexander_persona()
    assert persona.name == "Alexander"
    assert "Alexander" in persona.system_prompt
    assert len(persona.system_prompt) > 200


def test_persona_es_inmutable() -> None:
    persona = alexander_persona()
    with pytest.raises(dataclasses.FrozenInstanceError):
        persona.name = "Otro"  # type: ignore[misc]


def test_voice_description_es_masculina() -> None:
    desc = voice_description().lower()
    assert "masculina" in desc
