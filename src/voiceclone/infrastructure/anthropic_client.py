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


def generate_message(
    client: Anthropic,
    model: str,
    system: str,
    messages: list[MessageParam],
    max_tokens: int,
    temperature: float,
) -> Result[str, str]:
    """Genera una respuesta de Claude y devuelve su texto.

    Args:
        client: Cliente de Anthropic ya inicializado.
        model: Identificador del modelo (p.ej. ``claude-opus-4-8``).
        system: System prompt (la persona).
        messages: Historial en formato de la API de Claude.
        max_tokens: Limite de tokens de la respuesta.
        temperature: Aleatoriedad del muestreo (0.0 a 1.0). Valores bajos
            reducen la alucinacion de recuerdos y la sycophancy.

    Returns:
        ``Success(texto)`` o ``Failure(mensaje)``.
    """
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages,
        )
        texts = [block.text for block in response.content if isinstance(block, TextBlock)]
        reply = "\n".join(texts).strip()
        if not reply:
            return Failure("Claude no devolvio texto en la respuesta.")
        return Success(reply)
    except Exception as exc:  # boundary con SDK externo
        logger.error("Fallo la generacion de respuesta con Claude", exc_info=True)
        return Failure(f"Error generando la respuesta: {exc}")
