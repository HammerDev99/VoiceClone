"""Carga y validacion de la configuracion desde ``.env``.

Expone ``load_settings()`` que devuelve un ``Result[Settings, str]``:
- ``Success(Settings)`` si la configuracion minima es valida.
- ``Failure(mensaje)`` si falta algo critico (p.ej. la API key de ElevenLabs).

La API key de Anthropic es opcional a este nivel: solo el servicio de
conversacion la exige, y valida su presencia cuando se usa.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from returns.result import Failure, Result, Success

from voiceclone.domain.voice_presets import DEFAULT_PRESET

# Raiz del proyecto = dos niveles arriba de este archivo (src/voiceclone/config).
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = PROJECT_ROOT / ".env"

# Temperatura del muestreo de Claude. Es OPCIONAL: por defecto no se fija (None) y
# no se envia a la API. Motivo: los modelos recientes (p.ej. claude-opus-4-8)
# DEPRECARON 'temperature' y devuelven 400 si se envia. Solo se usa si el usuario
# la define explicitamente en ANTHROPIC_TEMPERATURE y el modelo la soporta.
# Rango valido de la API cuando aplica: 0.0 a 1.0.


@dataclass(frozen=True)
class Settings:
    """Configuracion inmutable del proyecto."""

    elevenlabs_api_key: str
    elevenlabs_model_id: str
    elevenlabs_output_format: str
    anthropic_api_key: str
    anthropic_model: str
    anthropic_temperature: float | None
    voice_name: str
    voice_id: str | None
    voice_preset: str
    audio_input_dir: Path
    audio_output_dir: Path
    log_level: str

    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_voice_id(self) -> bool:
        return bool(self.voice_id)


def _resolve_dir(raw: str) -> Path:
    """Resuelve una ruta relativa contra la raiz del proyecto."""
    path = Path(raw)
    return path if path.is_absolute() else (PROJECT_ROOT / path)


def _parse_temperature(raw: str | None) -> float | None:
    """Convierte el valor de entorno a float acotado a [0.0, 1.0], o ``None``.

    Devuelve ``None`` (no fijar temperature) cuando la variable esta ausente,
    vacia o no es numerica. Asi, por defecto no se envia 'temperature' a la API
    y se evita el 400 de los modelos que la deprecaron; un valor explicito y
    valido se respeta (acotado al rango permitido).
    """
    if raw is None or not raw.strip():
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return max(0.0, min(1.0, value))


def load_settings(env_path: Path = ENV_PATH) -> Result[Settings, str]:
    """Carga la configuracion desde ``.env`` y valida lo minimo indispensable.

    Args:
        env_path: Ruta al archivo ``.env`` (por defecto, en la raiz).

    Returns:
        ``Success(Settings)`` o ``Failure(mensaje de error claro)``.
    """
    load_dotenv(dotenv_path=env_path, override=False)

    elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not elevenlabs_api_key:
        return Failure(
            "Falta ELEVENLABS_API_KEY. Copia .env.example a .env y completa la clave. "
            f"(.env esperado en: {env_path})"
        )

    voice_id_raw = os.environ.get("VOICE_ID", "").strip()

    settings = Settings(
        elevenlabs_api_key=elevenlabs_api_key,
        elevenlabs_model_id=os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        elevenlabs_output_format=os.environ.get("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip(),
        anthropic_model=os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8"),
        anthropic_temperature=_parse_temperature(os.environ.get("ANTHROPIC_TEMPERATURE")),
        voice_name=os.environ.get("VOICE_NAME", "Alexander").strip() or "Alexander",
        voice_id=voice_id_raw or None,
        voice_preset=os.environ.get("VOICE_PRESET", DEFAULT_PRESET).strip() or DEFAULT_PRESET,
        audio_input_dir=_resolve_dir(os.environ.get("AUDIO_INPUT_DIR", "audios")),
        audio_output_dir=_resolve_dir(os.environ.get("AUDIO_OUTPUT_DIR", "output")),
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    )
    return Success(settings)


def save_voice_id(voice_id: str, env_path: Path = ENV_PATH) -> Result[None, str]:
    """Persiste el ``VOICE_ID`` en el ``.env`` para reutilizar la voz clonada.

    Reescribe la linea ``VOICE_ID=`` si existe; si no, la agrega al final.

    Args:
        voice_id: Identificador de la voz devuelto por ElevenLabs.
        env_path: Ruta al ``.env``.

    Returns:
        ``Success(None)`` o ``Failure(mensaje)``.
    """
    if not voice_id.strip():
        return Failure("voice_id vacio; no se persiste.")

    try:
        lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
        new_line = f"VOICE_ID={voice_id}"
        replaced = False
        for i, line in enumerate(lines):
            if line.strip().startswith("VOICE_ID="):
                lines[i] = new_line
                replaced = True
                break
        if not replaced:
            lines.append(new_line)
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return Success(None)
    except OSError as exc:
        return Failure(f"No se pudo escribir VOICE_ID en {env_path}: {exc}")
