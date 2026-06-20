#!/usr/bin/env python
"""Paso 1: verifica la conexion con ElevenLabs (y Claude) y muestra el estado.

Uso:
    python scripts/01_verificar_conexion.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voiceclone.cli.main import cmd_verify

if __name__ == "__main__":
    raise SystemExit(cmd_verify())
