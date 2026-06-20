#!/usr/bin/env python
"""Paso 3: genera un audio (TTS) con la voz clonada.

Uso:
    python scripts/03_generar_voz.py "Texto a convertir en voz"

Si no se pasa texto, usa un mensaje de ejemplo.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voiceclone.cli.main import cmd_generate

_DEFAULT_TEXT = "Hola, soy Alexander. Gracias por recordarme."

if __name__ == "__main__":
    texto = " ".join(sys.argv[1:]).strip() or _DEFAULT_TEXT
    raise SystemExit(cmd_generate(texto))
