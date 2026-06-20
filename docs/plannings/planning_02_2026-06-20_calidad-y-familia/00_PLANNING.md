# Planning 02 — Calidad de voz + Interfaz para la familia

**Fecha**: 2026-06-20
**Origen**: feature request (mejorar tono/calidad de la voz; UI para la familia)
**Objetivo**: (A) Encontrar la mejor calidad de voz de Alexander; (B) interfaz
Streamlit amable para que la familia converse con él sin terminal.
**Metodología**: SDD / CDAID v2

## Alcance

### Fase A — Calidad de voz
| ID | Componente | Archivos | Esfuerzo |
|----|-----------|----------|:--------:|
| A-01 | Re-clonar con 5 muestras `.m4a` | (script 02) | Bajo |
| A-02 | DTO `VoiceTuning` (stability, similarity, style, speed, speaker_boost) | `domain/models.py` | Bajo |
| A-03 | Presets nombrados de voz | `domain/voice_presets.py` | Bajo |
| A-04 | Pasar `VoiceSettings` en TTS | `infrastructure/elevenlabs_client.py` | Bajo |
| A-05 | `synthesize` con tuning opcional + preset por defecto | `services/speech_synthesis.py`, `config/settings.py` | Medio |
| A-06 | Script de calibración (mismo texto × presets) | `scripts/05_calibrar_voz.py` | Bajo |

### Fase B — Interfaz Streamlit
| ID | Componente | Archivos | Esfuerzo |
|----|-----------|----------|:--------:|
| B-01 | App de chat con voz (st.chat + st.audio) | `app/streamlit_app.py` | Medio |
| B-02 | Caché de recursos (clientes) + session_state historial | idem | Bajo |
| B-03 | Config/tema + lanzador | `.streamlit/config.toml`, `scripts/06_app_familia.py` | Bajo |

### Fase C — Verificación
| ID | Componente | Esfuerzo |
|----|-----------|:--------:|
| C-01 | Tests (VoiceTuning, presets, synthesize con tuning) | Medio |
| C-02 | Quality gate + AUDIT_02 | Bajo |

## Decisiones

| Decisión | Elegido | Razón |
|----------|---------|-------|
| Afinado de calidad | `VoiceSettings` + presets comparables | Permite elegir el mejor tono objetivamente |
| Preset por defecto | `calido_sereno` | Tono pausado y afectuoso, apropiado para memorial |
| Interfaz | Streamlit (chat + st.audio) | Rápida, amable, sin terminal; reproduce voz en el navegador |
| Reproducción | `st.audio(autoplay)` | La familia escucha a Alexander directamente |

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Re-clonar duplica voces en la cuenta | Guardar nuevo VOICE_ID; avisar para borrar la anterior |
| Consumo de caracteres en calibración | Texto corto; un archivo por preset |
| Secretos en la UI | Claves desde `.env`, nunca en la UI ni en `secrets` versionados |

## Criterios de éxito

- [ ] Voz re-clonada con 5 muestras (nuevo VOICE_ID).
- [ ] Muestras de calibración generadas para comparar presets.
- [ ] App Streamlit funcional: escribir → leer/escuchar a Alexander.
- [ ] `pytest`/`ruff`/`mypy` limpios; Gate F2 aprobado.
