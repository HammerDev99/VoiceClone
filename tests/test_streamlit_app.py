"""Smoke test de la interfaz Streamlit (no hace llamadas de red)."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")


def test_app_arranca_y_muestra_titulo() -> None:
    at = AppTest.from_file(APP_PATH).run(timeout=60)
    # No debe lanzar excepciones al renderizar.
    assert not at.exception
    # El encabezado del memorial siempre se muestra.
    assert any("Alexander" in title.value for title in at.title)


def test_consent_gate_oculta_el_chat_hasta_aceptar(monkeypatch: pytest.MonkeyPatch) -> None:
    # Claves de prueba para que _check_ready pase de forma determinista (sin red).
    for clave, valor in {
        "ELEVENLABS_API_KEY": "sk_test",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "VOICE_ID": "voice_test",
    }.items():
        monkeypatch.setenv(clave, valor)
    import streamlit as st

    st.cache_resource.clear()  # evita arrastrar settings cacheadas de otro test

    at = AppTest.from_file(APP_PATH).run(timeout=60)
    assert not at.error
    # Antes de consentir no hay caja de chat, pero sí el checkbox de transparencia.
    assert len(at.chat_input) == 0
    assert len(at.checkbox) >= 1
    # Al marcar el checkbox aparece el botón de entrada (render condicional).
    at.checkbox[0].check().run(timeout=60)
    at.button[0].click().run(timeout=60)
    # Tras aceptar, el chat queda disponible y sin excepciones.
    assert not at.exception
    assert len(at.chat_input) == 1
