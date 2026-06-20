#!/usr/bin/env python
"""Paso 4: conversa con la persona de Alexander (Claude) y escucha su voz.

Requiere ANTHROPIC_API_KEY y una voz ya clonada (VOICE_ID en .env).

Uso:
    python scripts/04_conversar.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from voiceclone.cli.main import cmd_converse

if __name__ == "__main__":
    raise SystemExit(cmd_converse())
