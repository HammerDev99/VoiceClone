# project_status.md — Estado actual

> Nivel 2. Informativo. Actualizado: 2026-06-20.

## Resumen

```
F1 Núcleo (clonado·TTS·conversación):           [████████████████████] 100% ✅ APROBADO
F2 Calidad de voz + interfaz familia:           [████████████████████] 100% ✅ APROBADO
Despliegue en Streamlit Cloud:                  [████████████████████] 100% ✅ DESPLEGADO
F3 Canal WhatsApp (Twilio):                     [░░░░░░░░░░░░░░░░░░░░] roadmap (no iniciado)
```

## Fase CDAID actual

**Gates F1 y F2 aprobados** y app **desplegada en Streamlit Community Cloud con
éxito**. Próximo foco propuesto: canal de WhatsApp (ver Roadmap).

## Hecho

- [x] Sprint 01: núcleo (config, dominio, infra, servicios, CLI, scripts 01-04).
- [x] Sprint 02: afinado de voz (presets), calibración, interfaz Streamlit, despliegue.
- [x] Voz re-clonada con 5 muestras: `VOICE_ID=A1w42DVwDu80oNyR6BeL`.
- [x] Presets validados a oído: `calido_sereno` (defecto) y `natural`.
- [x] App Streamlit (`streamlit_app.py`) con chat + voz + historial.
- [x] **Selector de tono de voz** en la barra lateral de la app.
- [x] **Desplegada en Streamlit Community Cloud** (2026-06-20).
- [x] 69 tests, ruff 0, mypy 0. Auditorías F1 y F2 aprobadas (tasa SDD 100%).

## Pendiente del usuario

- [ ] Rotar las API keys de ElevenLabs y Anthropic (compartidas en el chat).
- [ ] (Opcional) Borrar de la cuenta ElevenLabs las voces antiguas (3 muestras).

## Roadmap — Canal de WhatsApp (dirección elegida: Twilio)

Objetivo: que la familia converse con Alexander por WhatsApp y reciba **notas de
voz**. Decisión tomada: **empezar con Twilio (sandbox)** por su rapidez de
arranque; migrable a Meta Cloud API más adelante.

**Arquitectura prevista** (el núcleo `voiceclone` se reutiliza tal cual):
```
WhatsApp → webhook (FastAPI) → conversation (Claude+persona) → speech_synthesis → nota de voz
```
- Requiere un **backend con webhook público** (Render/Railway/Fly.io); Streamlit
  no sirve para webhooks.
- Audio: nota de voz `ogg/opus` (o `mp3` adjunto).
- **Control de acceso**: lista blanca de números de la familia (privacidad).
- Costo: por conversación/mensaje (a estimar).
- Datos de conexión del sandbox (número de la familia, comando `join <sandbox>`,
  membresía de 72 h) se guardan **fuera del repo** (memoria/.env), por privacidad.

> ⏸️ Hay un planning formal pendiente del usuario sobre **"Ethical Concerns in
> Digital Afterlife Industry"** que precederá/condicionará esta fase. No iniciar
> la implementación de WhatsApp hasta recibir ese planning.

## Backlog (diferido)

- Streaming token a token en la UI (`st.write_stream`).
- Gestión de voces (borrar/editar); reproducción/descarga avanzada.
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
