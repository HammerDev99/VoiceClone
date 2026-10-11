# troubleshooting.md — Cómo resolver problemas comunes

> Nivel 2. Reactivo.

## "Falta ELEVENLABS_API_KEY"
Copia `.env.example` a `.env` y rellena `ELEVENLABS_API_KEY`. Verifica con
`python scripts/01_verificar_conexion.py`.

## "No se encontraron muestras de audio en audios/"
Coloca archivos `.m4a` (o `.mp3`/`.wav`) en `audios/`. Extensiones soportadas:
`.m4a .mp3 .wav .ogg .flac .aac .webm`.

## "Tu plan NO permite IVC"
El Instant Voice Cloning requiere plan **Starter o superior** en ElevenLabs.

## "No hay VOICE_ID. Clona la voz primero"
Ejecuta `python scripts/02_clonar_voz.py`. El `VOICE_ID` se guarda solo en
`.env`. También puedes pegar un `VOICE_ID` existente en `.env`.

## "Falta ANTHROPIC_API_KEY"
Necesaria solo para `04_conversar.py`. Añádela en `.env`
(https://console.anthropic.com/settings/keys).

## Error de atributo del SDK (`'X' object has no attribute 'Y'`)
El SDK de ElevenLabs cambió de firma entre versiones. Inspecciona la API real:
```bash
.venv/Scripts/python -c "from elevenlabs.client import ElevenLabs; c=ElevenLabs(api_key='x'); print(dir(c.voices))"
```
Ajusta el wrapper en `infrastructure/elevenlabs_client.py`.

## El audio generado no se reproduce
Se guarda en `output/` como `.mp3`. Ábrelo con cualquier reproductor. La
reproducción automática (no incluida) requeriría `ffmpeg`/`mpv`.

## ModuleNotFoundError: voiceclone
Ejecuta desde la raíz del proyecto con el venv activo. Los scripts ajustan
`sys.path`; los tests usan `pythonpath=["src"]` (pyproject).

## Límite de caracteres agotado
Revisa el uso con `scripts/01_verificar_conexion.py`. El plan starter da
90 000 caracteres/mes.

## Cuota / errores 401 / 429
- 401: API key inválida → revisa `.env`.
- 429: límite de tasa → reintenta más tarde.

## La app Streamlit no arranca
- Local: `streamlit run streamlit_app.py` (o `python scripts/06_app_familia.py`)
  desde la raíz del proyecto con el venv activo.
- Si muestra "Falta ANTHROPIC_API_KEY" o "No hay VOICE_ID": faltan claves en
  `.env` (local) o en *Secrets* (nube).

## En Streamlit Cloud la app no encuentra las claves
La nube no usa `.env`. Define las claves en *App → Settings → Secrets* (formato
TOML, plantilla en `.streamlit/secrets.toml.example`). El puente
`_bridge_secrets_to_env` de `streamlit_app.py` las vuelca a variables de entorno.

## El selector de tono de voz no cambia nada
El preset elegido en la barra lateral se aplica a la **siguiente** respuesta. Los
presets válidos son `calido_sereno` y `natural` (ver `domain/voice_presets.py`).

## Quiero cambiar el preset por defecto
Edita `VOICE_PRESET` en `.env` (local) o en *Secrets* (nube).

## Diagnóstico capa por capa (claves, Claude, voz, TTS)
`python scripts/00_diagnostico.py` hace una llamada real a Claude, verifica que el
`VOICE_ID` exista en la cuenta y sintetiza un "Hola" por la misma ruta que la app,
mostrando el status HTTP y el cuerpo exacto de cada error. Es el primer paso ante
"la app responde en texto pero no habla" o "no sé qué servicio falla".

## "Tu plan de ElevenLabs no permite usar voces clonadas" (`ivc_not_permitted`)
La cuenta está activa y puede tener créditos, pero el **tipo de plan** (p.ej. pago
por uso o Free) no habilita el uso de voces creadas con Instant Voice Cloning. La
voz sigue en la cuenta; ElevenLabs responde 401 `subscription_required` al
sintetizar con ella. Solución: plan **Starter o superior**. No es un problema de
créditos (eso sería `quota_exceeded`) ni de código; no hace falta redesplegar.
La app muestra este motivo bajo el aviso "(No se pudo generar la voz...)".

## Tras un push, la app en la nube muestra mensajes o comportamientos antiguos
Streamlit Cloud puede recargar `streamlit_app.py` sin reiniciar el proceso, con lo
que los módulos de `src/` ya importados siguen en memoria (p.ej. un error que
debería salir traducido aparece con el volcado de cabeceras). Solución: *Manage
app → Reboot app*. Un cambio en `requirements.txt` también fuerza la reconstrucción
completa del entorno.

## `temperature` ya no existe en el SDK de Anthropic
`anthropic` 1.x eliminó `temperature`/`top_p`/`top_k` de `messages.create`. La app
no envía parámetros de muestreo; una variable `ANTHROPIC_TEMPERATURE` heredada se
ignora. Si un fork antiguo aún la envía, el SDK lanza `TypeError` en el cliente.

## La analítica (Umami) no registra visitas
La analítica es opcional y **solo se activa en la nube**. Verifica que el secreto
`ANALYTICS_SCRIPT` esté definido en *App → Settings → Secrets* con el snippet
completo (debe incluir `src="..."` y `data-website-id="..."`). En local no se
activa (no hay `secrets.toml`). El script se inyecta una sola vez en el `<head>`;
si recargas y no ves peticiones a `script.js`, revisa que el snippet esté bien
formado y que el dominio de Umami sea accesible. Solo registra páginas vistas, no
el contenido de las conversaciones.
