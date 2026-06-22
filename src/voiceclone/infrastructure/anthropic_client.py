"""Cliente de infraestructura para la API de Anthropic (Claude).

Simetrico a ``elevenlabs_client``: encapsula el SDK de Anthropic y traduce
sus excepciones a ``Result[T, str]``. Aisla del resto del proyecto los
detalles del SDK (clase ``Anthropic``, ``TextBlock``, ``messages.create``).
"""

from __future__ import annotations

from anthropic import Anthropic
from anthropic.types import MessageParam, TextBlock
from returns.result import Failure, Result, Success

from voiceclone.infrastructure.logging import get_logger

logger = get_logger(__name__)


def build_client(api_key: str) -> Result[Anthropic, str]:
    """Construye el cliente de Anthropic a partir de la API key."""
    if not api_key.strip():
        return Failure("API key de Anthropic vacia.")
    try:
        return Success(Anthropic(api_key=api_key))
    except Exception as exc:  # boundary con SDK externo
        logger.error("No se pudo inicializar el cliente de Anthropic", exc_info=True)
        return Failure(f"Error al inicializar Anthropic: {exc}")


def _temperature_rechazada(exc: Exception) -> bool:
    """Detecta si el error se debe a que el modelo no acepta 'temperature'.

    Los modelos recientes (p.ej. claude-opus-4-8) deprecaron el parametro y
    responden 400 con un mensaje que menciona 'temperature'.
    """
    return "temperature" in str(exc).lower()


def _create_message(
    client: Anthropic,
    model: str,
    system: str,
    messages: list[MessageParam],
    max_tokens: int,
    temperature: float | None,
) -> str:
    """Llama a la API y extrae el texto. Lanza si el SDK falla (boundary).

    'temperature' se incluye solo cuando no es ``None`` (algunos modelos la
    deprecaron); se usan dos llamadas explicitas para mantener el tipado estricto.
    """
    if temperature is None:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
    else:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages,
        )
    texts = [block.text for block in response.content if isinstance(block, TextBlock)]
    return "\n".join(texts).strip()


def generate_message(
    client: Anthropic,
    model: str,
    system: str,
    messages: list[MessageParam],
    max_tokens: int,
    temperature: float | None = None,
) -> Result[str, str]:
    """Genera una respuesta de Claude y devuelve su texto.

    Args:
        client: Cliente de Anthropic ya inicializado.
        model: Identificador del modelo (p.ej. ``claude-opus-4-8``).
        system: System prompt (la persona).
        messages: Historial en formato de la API de Claude.
        max_tokens: Limite de tokens de la respuesta.
        temperature: Aleatoriedad del muestreo (0.0 a 1.0) o ``None`` para no
            fijarla. Si el modelo la deprecó, se reintenta sin ella.

    Returns:
        ``Success(texto)`` o ``Failure(mensaje)``.
    """
    try:
        reply = _create_message(client, model, system, messages, max_tokens, temperature)
    except Exception as exc:  # boundary con SDK externo
        if temperature is not None and _temperature_rechazada(exc):
            logger.warning(
                "El modelo '%s' no acepta 'temperature'; se reintenta sin ella.", model
            )
            try:
                reply = _create_message(client, model, system, messages, max_tokens, None)
            except Exception as exc2:  # boundary con SDK externo
                logger.error("Fallo la generacion de respuesta con Claude", exc_info=True)
                return Failure(f"Error generando la respuesta: {exc2}")
        else:
            logger.error("Fallo la generacion de respuesta con Claude", exc_info=True)
            return Failure(f"Error generando la respuesta: {exc}")

    if not reply:
        return Failure("Claude no devolvio texto en la respuesta.")
    return Success(reply)
