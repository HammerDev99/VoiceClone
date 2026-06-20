"""Comandos de la CLI: verificar, clonar, generar y conversar.

Cada funcion ``cmd_*`` orquesta servicios y devuelve un codigo de salida
(0 = exito, 1 = error). Los scripts de ``scripts/`` son finos envoltorios
que invocan estas funciones.
"""

from __future__ import annotations

from elevenlabs.client import ElevenLabs
from returns.result import Failure, Result, Success

from voiceclone.cli import console
from voiceclone.config.settings import Settings, load_settings
from voiceclone.domain.models import ConversationTurn
from voiceclone.domain.persona import alexander_persona
from voiceclone.domain.voice_presets import get_preset, preset_names
from voiceclone.infrastructure import elevenlabs_client as el
from voiceclone.services import conversation, speech_synthesis, voice_cloning

_EXIT_WORDS = frozenset({"salir", "exit", "quit", "adios", "chau"})


def _setup() -> Result[tuple[Settings, ElevenLabs], str]:
    """Carga la configuracion y construye el cliente de ElevenLabs.

    Centraliza el arranque comun a todos los comandos (evita duplicacion).
    """
    settings_result = load_settings()
    if isinstance(settings_result, Failure):
        return Failure(settings_result.failure())
    settings = settings_result.unwrap()

    client_result = el.build_client(settings.elevenlabs_api_key)
    if isinstance(client_result, Failure):
        return Failure(client_result.failure())

    return Success((settings, client_result.unwrap()))


def cmd_verify() -> int:
    """Verifica las credenciales y muestra el estado de la cuenta."""
    console.heading("Verificacion de conexion")
    setup = _setup()
    if isinstance(setup, Failure):
        console.error(setup.failure())
        return 1
    settings, client = setup.unwrap()

    info_result = el.get_account_info(client)
    if isinstance(info_result, Failure):
        console.error(info_result.failure())
        return 1
    account = info_result.unwrap()
    console.success(f"ElevenLabs conectado. Plan: {account.tier}")
    console.info(
        f"    Caracteres: {account.characters_used}/{account.characters_limit} "
        f"(disponibles: {account.characters_remaining})"
    )
    if account.can_clone_ivc:
        console.success("Tu plan permite Instant Voice Cloning (IVC).")
    else:
        console.warn("Tu plan NO permite IVC. Necesitas plan Starter o superior.")

    voices_result = el.list_voices(client)
    if isinstance(voices_result, Failure):
        console.warn(voices_result.failure())
    else:
        voices = voices_result.unwrap()
        console.info(f"    Voces en la cuenta: {len(voices)}")
        if settings.has_voice_id:
            match = next((v for v in voices if v.voice_id == settings.voice_id), None)
            if match:
                console.success(f"Voz '{match.name}' lista (VOICE_ID={match.voice_id})")
            else:
                console.warn(f"VOICE_ID={settings.voice_id} no aparece en la cuenta.")
        else:
            console.info("    Aun no hay voz clonada (ejecuta 02_clonar_voz.py).")

    if settings.has_anthropic:
        console.success("Anthropic (Claude) configurado para la conversacion.")
    else:
        console.warn("ANTHROPIC_API_KEY no configurada (necesaria para 04_conversar.py).")
    return 0


def cmd_clone() -> int:
    """Clona la voz 'Alexander' a partir de las muestras en audios/."""
    console.heading("Clonado de voz (Instant Voice Cloning)")
    setup = _setup()
    if isinstance(setup, Failure):
        console.error(setup.failure())
        return 1
    settings, client = setup.unwrap()

    console.info(f"Clonando '{settings.voice_name}' desde: {settings.audio_input_dir}")
    clone_result = voice_cloning.clone_voice(client, settings)
    if isinstance(clone_result, Failure):
        console.error(clone_result.failure())
        return 1
    cloned = clone_result.unwrap()
    console.success(f"Voz creada: {cloned.name}")
    console.info(f"    VOICE_ID = {cloned.voice_id}  (guardado en .env)")
    console.info('    Pruebala con:  python scripts/03_generar_voz.py "Hola, soy Alexander"')
    return 0


def cmd_generate(text: str) -> int:
    """Genera un audio (TTS) con la voz clonada a partir de ``text``."""
    console.heading("Generacion de voz (TTS)")
    setup = _setup()
    if isinstance(setup, Failure):
        console.error(setup.failure())
        return 1
    settings, client = setup.unwrap()

    result = speech_synthesis.synthesize(client, settings, text)
    if isinstance(result, Failure):
        console.error(result.failure())
        return 1
    generated = result.unwrap()
    console.success(f"Audio generado: {generated.path}")
    console.info(f"    {generated.bytes_written} bytes")
    return 0


def cmd_calibrate(text: str) -> int:
    """Genera el mismo texto con cada preset para comparar la calidad."""
    console.heading("Calibracion de voz (comparar presets)")
    setup = _setup()
    if isinstance(setup, Failure):
        console.error(setup.failure())
        return 1
    settings, client = setup.unwrap()

    if not settings.has_voice_id:
        console.error("No hay VOICE_ID. Clona la voz primero (02_clonar_voz.py).")
        return 1

    out_dir = settings.audio_output_dir / "calibracion"
    console.info(f"Generando {len(preset_names())} muestras en: {out_dir}")
    for name in preset_names():
        tuning = get_preset(name).unwrap()
        destino = out_dir / f"calibracion_{name}.mp3"
        result = speech_synthesis.synthesize(
            client, settings, text, tuning=tuning, output_path=destino
        )
        if isinstance(result, Failure):
            console.warn(f"{name}: {result.failure()}")
        else:
            console.success(f"{name:14s} -> {result.unwrap().path.name}")
    console.info("\nEscucha las muestras y elige tu preferida.")
    console.info("Luego fija VOICE_PRESET=<preset> en .env.")
    return 0


def cmd_converse() -> int:
    """Conversacion interactiva con la persona (Claude) y su voz."""
    console.heading("Conversacion con Alexander")
    setup = _setup()
    if isinstance(setup, Failure):
        console.error(setup.failure())
        return 1
    settings, client = setup.unwrap()

    if not settings.has_anthropic:
        console.error("Falta ANTHROPIC_API_KEY en .env (necesaria para conversar).")
        return 1
    if not settings.has_voice_id:
        console.error("No hay VOICE_ID. Clona la voz primero (02_clonar_voz.py).")
        return 1

    persona = alexander_persona()
    history: list[ConversationTurn] = []
    console.info("Escribe un mensaje. Para terminar: 'salir'.")

    while True:
        try:
            user_message = input("\nTu: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.info("\nHasta pronto.")
            return 0
        if not user_message:
            continue
        if user_message.lower() in _EXIT_WORDS:
            console.info("Hasta pronto.")
            return 0

        reply_result = conversation.generate_reply(settings, persona, history, user_message)
        if isinstance(reply_result, Failure):
            console.error(reply_result.failure())
            continue
        reply = reply_result.unwrap()
        console.say(persona.name, reply)

        audio_result = speech_synthesis.synthesize(client, settings, reply)
        if isinstance(audio_result, Failure):
            console.warn(f"No se pudo generar el audio: {audio_result.failure()}")
        else:
            console.info(f"    (voz: {audio_result.unwrap().path})")

        history = [
            *history,
            ConversationTurn(role="user", content=user_message),
            ConversationTurn(role="assistant", content=reply),
        ]
