#!/usr/bin/env python
"""Paso 2: clona la voz 'Alexander' desde las muestras .m4a en audios/.

Guarda el VOICE_ID resultante en .env para reutilizarlo.

Uso:
    python scripts/02_clonar_voz.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voiceclone.cli.main import cmd_clone

if __name__ == "__main__":
    raise SystemExit(cmd_clone())
