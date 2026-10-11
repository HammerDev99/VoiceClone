#!/usr/bin/env python
"""Paso 0: diagnostico capa por capa (configuracion -> Claude -> ElevenLabs -> voz -> TTS).

A diferencia de 01_verificar_conexion.py, aqui SI se hace una llamada real a Claude
con el modelo configurado y una sintesis minima con la voz clonada, para ver el
error exacto de cada servicio. No modifica nada; solo imprime evidencia.

Uso:
    python scripts/00_diagnostico.py
Lee las claves de .env (local) o de las variables de entorno. Nunca imprime claves.
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from returns.result import Failure

from voiceclone.config.settings import Settings, load_settings
from voiceclone.domain.models import SpeechRequest
from voiceclone.infrastructure import anthropic_client as ac
from voiceclone.infrastructure import elevenlabs_client as el


def _mask(value: str) -> str:
    if len(value) <= 12:
        return "(muy corta)"
    return f"{value[:6]}...{value[-4:]} ({len(value)} chars)"


def _describe(exc: BaseException) -> str:
    """Resume un error de SDK: tipo, status HTTP y cuerpo si existen."""
    status = getattr(exc, "status_code", None)
    body = getattr(exc, "body", None)
    if status is not None or body is not None:
        return f"{type(exc).__name__} status={status} body={str(body)[:300]}"
    return f"{type(exc).__name__}: {str(exc)[:300]}"


def _step(ok: bool, label: str, detail: str = "") -> None:
    estado = "OK   " if ok else "FALLA"
    print(f"  [{estado}] {label}" + (f": {detail}" if detail else ""))


def _print_versions() -> bool:
    print(f"python {sys.version.split()[0]}")
    try:
        import anthropic
        import elevenlabs

        print(
            f"anthropic {anthropic.__version__} | "
            f"elevenlabs {getattr(elevenlabs, '__version__', '?')}"
        )
    except Exception as exc:  # solo diagnostico
        _step(False, "importar SDKs", repr(exc))
        return False
    return True


def _check_config(s: Settings) -> None:
    print("\n1) Configuracion")
    _step(True, "ELEVENLABS_API_KEY", _mask(s.elevenlabs_api_key))
    _step(
        bool(s.anthropic_api_key),
        "ANTHROPIC_API_KEY",
        _mask(s.anthropic_api_key) if s.anthropic_api_key else "ausente",
    )
    _step(True, "ANTHROPIC_MODEL", s.anthropic_model)
    _step(bool(s.voice_id), "VOICE_ID", s.voice_id or "ausente")
    formato = f"{s.elevenlabs_model_id} / {s.elevenlabs_output_format}"
    _step(True, "ELEVENLABS_MODEL_ID / formato", formato)
    _step(True, "VOICE_PRESET", s.voice_preset)


def _check_claude(s: Settings) -> bool:
    print("\n2) Claude (Anthropic)")
    if not s.anthropic_api_key:
        _step(False, "sin ANTHROPIC_API_KEY; se omite")
        return False
    client_result = ac.build_client(s.anthropic_api_key)
    if isinstance(client_result, Failure):
        _step(False, "build_client", client_result.failure())
        return False
    client = client_result.unwrap()
    ok = True
    try:
        info = client.models.retrieve(s.anthropic_model)
        _step(True, "modelo disponible", f"{info.id} ({getattr(info, 'display_name', '')})")
    except Exception as exc:  # boundary con SDK externo
        _step(False, "models.retrieve", _describe(exc))
        ok = False
    t0 = time.time()
    reply = ac.generate_message(
        client,
        s.anthropic_model,
        "Responde con una sola palabra.",
        [{"role": "user", "content": "Di: hola"}],
        20,
    )
    if isinstance(reply, Failure):
        _step(False, "messages.create", reply.failure()[:400])
        return False
    _step(True, "messages.create", f"'{reply.unwrap()[:40]}' en {time.time() - t0:.1f}s")
    return ok


def _check_elevenlabs(s: Settings) -> bool:
    print("\n3) ElevenLabs")
    client_result = el.build_client(s.elevenlabs_api_key)
    if isinstance(client_result, Failure):
        _step(False, "build_client", client_result.failure())
        return False
    client = client_result.unwrap()
    ok = True

    try:
        sub = client.user.subscription.get()
        ivc = "si" if getattr(sub, "can_use_instant_voice_cloning", True) else "NO"
        _step(
            True,
            "cuenta",
            f"plan={sub.tier}, caracteres {sub.character_count}/{sub.character_limit}, IVC={ivc}",
        )
    except Exception as exc:  # boundary con SDK externo
        _step(False, "user.subscription.get", el.describe_error(exc))
        ok = False

    found = False
    try:
        voices = client.voices.get_all().voices
        names = ", ".join(f"{v.name}={v.voice_id}" for v in voices[:10])
        _step(True, "voces en la cuenta", f"{len(voices)}: {names}")
        if s.voice_id:
            found = any(v.voice_id == s.voice_id for v in voices)
            detail = s.voice_id if found else f"{s.voice_id} NO existe (¿se elimino la voz?)"
            _step(found, "VOICE_ID presente en la cuenta", detail)
            ok = ok and found
    except Exception as exc:  # boundary con SDK externo
        _step(False, "voices.get_all", el.describe_error(exc))
        ok = False

    print("\n4) Sintesis minima con la voz configurada (misma ruta que la app)")
    if not s.voice_id:
        _step(False, "sin VOICE_ID; se omite")
        return False
    t0 = time.time()
    request = SpeechRequest(
        text="Hola.",
        voice_id=s.voice_id,
        model_id=s.elevenlabs_model_id,
        output_format=s.elevenlabs_output_format,
        tuning=None,
    )
    audio = el.text_to_speech(client, request)
    if isinstance(audio, Failure):
        try:  # repetir la llamada directa (y consumir el stream) para ver status y cuerpo
            b"".join(
                client.text_to_speech.convert(
                    voice_id=s.voice_id,
                    text="Hola.",
                    model_id=s.elevenlabs_model_id,
                    output_format=s.elevenlabs_output_format,
                )
            )
            _step(False, "text_to_speech", audio.failure()[:300])
        except Exception as exc:  # boundary con SDK externo
            _step(False, "text_to_speech.convert", el.describe_error(exc))
        return False
    _step(True, "text_to_speech", f"{len(audio.unwrap())} bytes en {time.time() - t0:.1f}s")
    return ok


def _silenciar_logs() -> None:
    """Solo se muestran las lineas de resultado; los errores ya se explican en cada paso."""
    for name in ("voiceclone", "httpx", "httpx2", "anthropic", "elevenlabs"):
        logging.getLogger(name).setLevel(logging.CRITICAL)


def main() -> int:
    print("== Diagnostico VoiceClone ==")
    _silenciar_logs()
    if not _print_versions():
        return 1
    settings_result = load_settings()
    if isinstance(settings_result, Failure):
        print("\n1) Configuracion")
        _step(False, "load_settings", settings_result.failure())
        return 1
    s = settings_result.unwrap()
    _check_config(s)
    claude_ok = _check_claude(s)
    eleven_ok = _check_elevenlabs(s)
    todo_ok = claude_ok and eleven_ok
    print("\n== Resultado:", "todo OK ==" if todo_ok else "hay fallas (ver arriba) ==")
    return 0 if todo_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
