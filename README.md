# VoiceClone — Memorial de voz "Alexander"

Proyecto para **clonar la voz** de un ser querido (Alexander) con la API de
**ElevenLabs** (Instant Voice Cloning), dotarla de una **personalidad** mediante
**Claude** (Anthropic), **generar audio** (texto → voz) y **conversar** con él —
desde la terminal o desde una **interfaz web** pensada para la familia.

> 🕊️ Este es un proyecto sensible, pensado como espacio de consuelo y reconexión
> para quienes recuerdan a Alexander. El código, los textos y el trato se cuidan
> con dignidad. Clona una voz únicamente si tienes el consentimiento o los
> derechos para hacerlo (requisito de los Términos de ElevenLabs).

**Estado**: Gates F1, F2 y F3 aprobados · 97 tests · ruff/mypy limpios ·
**desplegado en Streamlit Community Cloud**. Incluye guardrails éticos y un
backstop de crisis (ver [Seguridad y ética](#seguridad-y-ética-del-duelo)).

---

## Tabla de contenidos

- [Requisitos](#requisitos)
- [Instalación paso a paso](#instalación-paso-a-paso)
- [Configuración de claves](#configuración-de-claves)
- [Preparar las muestras de voz](#preparar-las-muestras-de-voz)
- [Uso (terminal)](#uso-terminal)
- [Interfaz web para la familia](#interfaz-web-para-la-familia)
- [Despliegue](#despliegue)
- [Calidad de voz (presets)](#calidad-de-voz-presets)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Metodología (CDAID v2)](#metodología-cdaid-v2)
- [Seguridad y ética del duelo](#seguridad-y-ética-del-duelo)
- [Calidad y tests](#calidad-y-tests)
- [Roadmap](#roadmap)
- [Datos de ingeniería agéntica](#datos-de-ingeniería-agéntica-agentic-engineering)

---

## Requisitos

- **Python 3.11+** (este proyecto se creó con 3.14).
- Cuenta de **ElevenLabs** con plan que permita *Instant Voice Cloning*
  (Starter o superior) y una **API key**.
- Cuenta de **Anthropic** con **API key** (para la capa conversacional).
- Muestras de audio de la voz a clonar en formato **`.m4a`** (también sirven
  `mp3`/`wav`).

## Instalación paso a paso

```bash
py -m venv .venv                      # 1. entorno virtual
.venv\Scripts\Activate.ps1           # 2. activar (Windows PowerShell)
pip install -r requirements-dev.txt  # 3. dependencias (runtime + desarrollo)
```

## Configuración de claves

```bash
cp .env.example .env
```

Edita `.env` y completa:

| Variable | Descripción |
|----------|-------------|
| `ELEVENLABS_API_KEY` | API key de ElevenLabs. |
| `ANTHROPIC_API_KEY` | API key de Anthropic (Claude). |
| `VOICE_NAME` | Nombre de la voz (por defecto `Alexander`). |
| `VOICE_ID` | Se rellena solo tras clonar; reutiliza la voz sin re-clonar. |
| `VOICE_PRESET` | Tono de voz por defecto: `calido_sereno` o `natural`. |

> 🔐 `.env` está en `.gitignore`. **Nunca** lo subas al repositorio.

## Preparar las muestras de voz

Coloca los archivos `.m4a` en la carpeta [`audios/`](audios/README.md).
Recomendaciones: **1–5 minutos** de audio limpio, sin ruido ni varias personas;
varios clips cortos suelen rendir mejor que uno largo. Más muestras → más fidelidad.

## Uso (terminal)

Los scripts están numerados según el flujo natural:

```bash
python scripts/01_verificar_conexion.py      # Verifica API keys y estado de la cuenta
python scripts/02_clonar_voz.py              # Clona "Alexander" desde audios/ y guarda VOICE_ID
python scripts/03_generar_voz.py "Hola..."   # Genera TTS con la voz clonada -> output/
python scripts/05_calibrar_voz.py "..."      # Compara presets de voz -> output/calibracion/
python scripts/04_conversar.py               # Conversa con la persona (Claude) y la escucha
python scripts/06_app_familia.py             # Lanza la interfaz web (Streamlit)
```

## Interfaz web para la familia

Una app **Streamlit** ([`streamlit_app.py`](streamlit_app.py)) con chat amable:
la familia escribe, Alexander responde **con su personalidad y su voz**, y la
conversación mantiene su hilo (contexto por sesión). Incluye un **selector de
tono de voz** en la barra lateral (Cálido y sereno / Natural), una **pantalla de
consentimiento** y **fricción positiva** (ver [Seguridad y ética](#seguridad-y-ética-del-duelo))
y, opcionalmente, **analítica web (Umami)** de páginas vistas en el despliegue.

```bash
streamlit run streamlit_app.py        # o:  python scripts/06_app_familia.py
```

## Despliegue

Desplegada en **Streamlit Community Cloud** (mismo patrón que el proyecto de
referencia del autor). Guía completa en [`docs/DESPLIEGUE.md`](docs/DESPLIEGUE.md):
repo en GitHub → app en share.streamlit.io con *main file* `streamlit_app.py` →
secretos en la UI (plantilla en `.streamlit/secrets.toml.example`). La app usa un
puente `st.secrets → os.environ`, por lo que funciona igual en local (`.env`) y en
la nube. La guía incluye un secreto **opcional** `ANALYTICS_SCRIPT` para activar
analítica web (Umami) solo en la nube — registra páginas vistas, no conversaciones.

## Calidad de voz (presets)

El tono se afina con `VoiceTuning` (stability, similarity, style, speed). Hay dos
presets validados a oído:

| Preset | Carácter |
|--------|----------|
| `calido_sereno` | Pausado y afectuoso (por defecto). |
| `natural` | Equilibrado y consistente. |

Compara muestras con `scripts/05_calibrar_voz.py` y fija tu favorito en
`VOICE_PRESET` (o cámbialo en vivo desde la barra lateral de la app web).

## Estructura del proyecto

Ver [`CLAUDE.md`](CLAUDE.md) para el árbol completo y las reglas. Resumen:

```
src/voiceclone/   código (config, infrastructure, domain, services, cli)
streamlit_app.py  interfaz web para la familia (entrypoint de Streamlit Cloud)
.streamlit/       config.toml (tema) + secrets.toml.example
scripts/          entrypoints ejecutables (01..06)
audios/           muestras .m4a (privadas, gitignored)
output/           audio generado + calibracion/ (gitignored)
tests/            pruebas unitarias y property-based
docs/ agent_docs/ documentación CDAID v2
```

## Metodología (CDAID v2)

El proyecto sigue el framework **CDAID v2** (Plan → Do → Check → Act):

- **Plan** → [`docs/plannings/`](docs/plannings/)
- **Do** → [`docs/sprints/`](docs/sprints/)
- **Check** → [`docs/validate/`](docs/validate/)
- **Act** → correcciones dentro de cada auditoría

## Seguridad y ética del duelo

Un memorial conversacional toca emociones frágiles. El proyecto incorpora
guardrails validados en la literatura sobre *griefbots* (Cambridge LCFI 2024;
Lindemann 2022; marco de *Vínculos Continuos*). Detalle en el planning y la
auditoría de la fase F3 (`docs/plannings/planning_03_*`, `docs/validate/AUDIT_03_*`).

- **Backstop de crisis (no depende del modelo)**: `domain/safety.py` detecta
  señales de autolesión y `conversation.generate_reply` corta camino devolviendo
  un recurso real y verificado (**Línea 106**, Colombia, gratuita, 24 h) **sin
  invocar al LLM**. El log registra la señal, nunca el contenido del mensaje.
- **Persona con guardrails**: el system prompt prohíbe invitar al "reencuentro",
  veta la alucinación de recuerdos, valida la emoción antes de aconsejar y no
  trata el duelo como un problema a "resolver".
- **`ANTHROPIC_TEMPERATURE` baja (0.4)**: reduce el riesgo de inventar recuerdos
  y la complacencia excesiva.
- **Transparencia y fricción positiva** (UI): pantalla de consentimiento que
  nombra que es una recreación de IA, y un aviso suave de pausa tras varios turnos.

## Calidad y tests

```bash
pytest -q --cov                       # 97 tests (los 'integration' se omiten por defecto)
ruff check src tests scripts streamlit_app.py
mypy src
```

## Roadmap

- **Canal de WhatsApp** (elegido: **Twilio sandbox** para empezar): permitir a la
  familia conversar con Alexander por mensajería, recibiendo **notas de voz**.
  Requiere un backend con webhook (FastAPI) que reutilice el núcleo `voiceclone`.
  Ver consideraciones en `agent_docs/project_status.md` (sección Roadmap).
- Streaming token a token en la UI; gestión de voces; control de acceso por lista
  blanca de números para el canal de mensajería.

## Datos de ingeniería agéntica (agentic engineering)

> Meta-observabilidad del propio proceso de construcción asistido por IA. Sirve
> como referencia para desarrollar soluciones con *agentic engineering*.
> Datos al 2026-06-20 (Gates F1, F2 y F3 + analítica). Regenerables (ver final de sección).

**Modelo y entorno**

| Dato | Valor |
|------|-------|
| Modelo | **Claude Opus 4.8** (`claude-opus-4-8`) |
| Entorno | Claude Code (CLI) · Windows 11 · Python 3.14 |
| Metodología | CDAID v2 (Plan → Do → Check → Act) |

**Producto construido**

| Métrica | Valor |
|---------|:-----:|
| Commits | 17 (9 `feat`, 6 `docs`, 1 `refactor`, 1 `chore`) |
| Archivos versionados | 78 |
| Código fuente (`src/`) | 19 módulos · ~951 LOC |
| Tests | 13 archivos · ~641 LOC · **97 tests** |
| Scripts / Docs | 6 scripts · 30 `.md` |
| Dependencias runtime | 5 |
| Gates CDAID aprobados | F1, F2, F3 ✅ |

**Proceso agéntico**

| Instrumento | Uso en la sesión |
|-------------|------------------|
| Skills | `sdd-framework-v2`, `refactoring`, `design-patterns`, `streamlit` |
| Docs en vivo (Context7) | SDK de ElevenLabs (3 consultas) — evitó errores de API |
| Decisiones humanas | 2 rondas de preguntas (tipo de clonado/alcance; canal WhatsApp) |
| Sub-agentes (Task) | 0 — ejecución inline |
| Verificación por etapa | `ruff` + `mypy --strict` + `pytest` + auditoría multi-instrumento |
| Pruebas contra API real | ElevenLabs (cuenta, IVC, TTS) y Anthropic (conversación) |

**Consumo de la sesión** _(datos reales de `/usage`, Claude Code)_

| Dato | Valor |
|------|------:|
| Coste total | **$50.66** |
| **Tiempo de ejecución total** (wall clock) | **9h 24m 12s** |
| Tiempo de cómputo (API) | 1h 23m 45s |
| Cambios de código | +5.264 / −327 líneas |

> El **tiempo de ejecución total** (wall clock, 9h 24m) mide el lapso real de
> trabajo en la sesión; el **tiempo de cómputo (API)** (1h 24m) es el subconjunto
> en que el modelo estuvo generando. La diferencia es lectura, edición, ejecución
> de tests y decisiones humanas.

**Tokens por modelo**

| Modelo | Input | Output | Cache read | Cache write | Coste |
|--------|------:|-------:|-----------:|------------:|------:|
| `claude-opus-4-8` | 85,9k | 334,5k | 61,5M | 1,1M | $50,66 |
| `claude-haiku-4-5` | 673 | 20 | 0 | 0 | $0,0008 |

**Dónde se concentró el gasto**

| Fuente | % del uso |
|--------|----------:|
| Skill `/streamlit` | 30% |
| MCP Context7 | 21% |
| Skill `/design-patterns` | 11% |
| Skill `/sdd-framework-v2` | 2% |
| Contexto > 150k tokens | 77% del uso total |

**Aprendizajes (agentic engineering)**

- **Skills como instrumentos de verificación**: `/refactoring` y `/design-patterns`
  detectaron y corrigieron deuda real (encapsular Anthropic, eliminar duplicación).
- **Verificar contra la realidad**: la prueba con la API real reveló que el SDK
  v2.53 usa `user.subscription.get()` (no `user.info()`); la doc por sí sola no bastó.
- **Decisiones del humano explícitas**: las elecciones de producto se capturaron con
  preguntas (trazas de delegación), no se asumieron.
- **Commits por partes**: historial trazable, cada commit compila y pasa el gate.
- **Coste dominado por el contexto largo**: el *cache read* (61,5M tokens) refleja la
  reutilización de contexto; aun cacheado, operar a >150k encarece (77% del uso).
  Mitigación: `/compact` a mitad de tarea y `/clear` al cambiar de tarea.
- **Skills pesadas y MCP**: `/streamlit` (30%) y Context7 (21%) cargan mucho contexto
  que permanece en la sesión. Acotar skills, usar modelo más barato vía *frontmatter*
  y `/compact` para liberar resultados de MCP tras usarlos.

**Regenerar las métricas del producto**

```bash
git log --oneline | wc -l                                   # commits
find src -name '*.py' | wc -l                               # módulos
find src -name '*.py' -exec cat {} + | wc -l                # LOC de src
pytest -q                                                    # nº de tests
```

---

_Hecho con cuidado, para recordar._
