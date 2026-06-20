"""Servicio de sintesis de voz (texto -> audio con la voz clonada)."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from elevenlabs.client import ElevenLabs
from returns.result import Failure, Result, Success

from voiceclone.config.settings import Settings
from voiceclone.domain.models import GeneratedSpeech, SpeechRequest, VoiceTuning
from voiceclone.domain.voice_presets import get_preset
from voiceclone.infrastructure import elevenlabs_client as el
from voiceclone.infrastructure.logging import get_logger

logger = get_logger(__name__)

MAX_TEXT_LENGTH = 5000


def _extension_for_format(output_format: str) -> str:
    """Deriva la extension del archivo segun el formato de salida."""
    if output_format.startswith("mp3"):
        return "mp3"
    if output_format.startswith("pcm"):
        return "wav"
    if output_format.startswith(("ulaw", "alaw")):
        return "raw"
    if output_format.startswith("opus"):
        return "opus"
    return "audio"


def _slugify(text: str, max_len: int = 30) -> str:
    """Crea un fragmento seguro para nombre de archivo a partir del texto."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:max_len] or "voz"


def build_output_path(text: str, settings: Settings) -> Path:
    """Construye una ruta de salida unica (timestamp + fragmento del texto)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = _extension_for_format(settings.elevenlabs_output_format)
    filename = f"{timestamp}_{_slugify(text)}.{extension}"
    return settings.audio_output_dir / filename


def _resolve_tuning(settings: Settings, tuning: VoiceTuning | None) -> VoiceTuning | None:
    """Resuelve el afinado: el explicito gana; si no, el preset por defecto."""
    if tuning is not None:
        return tuning
    preset_result = get_preset(settings.voice_preset)
    if isinstance(preset_result, Failure):
        logger.warning("Preset de voz invalido (%s); se usan ajustes por defecto del servidor.",
                       settings.voice_preset)
        return None
    return preset_result.unwrap()


def synthesize(
    client: ElevenLabs,
    settings: Settings,
    text: str,
    voice_id: str | None = None,
    tuning: VoiceTuning | None = None,
    output_path: Path | None = None,
) -> Result[GeneratedSpeech, str]:
    """Convierte ``text`` a voz y guarda el audio en ``output/``.

    Args:
        client: Cliente de ElevenLabs ya inicializado.
        settings: Configuracion del proyecto.
        text: Texto a sintetizar.
        voice_id: Voz a usar; si es ``None``, se toma de ``settings.voice_id``.
        tuning: Afinado de voz; si es ``None``, se usa el preset por defecto.
        output_path: Ruta de salida; si es ``None``, se genera en ``output/``.

    Returns:
        ``Success(GeneratedSpeech)`` o ``Failure(mensaje)``.
    """
    clean = text.strip()
    if not clean:
        return Failure("El texto a sintetizar esta vacio.")
    if len(clean) > MAX_TEXT_LENGTH:
        return Failure(f"El texto excede {MAX_TEXT_LENGTH} caracteres ({len(clean)}).")

    resolved_voice = (voice_id or settings.voice_id or "").strip()
    if not resolved_voice:
        return Failure(
            "No hay VOICE_ID. Clona la voz primero (scripts/02_clonar_voz.py) "
            "o define VOICE_ID en .env."
        )

    request = SpeechRequest(
        text=clean,
        voice_id=resolved_voice,
        model_id=settings.elevenlabs_model_id,
        output_format=settings.elevenlabs_output_format,
        tuning=_resolve_tuning(settings, tuning),
    )

    audio_result = el.text_to_speech(client, request)
    if isinstance(audio_result, Failure):
        return audio_result
    audio_bytes = audio_result.unwrap()

    target_path = output_path or build_output_path(clean, settings)
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(audio_bytes)
    except OSError as exc:
        logger.error("No se pudo guardar el audio", exc_info=True)
        return Failure(f"Error guardando el audio en {target_path}: {exc}")

    logger.info("Audio generado: %s (%d bytes)", target_path, len(audio_bytes))
    return Success(GeneratedSpeech(path=target_path, bytes_written=len(audio_bytes)))
