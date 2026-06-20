"""Servicio de conversacion: genera respuestas con la persona via Claude.

Orquesta la capa de infraestructura de Anthropic. No depende del SDK
directamente (eso vive en ``infrastructure/anthropic_client``), lo que
mantiene la simetria con el servicio de voz y facilita el testeo.
"""

from __future__ import annotations

from anthropic.types import MessageParam
from returns.result import Failure, Result

from voiceclone.config.settings import Settings
from voiceclone.domain.models import ConversationTurn
from voiceclone.domain.persona import Persona
from voiceclone.infrastructure import anthropic_client as ac
from voiceclone.infrastructure.logging import get_logger

logger = get_logger(__name__)

MAX_REPLY_TOKENS = 400


def _to_message_params(history: list[ConversationTurn], user_message: str) -> list[MessageParam]:
    """Convierte el historial + mensaje nuevo al formato de la API de Claude."""
    messages: list[MessageParam] = [
        {"role": turn.role, "content": turn.content}  # type: ignore[typeddict-item]
        for turn in history
    ]
    messages.append({"role": "user", "content": user_message})
    return messages


def generate_reply(
    settings: Settings,
    persona: Persona,
    history: list[ConversationTurn],
    user_message: str,
) -> Result[str, str]:
    """Genera la respuesta de la persona ante el mensaje del usuario.

    Args:
        settings: Configuracion (incluye API key y modelo de Anthropic).
        persona: Personalidad que guia la respuesta (system prompt).
        history: Turnos previos de la conversacion.
        user_message: Mensaje actual del usuario.

    Returns:
        ``Success(texto de la respuesta)`` o ``Failure(mensaje)``.
    """
    clean = user_message.strip()
    if not clean:
        return Failure("El mensaje del usuario esta vacio.")
    if not settings.has_anthropic:
        return Failure("Falta ANTHROPIC_API_KEY en .env. Es necesaria para la conversacion.")

    client_result = ac.build_client(settings.anthropic_api_key)
    if isinstance(client_result, Failure):
        return client_result
    client = client_result.unwrap()

    return ac.generate_message(
        client=client,
        model=settings.anthropic_model,
        system=persona.system_prompt,
        messages=_to_message_params(history, clean),
        max_tokens=MAX_REPLY_TOKENS,
    )
