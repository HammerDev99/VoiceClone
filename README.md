# VoiceClone — Memorial de voz "Alexander"

Proyecto para **clonar la voz** de un ser querido (Alexander) usando la API de
**ElevenLabs** (Instant Voice Cloning), dotarla de una **personalidad** mediante
**Claude** (Anthropic), y **generar audio** (texto → voz) que honre su memoria.

> 🕊️ Este es un proyecto sensible, pensado como espacio de consuelo y reconexión
> para quienes recuerdan a Alexander. El código, los textos y el trato se cuidan
> con dignidad. Clona una voz únicamente si tienes el consentimiento o los
> derechos para hacerlo (requisito de los Términos de ElevenLabs).

---

## Tabla de contenidos

- [Requisitos](#requisitos)
- [Instalación paso a paso](#instalación-paso-a-paso)
- [Configuración de claves](#configuración-de-claves)
- [Preparar las muestras de voz](#preparar-las-muestras-de-voz)
- [Uso](#uso)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Metodología (CDAID v2)](#metodología-cdaid-v2)
- [Calidad y tests](#calidad-y-tests)

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
# 1. (Ya hecho) Entorno virtual
py -m venv .venv

# 2. Activar el entorno
#    Windows PowerShell:
.venv\Scripts\Activate.ps1
#    Windows Git Bash:
source .venv/Scripts/activate

# 3. Instalar dependencias (runtime + desarrollo)
pip install -r requirements-dev.txt
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

> 🔐 `.env` está en `.gitignore`. **Nunca** lo subas al repositorio.

## Preparar las muestras de voz

Coloca los archivos `.m4a` en la carpeta [`audios/`](audios/README.md).
Recomendaciones para mejor calidad:

- Entre **1 y 5 minutos** de audio en total (IVC).
- Voz **limpia**, sin música de fondo, ruido ni varias personas hablando.
- Varios clips cortos suelen funcionar mejor que uno largo.

## Uso

Los scripts están numerados según el flujo natural:

```bash
python scripts/01_verificar_conexion.py      # Verifica API keys y muestra info de la cuenta
python scripts/02_clonar_voz.py              # Clona "Alexander" desde audios/ y guarda VOICE_ID
python scripts/03_generar_voz.py "Hola..."   # Genera TTS con la voz clonada -> output/
python scripts/04_conversar.py               # Conversa con la persona (Claude) y la escucha
```

## Estructura del proyecto

Ver [`CLAUDE.md`](CLAUDE.md) para el árbol completo y las reglas. Resumen:

```
src/voiceclone/   código (config, infrastructure, domain, services, cli)
scripts/          entrypoints ejecutables (01..04)
audios/           muestras .m4a (privadas)
output/           audio generado
tests/            pruebas unitarias y property-based
docs/ agent_docs/ documentación CDAID v2
```

## Metodología (CDAID v2)

El proyecto sigue el framework **CDAID v2** (Plan → Do → Check → Act):

- **Plan** → [`docs/plannings/`](docs/plannings/)
- **Do** → [`docs/sprints/`](docs/sprints/)
- **Check** → [`docs/validate/`](docs/validate/)
- **Act** → correcciones dentro de cada auditoría

## Calidad y tests

```bash
pytest -x            # tests (los marcados 'integration' se omiten por defecto)
pytest --cov         # con cobertura
ruff check src tests scripts
mypy src
```

---

_Hecho con cuidado, para recordar._
