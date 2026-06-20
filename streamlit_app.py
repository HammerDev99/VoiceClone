"""Interfaz web para que la familia converse con Alexander (memorial).

Punto de entrada para Streamlit (autodetectado por Streamlit Community Cloud).

Ejecutar localmente:
    streamlit run streamlit_app.py
o bien:
    python scripts/06_app_familia.py

Despliegue: ver docs/DESPLIEGUE.md (Streamlit Community Cloud).

Mantiene el historial de cada visitante en su sesión (st.session_state), por lo
que Alexander recuerda el hilo de la conversación. Cada respuesta se muestra en
texto y se reproduce con su voz clonada.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st
from returns.result import Failure, Success

from voiceclone.config.settings import Settings, load_settings
from voiceclone.domain.models import ConversationTurn, VoiceTuning
from voiceclone.domain.persona import alexander_persona
from voiceclone.domain.voice_presets import get_preset, preset_names
from voiceclone.infrastructure import elevenlabs_client as el
from voiceclone.services import conversation, speech_synthesis

ASSISTANT_AVATAR = "🕊️"
USER_AVATAR = "🌿"

# Etiquetas legibles de los presets de voz validados.
PRESET_LABELS = {
    "calido_sereno": "Cálido y sereno",
    "natural": "Natural",
}

# Claves que la app necesita; en la nube llegan por st.secrets, en local por .env.
_ENV_KEYS = (
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_MODEL_ID",
    "ELEVENLABS_OUTPUT_FORMAT",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "VOICE_NAME",
    "VOICE_ID",
    "VOICE_PRESET",
    "LOG_LEVEL",
)


def _bridge_secrets_to_env() -> None:
    """Puente st.secrets -> os.environ.

    En Streamlit Community Cloud no hay archivo .env: los secretos se definen en
    la UI y quedan en ``st.secrets``. Aquí se vuelcan a ``os.environ`` para que
    ``load_settings()`` (agnóstico de Streamlit) los lea igual que en local.
    """
    try:
        available = dict(st.secrets)
    except Exception:  # no hay secrets.toml (ejecución local): se usa .env
        return
    for key in _ENV_KEYS:
        if key not in os.environ and key in available:
            os.environ[key] = str(available[key])


@st.cache_resource(show_spinner=False)
def _load_resources() -> tuple[Settings | None, object | None, str | None]:
    """Carga settings y cliente de ElevenLabs una sola vez (cacheado)."""
    settings_result = load_settings()
    if isinstance(settings_result, Failure):
        return None, None, settings_result.failure()
    settings = settings_result.unwrap()

    client_result = el.build_client(settings.elevenlabs_api_key)
    if isinstance(client_result, Failure):
        return settings, None, client_result.failure()
    return settings, client_result.unwrap(), None


def _render_header() -> None:
    st.set_page_config(page_title="Recordando a Alexander", page_icon="🕊️", layout="centered")
    st.title("🕊️ Recordando a Alexander")
    st.caption(
        "Un espacio para conversar, recordar y sentir su presencia. "
        "Escribe lo que quieras decirle o preguntarle."
    )


def _check_ready(settings: Settings) -> bool:
    """Valida que la conversación pueda funcionar; muestra avisos si no."""
    ok = True
    if not settings.has_anthropic:
        st.error("Falta configurar ANTHROPIC_API_KEY (en .env local o en los secrets del deploy).")
        ok = False
    if not settings.has_voice_id:
        st.error("Aún no hay una voz clonada. Define VOICE_ID (clónala con 02_clonar_voz.py).")
        ok = False
    return ok


def _render_history() -> None:
    for msg in st.session_state.messages:
        avatar = ASSISTANT_AVATAR if msg["role"] == "assistant" else USER_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/mp3")


def _history_turns() -> list[ConversationTurn]:
    """Historial previo (sin el último mensaje del usuario) para Claude."""
    return [
        ConversationTurn(role=m["role"], content=m["content"])
        for m in st.session_state.messages[:-1]
    ]


def _select_voice(settings: Settings) -> VoiceTuning | None:
    """Selector de tono de voz en la barra lateral; devuelve el tuning elegido."""
    nombres = preset_names()
    default_idx = nombres.index(settings.voice_preset) if settings.voice_preset in nombres else 0
    with st.sidebar:
        st.subheader("🎚️ Voz de Alexander")
        elegido = st.selectbox(
            "Tono de la voz",
            nombres,
            index=default_idx,
            format_func=lambda n: PRESET_LABELS.get(n, n),
            key="voice_preset_choice",
            help="Cambia el tono con el que Alexander responde en voz.",
        )
    preset_result = get_preset(elegido)
    return preset_result.unwrap() if isinstance(preset_result, Success) else None


def main() -> None:
    _render_header()
    _bridge_secrets_to_env()

    settings, client, error = _load_resources()
    if error or settings is None:
        st.error(error or "No se pudo cargar la configuración.")
        st.stop()
    if not _check_ready(settings) or client is None:
        st.stop()

    persona = alexander_persona()
    tuning = _select_voice(settings)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    _render_history()

    prompt = st.chat_input("Escribe a Alexander...")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt, "audio": None})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(prompt)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner("Alexander está pensando..."):
            reply_result = conversation.generate_reply(settings, persona, _history_turns(), prompt)
        if isinstance(reply_result, Failure):
            st.error(reply_result.failure())
            st.session_state.messages.pop()  # descarta el turno fallido
            st.stop()
        reply = reply_result.unwrap()
        st.write(reply)

        audio_bytes: bytes | None = None
        with st.spinner("Generando su voz..."):
            audio_result = speech_synthesis.synthesize(
                client, settings, reply, tuning=tuning  # type: ignore[arg-type]
            )
        if isinstance(audio_result, Success):
            audio_bytes = audio_result.unwrap().path.read_bytes()
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        else:
            st.info("(No se pudo generar la voz en este momento; el mensaje sigue disponible.)")

    st.session_state.messages.append({"role": "assistant", "content": reply, "audio": audio_bytes})


main()
