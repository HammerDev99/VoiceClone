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
