# project_status.md — Estado actual

> Nivel 2. Informativo. Actualizado: 2026-06-20.

## Resumen

```
F1 Núcleo (clonado·TTS·conversación):           [████████████████████] 100% ✅ APROBADO
F2 Calidad de voz + interfaz familia:           [████████████████████] 100% ✅ APROBADO
Despliegue en Streamlit Cloud:                  [████████░░░░░░░░░░░░] pendiente del usuario
```

## Fase CDAID actual

**Gate F2 aprobado** (`docs/validate/AUDIT_02`). Voz mejorada y app lista para la
familia. Falta el despliegue efectivo en Streamlit Community Cloud.

## Hecho

- [x] Sprint 01: núcleo (config, dominio, infra, servicios, CLI, scripts 01-04).
- [x] Sprint 02: afinado de voz (presets), calibración, interfaz Streamlit, despliegue.
- [x] Voz re-clonada con 5 muestras: `VOICE_ID=A1w42DVwDu80oNyR6BeL`.
- [x] Presets validados a oído: `calido_sereno` (defecto) y `natural`.
- [x] App Streamlit (`streamlit_app.py`) con chat + voz + historial.
- [x] 69 tests, ruff 0, mypy 0.
- [x] Auditorías F1 y F2 aprobadas (tasa SDD 100%).

## Pendiente del usuario

- [ ] Elegir/confirmar preset final en `.env` (`VOICE_PRESET`).
- [ ] Desplegar en Streamlit Community Cloud (ver `docs/DESPLIEGUE.md`):
      subir a GitHub, crear app, configurar secrets.
- [ ] Rotar las API keys de ElevenLabs y Anthropic (compartidas en el chat).
- [ ] (Opcional) Borrar de la cuenta ElevenLabs las voces antiguas (3 muestras).

## Backlog (diferido)

- Streaming token a token en la UI (`st.write_stream`).
- Reproducción/descarga avanzada; gestión de voces (borrar/editar).
- Tests `@pytest.mark.integration` contra APIs reales.

## Métricas

| Tests | ruff | mypy | Tasa SDD | Gates |
|:-----:|:----:|:----:|:--------:|:-----:|
| 69 | 0 | 0 | 100% | F1, F2 ✅ |

## Flujo de scripts

```
01_verificar_conexion → 02_clonar_voz → 03_generar_voz → 05_calibrar_voz
04_conversar (terminal)            06_app_familia (interfaz web Streamlit)
```
