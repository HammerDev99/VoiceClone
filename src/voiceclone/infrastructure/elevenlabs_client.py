"""Cliente de infraestructura para la API de ElevenLabs.

Envuelve el SDK oficial y traduce sus excepciones a ``Result[T, str]``.
Este es el unico modulo autorizado a capturar excepciones amplias: es el
limite (boundary) con un servicio externo. Toda falla se registra y se
devuelve como ``Failure`` con un mensaje claro, nunca se silencia.
"""

from __future__ import annotations

from pathlib import Path

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from returns.result import Failure, Result, Success

from voiceclone.domain.models import AccountInfo, ClonedVoice, SpeechRequest
from voiceclone.infrastructure.logging import get_logger

logger = get_logger(__name__)


def build_client(api_key: str) -> Result[ElevenLabs, str]:
    """Construye el cliente de ElevenLabs a partir de la API key."""
    if not api_key.strip():
        return Failure("API key de ElevenLabs vacia.")
    try:
        return Success(ElevenLabs(api_key=api_key))
    except Exception as exc:  # boundary con SDK externo
        logger.error("No se pudo inicializar el cliente de ElevenLabs", exc_info=True)
        return Failure(f"Error al inicializar ElevenLabs: {exc}")


def get_account_info(client: ElevenLabs) -> Result[AccountInfo, str]:
    """Obtiene tier y uso de caracteres de la cuenta (verifica la conexion)."""
    try:
        sub = client.user.subscription.get()
        return Success(
            AccountInfo(
                tier=str(sub.tier),
                characters_used=int(sub.character_count),
                characters_limit=int(sub.character_limit),
                can_clone_ivc=bool(getattr(sub, "can_use_instant_voice_cloning", True)),
            )
        )
    except Exception as exc:  # boundary con SDK externo
        logger.error("No se pudo obtener la informacion de la cuenta", exc_info=True)
        return Failure(f"Error consultando la cuenta de ElevenLabs: {exc}")


def list_voices(client: ElevenLabs) -> Result[list[ClonedVoice], str]:
    """Lista las voces disponibles para la cuenta."""
    try:
        response = client.voices.get_all()
        voices = [ClonedVoice(voice_id=str(v.voice_id), name=str(v.name)) for v in response.voices]
        return Success(voices)
    except Exception as exc:  # boundary con SDK externo
        logger.error("No se pudieron listar las voces", exc_info=True)
        return Failure(f"Error listando voces: {exc}")


def create_instant_voice(
    client: ElevenLabs,
    name: str,
    sample_paths: list[Path],
    description: str,
) -> Result[ClonedVoice, str]:
    """Crea una voz mediante Instant Voice Cloning (IVC).

    Abre las muestras en modo binario y las envia al endpoint de IVC.

    Args:
        client: Cliente de ElevenLabs ya inicializado.
        name: Nombre con el que se registra la voz.
        sample_paths: Rutas a las muestras de audio.
        description: Descripcion de la voz (etiquetado).

    Returns:
        ``Success(ClonedVoice)`` con el ``voice_id``, o ``Failure(mensaje)``.
    """
    if not sample_paths:
        return Failure("No hay muestras de audio para clonar.")

    handles = []
    try:
        for path in sample_paths:
            handles.append(path.open("rb"))
        voice = client.voices.ivc.create(name=name, description=description, files=handles)
        voice_id = str(voice.voice_id)
        logger.info("Voz creada (IVC): %s -> %s", name, voice_id)
        return Success(ClonedVoice(voice_id=voice_id, name=name))
    except Exception as exc:  # boundary con SDK externo
        logger.error("Fallo el clonado IVC", exc_info=True)
        return Failure(f"Error en el clonado IVC: {exc}")
    finally:
        for handle in handles:
            handle.close()


def text_to_speech(client: ElevenLabs, request: SpeechRequest) -> Result[bytes, str]:
    """Convierte texto a voz y devuelve los bytes del audio.

    Args:
        client: Cliente de ElevenLabs ya inicializado.
        request: Datos de la sintesis (texto, voz, modelo, formato).

    Returns:
        ``Success(bytes)`` con el audio, o ``Failure(mensaje)``.
    """
    try:
        convert_kwargs: dict[str, object] = {
            "voice_id": request.voice_id,
            "text": request.text,
            "model_id": request.model_id,
            "output_format": request.output_format,
        }
        if request.tuning is not None:
            t = request.tuning
            convert_kwargs["voice_settings"] = VoiceSettings(
                stability=t.stability,
                similarity_boost=t.similarity_boost,
                style=t.style,
                speed=t.speed,
                use_speaker_boost=t.use_speaker_boost,
            )
        audio_stream = client.text_to_speech.convert(**convert_kwargs)
        audio_bytes = b"".join(audio_stream)
        if not audio_bytes:
            return Failure("ElevenLabs devolvio audio vacio.")
        return Success(audio_bytes)
    except Exception as exc:  # boundary con SDK externo
        logger.error("Fallo la sintesis de voz (TTS)", exc_info=True)
        return Failure(f"Error en la sintesis de voz: {exc}")
