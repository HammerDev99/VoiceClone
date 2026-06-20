# Sprint 02 — Calidad de voz + Interfaz para la familia

**Fecha inicio**: 2026-06-20
**Objetivo**: Mejorar el tono/calidad de la voz de Alexander y dar a la familia
una interfaz amable (Streamlit) para conversar con él.
**Planning**: `docs/plannings/planning_02_2026-06-20_calidad-y-familia/`
**Metodología**: SDD / CDAID v2

## Estado General

```
Sprint 02: [████████████████████] 100% (12/12 SPECs)
```

| Fase | Total | Completados |
|------|:-----:|:-----------:|
| A — Calidad de voz | 6 | 6 |
| B — Interfaz Streamlit | 3 | 3 |
| C — Verificación | 3 | 3 |

## Registro de Progreso

| Fecha | SPEC | Descripción | Tests |
|-------|------|-------------|:-----:|
| 06-20 | A-01 | Re-clonado con 5 muestras (VOICE_ID A1w42DVwDu80oNyR6BeL) | — |
| 06-20 | A-02 | DTO VoiceTuning | (cubierto) |
| 06-20 | A-03 | Presets de voz | +8 |
| 06-20 | A-04 | VoiceSettings en TTS | +2 |
| 06-20 | A-05 | synthesize con tuning + output_path | +2 |
| 06-20 | A-06 | Script de calibración | (CLI) |
| 06-20 | B-01 | App Streamlit (chat + voz + historial) | +1 |
| 06-20 | B-02 | Caché de recursos + puente st.secrets | — |
| 06-20 | B-03 | Tema + lanzador (script 06) | — |
| 06-20 | C-01 | Tests nuevos | 71 → ajuste |
| 06-20 | C-02 | Quality gate + AUDIT_02 | — |
| 06-20 | C-03 | Selección a oído de presets | 69 final |

## Métricas de Verificación

| Métrica | Pre | Post | Δ |
|---------|:---:|:----:|:-:|
| Tests | 55 | 69 | +14 |
| ruff | 0 | 0 | = |
| mypy | 0 | 0 | = |

## Decisiones Tomadas

| # | Decisión | Razón |
|---|----------|-------|
| 1 | Re-clonar con 5 audios | Más material → mejor fidelidad del clon |
| 2 | Presets comparables + elegir a oído | Calidad es subjetiva; comparar es lo objetivo |
| 3 | Conservar solo calido_sereno y natural | estable/expresivo perdían realidad de la voz |
| 4 | Streamlit + Community Cloud | Patrón conocido del usuario (disciplinajudicialai) |
| 5 | Puente st.secrets → os.environ | Misma config en local (.env) y nube (secrets) |
| 6 | Entrypoint streamlit_app.py en la raíz | Autodetectado por Streamlit Cloud |

## Trazas de Delegación

| Decisión | Propuesta IA | Aprobación Humano |
|----------|-------------|-------------------|
| Presets de afinado | 4 presets propuestos | Usuario eligió 2 (calido_sereno, natural) |
| Interfaz | Streamlit recomendado | Confirmado por el usuario |
| Despliegue | Community Cloud (patrón de referencia) | Indicado por el usuario |

## Resultado

Gate F2 **APROBADO** (`docs/validate/AUDIT_02_2026-06-20_GATE_F2_CALIDAD_UI.md`).
Pendiente del usuario: desplegar en Streamlit Cloud (ver `docs/DESPLIEGUE.md`).
