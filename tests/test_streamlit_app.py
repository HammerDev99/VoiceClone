"""Smoke test de la interfaz Streamlit (no hace llamadas de red)."""

from __future__ import annotations

from pathlib import Path

import pytest
from returns.result import Failure, Success
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")


def test_app_arranca_y_muestra_titulo() -> None:
    at = AppTest.from_file(APP_PATH).run(timeout=60)
    # No debe lanzar excepciones al renderizar.
    assert not at.exception
    # El encabezado del memorial siempre se muestra.
    assert any("Alexander" in title.value for title in at.title)


def test_analytics_con_secreto_no_rompe_la_app() -> None:
    at = AppTest.from_file(APP_PATH)
    at.secrets["ANALYTICS_SCRIPT"] = (
        '<script defer src="https://analytics.example.com/script.js" '
        'data-website-id="test-id-123"></script>'
    )
    at.run(timeout=60)
    # La inyección de analítica ocurre antes de validar config; nunca debe romper.
    assert not at.exception


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


def test_muestra_el_motivo_si_falla_la_voz(monkeypatch: pytest.MonkeyPatch) -> None:
    for clave, valor in {
        "ELEVENLABS_API_KEY": "sk_test",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "VOICE_ID": "voice_test",
    }.items():
        monkeypatch.setenv(clave, valor)
    import streamlit as st

    from voiceclone.services import conversation, speech_synthesis

    st.cache_resource.clear()
    monkeypatch.setattr(conversation, "generate_reply", lambda *a, **k: Success("Hola, mi niña."))
    monkeypatch.setattr(
        speech_synthesis,
        "synthesize",
        lambda *a, **k: Failure("Tu plan de ElevenLabs no permite usar voces clonadas."),
    )

    at = AppTest.from_file(APP_PATH)
    at.session_state["consentimiento_dado"] = True
    at.run(timeout=60)
    at.chat_input[0].set_value("Hola").run(timeout=60)
    assert not at.exception
    # El texto de Alexander se muestra igual...
    assert any("Hola, mi niña." in m.value for m in at.markdown)
    # ...y el motivo real de la falla de voz queda visible (no solo el aviso genérico).
    visibles = [c.value for c in at.caption] + [i.value for i in at.info]
    visibles += [w.value for w in at.warning]
    assert any("voces clonadas" in texto for texto in visibles)
