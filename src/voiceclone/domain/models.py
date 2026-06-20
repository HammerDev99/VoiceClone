"""DTOs inmutables del dominio.

Todos los modelos son ``frozen=True`` para prevenir mutacion accidental
y bugs de estado compartido (regla critica del proyecto).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VoiceSample:
    """Una muestra de audio usada para clonar la voz."""

    path: Path

    @property
    def name(self) -> str:
        return self.path.name


@dataclass(frozen=True)
class ClonedVoice:
    """Voz ya clonada en ElevenLabs."""

    voice_id: str
    name: str


@dataclass(frozen=True)
class VoiceTuning:
    """Ajustes de calidad/tono de la voz al sintetizar.

    Rangos (ElevenLabs):
    - ``stability`` 0-1: bajo = mas expresivo/variable, alto = mas estable.
    - ``similarity_boost`` 0-1: cercania al timbre original.
    - ``style`` 0-1: exageracion del estilo (0 favorece la estabilidad).
    - ``speed`` ~0.7-1.2: 1.0 = velocidad normal.
    - ``use_speaker_boost``: refuerza el parecido con el hablante.
    """

    stability: float
    similarity_boost: float
    style: float
    speed: float
    use_speaker_boost: bool = True


@dataclass(frozen=True)
class SpeechRequest:
    """Peticion de sintesis de voz (texto -> audio)."""

    text: str
    voice_id: str
    model_id: str
    output_format: str
    tuning: VoiceTuning | None = None


@dataclass(frozen=True)
class GeneratedSpeech:
    """Resultado de una sintesis: audio guardado en disco."""

    path: Path
    bytes_written: int


@dataclass(frozen=True)
class ConversationTurn:
    """Un turno de conversacion con la persona.

    ``role`` es ``"user"`` o ``"assistant"`` (compatible con la API de Claude).
    """

    role: str
    content: str


@dataclass(frozen=True)
class AccountInfo:
    """Resumen del estado de la cuenta de ElevenLabs."""

    tier: str
    characters_used: int
    characters_limit: int
    can_clone_ivc: bool = True

    @property
    def characters_remaining(self) -> int:
        return max(self.characters_limit - self.characters_used, 0)
