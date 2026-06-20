"""Smoke test de la interfaz Streamlit (no hace llamadas de red)."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")


def test_app_arranca_y_muestra_titulo() -> None:
    at = AppTest.from_file(APP_PATH).run(timeout=60)
    # No debe lanzar excepciones al renderizar.
    assert not at.exception
    # El encabezado del memorial siempre se muestra.
    assert any("Alexander" in title.value for title in at.title)
