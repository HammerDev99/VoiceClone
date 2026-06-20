"""Tests del backstop de seguridad (deteccion de crisis).

Logica de seguridad critica: se prueba deteccion positiva (incluyendo variantes
con mayusculas y tildes), negativa (duelo "normal") y el contenido del recurso.
"""

from __future__ import annotations

import pytest

from voiceclone.domain import safety


@pytest.mark.parametrize(
    "texto",
    [
        "ya no aguanto mas",
        "quiero irme contigo",
        "creo que quiero matarme",
        "MEJOR ESTARIA MUERTA",
        "no quiero seguir viviendo",
        "voy a hacerme daño",
        "ya no puedo más",  # tilde
        "Quiero Morir",  # mayusculas mezcladas
    ],
)
def test_detect_crisis_signal_positivo(texto: str) -> None:
    assert safety.detect_crisis_signal(texto) is True


@pytest.mark.parametrize(
    "texto",
    [
        "te extrano mucho hoy",
        "hoy fue un dia dificil",
        "recuerdo cuando reiamos juntos",
        "te amo y te extraño",
        "",
    ],
)
def test_detect_crisis_signal_negativo(texto: str) -> None:
    assert safety.detect_crisis_signal(texto) is False


def test_crisis_response_incluye_linea_106() -> None:
    assert "106" in safety.CRISIS_RESPONSE


def test_crisis_response_no_es_vacio() -> None:
    assert len(safety.CRISIS_RESPONSE.strip()) > 50
