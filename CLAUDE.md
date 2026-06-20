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
  infrastructure/ logging.py, elevenlabs_client.py
  domain/         models.py (DTOs frozen), persona.py (personalidad Alexander)
  services/       voice_cloning.py, speech_synthesis.py, conversation.py
  cli/            main.py
scripts/          01_verificar_conexion .. 04_conversar  (entrypoints ejecutables)
audios/           muestras .m4a de entrada (PRIVADAS, gitignored)
output/           audio generado (gitignored)
tests/            unit + PBT
docs/             plannings/ sprints/ validate/ templates/ prompts/ diagrams/
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
python scripts/04_conversar.py           # conversa con la persona (Claude + voz)
```

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

## Estado Actual

```
Sprint 01 (clonado IVC + TTS + persona): [██████████████████░░] andamiaje listo
```

| Metrica | Valor |
|---------|-------|
| Fase CDAID | Do (Sprint 01) |
| Tests | ver `agent_docs/project_status.md` |
| Voz clonada | pendiente (requiere API key + audios) |

## Compact Instructions

Al compactar, preserva: (1) que es un memorial con voz clonada de "Alexander"
(hombre, voz masculina), (2) stack ElevenLabs IVC + Claude, (3) las 6 reglas
criticas, (4) el SPEC activo en `docs/sprints/`, (5) el tono de dignidad del proyecto.
