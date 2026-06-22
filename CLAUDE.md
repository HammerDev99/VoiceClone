# CLAUDE.md — VoiceClone ("Alexander")

> Memorial conversacional con voz clonada. Clona la voz de un ser querido
> (Alexander) con ElevenLabs (IVC), le da una personalidad con Claude, y
> permite generar audio (TTS) que honra su memoria con dignidad.

**Metodologia**: CDAID v2 (Plan → Do → Check → Act). Lee este archivo primero;
para detalle, navega a `agent_docs/` (Nivel 2) y `docs/` (Nivel 3).

---

## Stack

| Capa | Tecnologia |
|------|-----------|
| Lenguaje | Python 3.11+ (entorno: 3.14, `.venv/`) |
| Voz (clonado + TTS) | `elevenlabs` (SDK oficial, IVC) |
| Conversacion (persona) | `anthropic` (Claude, `claude-opus-4-8`) |
| Errores | `returns` — `Result[T, E]` (Success/Failure) |
| Config | `python-dotenv` + `.env` |
| Tests | `pytest`, `pytest-cov`, `hypothesis` |
| Calidad | `ruff`, `mypy --strict` |

## Estructura

```
src/voiceclone/
  config/         settings.py        (carga y valida .env)
  infrastructure/ logging.py, elevenlabs_client.py, anthropic_client.py
  domain/         models.py (DTOs frozen), persona.py, voice_presets.py
  services/       voice_cloning.py, speech_synthesis.py, conversation.py
  cli/            main.py, console.py
streamlit_app.py  interfaz web para la familia (entrypoint de Streamlit Cloud)
.streamlit/       config.toml (tema) + secrets.toml.example
scripts/          01_verificar .. 06_app_familia  (entrypoints ejecutables)
audios/           muestras .m4a de entrada (PRIVADAS, gitignored)
output/           audio generado + calibracion/ (gitignored)
tests/            unit + PBT
docs/             plannings/ sprints/ validate/ templates/ DESPLIEGUE.md ...
agent_docs/       documentacion Nivel 2
```

## Quick Start

```bash
# 1. Activar entorno e instalar dependencias
.venv/Scripts/activate                  # Windows (PowerShell/Git Bash)
pip install -r requirements-dev.txt

# 2. Configurar secretos
cp .env.example .env                     # luego edita .env con tus API keys

# 3. Colocar muestras de voz .m4a en  audios/

# 4. Flujo de uso (scripts numerados)
python scripts/01_verificar_conexion.py  # comprueba API keys y cuenta
python scripts/02_clonar_voz.py          # crea la voz "Alexander" desde audios/
python scripts/03_generar_voz.py "texto" # TTS con la voz clonada -> output/
python scripts/05_calibrar_voz.py "..."  # compara presets de voz -> output/calibracion/
python scripts/04_conversar.py           # conversa en terminal (Claude + voz)
python scripts/06_app_familia.py         # interfaz web para la familia (Streamlit)
```

Despliegue web (Streamlit Community Cloud): ver `docs/DESPLIEGUE.md`.

## Divulgacion Progresiva (donde buscar)

| Necesitas... | Consulta |
|--------------|----------|
| Como trabajar con el ciclo CDAID | `agent_docs/workflow.md` |
| Convenciones de codigo | `agent_docs/code_conventions.md` |
| Como correr/escribir tests | `agent_docs/testing.md` |
| Metricas de verificacion | `agent_docs/verification_metrics.md` |
| Arquitectura y flujo de datos | `agent_docs/architecture.md` |
| Logging | `agent_docs/logging.md` |
| Que NO hacer | `agent_docs/antipatterns.md` |
| Resolver problemas comunes | `agent_docs/troubleshooting.md` |
| Estado actual del proyecto | `agent_docs/project_status.md` |
| Desplegar la app web (familia) | `docs/DESPLIEGUE.md` |
| Planning / sprints / auditorias | `docs/plannings/`, `docs/sprints/`, `docs/validate/` |

## Reglas Criticas (6)

1. **Logging**: `get_logger(__name__)`. Nunca `logging.getLogger`, nunca `print()`.
2. **Errores**: `Result[T, E]` (Success/Failure) en logica de negocio. No `except: pass`.
3. **Inmutabilidad**: `@dataclass(frozen=True)` para todos los DTOs.
4. **Secretos**: solo en `.env` (gitignored). Nunca hardcodear API keys.
5. **Privacidad y dignidad**: las muestras de voz son datos personales sensibles
   (NO se versionan). Esta es la voz de un ser querido: tratar el codigo, los
   textos y los logs con respeto. Clonar solo con consentimiento/derechos sobre la voz.
6. **Calidad**: todo cambio pasa `pytest -x` + `ruff check` + `mypy --strict`.
7. **Protocolo de crisis (no negociable)**: ante una senal de autolesion, el
   backstop `domain/safety.py` corta camino y devuelve `CRISIS_RESPONSE` (Linea 106,
   Colombia) SIN invocar al LLM. La seguridad no depende del prompt ni del modelo.
   Nunca debilitar ni eludir este corte; el log registra la senal, jamas el contenido.

## Estado Actual

```
Sprint 01 (clonado IVC + TTS + persona):  [████████████████████] ✅ Gate F1
Sprint 02 (calidad de voz + UI familia):  [████████████████████] ✅ Gate F2
Despliegue Streamlit Cloud:               [████████████████████] ✅ desplegado
Sprint 03 (etica, guardrails, friccion):  [████████████████████] ✅ Gate F3
F3+ Canal WhatsApp (Twilio):              [░░░░░░░░░░░░░░░░░░░░] roadmap
```

**Roadmap**: canal de WhatsApp (vía elegida: **Twilio sandbox**) para que la
familia converse con notas de voz; requiere backend con webhook (FastAPI) que
reutiliza el núcleo. El planning de ética del *digital afterlife* ya está
ejecutado (planning_03 / Gate F3): persona con guardrails, backstop de crisis y
consentimiento. Detalle en `agent_docs/project_status.md`.

| Metrica | Valor |
|---------|-------|
| Fase CDAID | Check completado (F1, F2, F3 aprobados) |
| Tests | 101 (ruff 0, mypy 0) — ver `agent_docs/project_status.md` |
| Voz clonada | `VOICE_ID=A1w42DVwDu80oNyR6BeL` (5 muestras) |
| Preset por defecto | `calido_sereno` (alt: `natural`) |
| Seguridad | backstop de crisis (`domain/safety.py`, Linea 106) + consentimiento UI |

## Compact Instructions

Al compactar, preserva: (1) que es un memorial con voz clonada de "Alexander"
(hombre, voz masculina), (2) stack ElevenLabs IVC + Claude, (3) las 7 reglas
criticas (incluida la #7 de protocolo de crisis no negociable), (4) el SPEC activo
en `docs/sprints/`, (5) el tono de dignidad del proyecto.
