# Auditoría #02 — Gate F2: Calidad de voz + Interfaz para la familia

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-06-20 |
| **Fase evaluada** | F2: afinado de voz (presets) + interfaz Streamlit + despliegue |
| **Instrumentos** | pytest+cov, ruff, mypy --strict, AppTest (Streamlit), validación a oído |
| **Baseline** | 55 tests (post F1) |
| **Post-corrección** | 69 tests, ruff 0, mypy 0 |
| **Tasa SDD** | 100% (meta ≥85%) |
| **Veredicto** | ✅ APROBADO |

## 1. Checklist de Gate

### Funcional
- [x] Re-clonado con 5 muestras `.m4a` (nuevo VOICE_ID `A1w42DVwDu80oNyR6BeL`).
- [x] `VoiceSettings` aplicado en TTS (stability, similarity, style, speed, speaker_boost).
- [x] Presets comparables vía `scripts/05_calibrar_voz.py`.
- [x] Selección a oído: se conservan `calido_sereno` y `natural`; se descartan
      `estable` y `expresivo` (perdían fidelidad del timbre).
- [x] Interfaz Streamlit: chat + voz + historial con contexto (st.session_state).
- [x] Smoke test de la app (AppTest) sin excepciones.

### Seguridad
- [x] Puente `st.secrets → os.environ` sin exponer claves en la UI ni en el repo.
- [x] `.streamlit/secrets.toml` gitignored; solo se versiona `.example`.
- [x] Sin secretos hardcodeados.

### Calidad
- [x] `pytest` → 69 passed. `ruff` 0. `mypy --strict` 0 (18 archivos).

### Arquitectura
- [x] `VoiceTuning` DTO frozen; presets en dominio con `Result`.
- [x] La app Streamlit es presentación pura; reutiliza servicios sin duplicar lógica.
- [x] `synthesize` extendido (tuning + output_path) sin romper llamadas previas.

## 2. Conformidad SDD (8 Puntos)

| Clasificación | Cantidad |
|--------------|:--------:|
| CONFORME | 8 |
| DEFECTO | 0 |
| **Tasa** | **100%** |

Reutiliza los patrones validados en AUDIT_01 (DI, Result, frozen DTOs, boundaries
de SDK). El cliente Anthropic/ElevenLabs sigue encapsulado en `infrastructure/`.

## 3. Reportes de Instrumentos

### 3.1 Calidad de voz (validación a oído del usuario)
Se generaron 4 muestras con el mismo texto. El usuario evaluó:
- **Mejores** (conservan la realidad de la voz): `calido_sereno`, `natural`.
- **Descartados** (pierden fidelidad): `estable`, `expresivo` → eliminados del código.

### 3.2 ruff / mypy / pytest
69 tests verdes; nuevos tests: `test_voice_presets.py`, ampliación de
`test_speech_synthesis.py` (tuning, output_path), `test_streamlit_app.py` (smoke).

### 3.3 Streamlit (AppTest)
La app arranca y muestra el encabezado sin excepción; sin llamadas de red en el test.

## 4. Correcciones Aplicadas

| # | ID | Cambio | Test |
|---|-----|--------|:----:|
| 1 | A-02..05 | `VoiceTuning` + `VoiceSettings` en TTS + tuning en synthesize | +8 |
| 2 | A-06 | Script de calibración por presets | (CLI) |
| 3 | B-01..03 | App Streamlit + lanzador + tema | +1 (smoke) |
| 4 | C-AJUSTE | Conservar solo presets validados (calido_sereno, natural) | actualizado |

## 5. Hallazgos Diferidos (backlog)

| ID | Hallazgo | Sprint |
|----|----------|:------:|
| D-03 | Borrar de la cuenta las voces antiguas (3 audios) | manual |
| D-04 | Streaming token a token (st.write_stream) en la UI | F3 |
| D-05 | Despliegue efectivo en Streamlit Cloud (requiere repo GitHub) | usuario |

## 6. Veredicto

✅ **APROBADO**. Calidad de voz mejorada (5 muestras + presets validados a oído),
interfaz para la familia funcional y lista para desplegar en Streamlit Community
Cloud. 69 tests, ruff/mypy limpios, tasa SDD 100%.
