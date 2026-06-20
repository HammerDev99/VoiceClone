"""Servicio de clonado de voz (Instant Voice Cloning).

Orquesta: descubrir las muestras en ``audios/``, validarlas, invocar el
clonado IVC y persistir el ``voice_id`` resultante en ``.env``.
"""

from __future__ import annotations

from pathlib import Path

from elevenlabs.client import ElevenLabs
from returns.result import Failure, Result, Success

from voiceclone.config.settings import Settings, save_voice_id
from voiceclone.domain.models import ClonedVoice
from voiceclone.domain.persona import voice_description
from voiceclone.infrastructure import elevenlabs_client as el
from voiceclone.infrastructure.logging import get_logger

logger = get_logger(__name__)

# Formatos de audio aceptados como muestras de entrada.
SUPPORTED_EXTENSIONS = frozenset({".m4a", ".mp3", ".wav", ".ogg", ".flac", ".aac", ".webm"})


def discover_samples(input_dir: Path) -> Result[list[Path], str]:
    """Busca muestras de audio validas en el directorio de entrada.

    Args:
        input_dir: Carpeta donde estan las muestras (p.ej. ``audios/``).

    Returns:
        ``Success(lista ordenada de rutas)`` o ``Failure`` si no hay ninguna.
    """
    if not input_dir.exists():
        return Failure(f"La carpeta de audios no existe: {input_dir}")

    samples = sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not samples:
        return Failure(
            f"No se encontraron muestras de audio en {input_dir}. "
            f"Formatos aceptados: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    logger.info("Muestras encontradas: %d en %s", len(samples), input_dir)
    return Success(samples)


def clone_voice(client: ElevenLabs, settings: Settings) -> Result[ClonedVoice, str]:
    """Clona la voz a partir de las muestras y persiste el ``voice_id``.

    Args:
        client: Cliente de ElevenLabs ya inicializado.
        settings: Configuracion del proyecto.

    Returns:
        ``Success(ClonedVoice)`` o ``Failure(mensaje)``.
    """
    samples_result = discover_samples(settings.audio_input_dir)
    if isinstance(samples_result, Failure):
        return samples_result
    samples = samples_result.unwrap()

    cloned_result = el.create_instant_voice(
        client=client,
        name=settings.voice_name,
        sample_paths=samples,
        description=voice_description(),
    )
    if isinstance(cloned_result, Failure):
        return cloned_result
    cloned = cloned_result.unwrap()

    persist_result = save_voice_id(cloned.voice_id)
    if isinstance(persist_result, Failure):
        # La voz se creo bien; solo no se pudo guardar el id. Avisar, no abortar.
        logger.warning(
            "Voz creada pero no se pudo persistir VOICE_ID: %s",
            persist_result.failure(),
        )

    return Success(cloned)
