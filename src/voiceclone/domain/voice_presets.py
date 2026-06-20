"""Presets de afinado de voz para comparar y elegir la mejor calidad.

Cada preset es un ``VoiceTuning`` con un nombre descriptivo. El script de
calibracion (``scripts/05_calibrar_voz.py``) genera el mismo texto con cada
preset para poder compararlos a oido y elegir el favorito.
"""

from __future__ import annotations

from returns.result import Failure, Result, Success

from voiceclone.domain.models import VoiceTuning

# Preset por defecto: tono pausado y afectuoso, apropiado para un memorial.
DEFAULT_PRESET = "calido_sereno"

PRESETS: dict[str, VoiceTuning] = {
    # Balance recomendado por ElevenLabs: natural y consistente.
    "natural": VoiceTuning(stability=0.50, similarity_boost=0.75, style=0.0, speed=1.0),
    # Muy consistente y sereno; menos variacion emocional.
    "estable": VoiceTuning(stability=0.75, similarity_boost=0.80, style=0.0, speed=0.95),
    # Calido, pausado y cercano: pensado para el memorial (por defecto).
    "calido_sereno": VoiceTuning(stability=0.65, similarity_boost=0.85, style=0.10, speed=0.92),
    # Mas emocion y matices, a costa de algo de consistencia.
    "expresivo": VoiceTuning(stability=0.35, similarity_boost=0.80, style=0.30, speed=1.0),
}


def get_preset(name: str) -> Result[VoiceTuning, str]:
    """Devuelve el ``VoiceTuning`` de un preset por nombre."""
    tuning = PRESETS.get(name.strip().lower())
    if tuning is None:
        disponibles = ", ".join(sorted(PRESETS))
        return Failure(f"Preset de voz desconocido: '{name}'. Disponibles: {disponibles}")
    return Success(tuning)


def preset_names() -> list[str]:
    """Lista de nombres de presets disponibles (orden estable)."""
    return sorted(PRESETS)
