#!/usr/bin/env python
"""Paso 6: lanza la interfaz web para la familia (Streamlit).

Abre una página en el navegador donde la familia puede conversar con Alexander
sin usar la terminal.

Uso:
    python scripts/06_app_familia.py
(equivale a:  streamlit run streamlit_app.py)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).resolve().parent.parent / "streamlit_app.py"
    raise SystemExit(
        subprocess.call([sys.executable, "-m", "streamlit", "run", str(app_path)])
    )
