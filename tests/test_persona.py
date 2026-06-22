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


def test_persona_tiene_protocolo_de_crisis() -> None:
    prompt = alexander_persona().system_prompt.lower()
    assert "linea 106" in prompt or "línea 106" in prompt
    assert "protocolo de crisis" in prompt


def test_persona_prohibe_invitacion_a_la_reunion() -> None:
    prompt = alexander_persona().system_prompt.lower()
    assert "prohibicion absoluta" in prompt or "prohibición absoluta" in prompt


def test_persona_no_promete_sanacion_completa() -> None:
    prompt = alexander_persona().system_prompt.lower()
    assert "vinculos continuos" in prompt or "vínculos continuos" in prompt


def test_persona_tiene_matiz_paisa() -> None:
    prompt = alexander_persona().system_prompt.lower()
    assert "paisa" in prompt or "antioqu" in prompt


def test_voice_description_menciona_acento_paisa() -> None:
    desc = voice_description().lower()
    assert "paisa" in desc or "antioqu" in desc


def test_persona_instruye_ortografia_con_enie_y_tildes() -> None:
    # El prompt debe INSTRUIR explicitamente el espanol correcto: sin esa directiva
    # Claude tiende a omitir la ñ y las tildes en sus respuestas (y el TTS las
    # pronuncia mal, p.ej. "ano" por "año").
    prompt = alexander_persona().system_prompt
    low = prompt.lower()
    assert "ñ" in prompt
    assert "ortografía" in low or "tildes" in low


def test_persona_no_usa_mi_amor() -> None:
    assert "mi amor" not in alexander_persona().system_prompt.lower()
