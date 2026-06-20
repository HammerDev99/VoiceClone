#!/usr/bin/env python
"""Paso 5 (opcional): genera el mismo texto con cada preset de voz para comparar.

Crea un archivo por preset en output/calibracion/ para que elijas a oido la
mejor calidad. Luego fija VOICE_PRESET=<preset> en .env.

Uso:
    python scripts/05_calibrar_voz.py "Texto de prueba"
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voiceclone.cli.main import cmd_calibrate

_DEFAULT_TEXT = (
    "Hola, soy Alexander. Gracias por estar aqui y por recordarme con tanto carino."
)

if __name__ == "__main__":
    texto = " ".join(sys.argv[1:]).strip() or _DEFAULT_TEXT
    raise SystemExit(cmd_calibrate(texto))
