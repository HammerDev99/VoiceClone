"""Senales de seguridad: deteccion de riesgo de autolesion/crisis emocional.

Funcion pura, sin efectos secundarios. Actua como backstop independiente del
LLM: la deteccion no depende de que el modelo "decida" frenar en cada turno.
Es deliberadamente conservadora (prefiere falsos positivos a falsos negativos):
ante la duda, mejor mostrar el recurso de apoyo que omitirlo.

Pertenece a la capa ``domain`` (pura, sin I/O). El recurso de crisis es la
Linea 106 de Colombia (gratuita, 24 horas, verificada con el Ministerio de Salud).
"""

from __future__ import annotations

import re

# Patrones de riesgo en espanol. Toleran mayusculas (re.IGNORECASE) y las
# tildes mas frecuentes ([aá], [ií], da[nñ]o) para no perder variantes reales.
_CRISIS_PATTERNS: tuple[str, ...] = (
    r"quiero (morir|matarme|suicidarme)",
    r"no quiero (vivir|seguir viviendo|estar m[aá]s aqu[ií])",
    r"(quiero|voy a) (hacerme da[nñ]o|lastimarme|quitarme la vida)",
    r"quiero irme contigo",
    r"ya no (aguanto|puedo) m[aá]s",
    r"mejor (estaria|estuviera|estaría) muert[oa]",
)

_COMPILED = tuple(re.compile(p, re.IGNORECASE) for p in _CRISIS_PATTERNS)


def detect_crisis_signal(text: str) -> bool:
    """Devuelve ``True`` si el texto contiene una senal de riesgo conocida."""
    return any(pattern.search(text) for pattern in _COMPILED)


CRISIS_RESPONSE = (
    "Quiero detenerme un momento porque lo que acabas de compartir me importa "
    "mucho. Tu vida es valiosa y mereces apoyo real ahora mismo, no solo mis "
    "palabras. En Colombia puedes llamar gratis, las 24 horas, a la Linea 106 "
    "desde cualquier celular o telefono fijo. Por favor, comunicate tambien con "
    "alguien de tu confianza en este momento. Sigo aqui contigo."
)
