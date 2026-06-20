# code_conventions.md — Cómo escribir código

> Nivel 2. Prescriptivo. Extiende las 6 reglas críticas de `CLAUDE.md`.

## Naming

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Archivos | `snake_case.py` | `speech_synthesis.py` |
| Clases / DTOs | `PascalCase` | `SpeechRequest` |
| Funciones | `snake_case` | `clone_voice` |
| Constantes | `UPPER_SNAKE` | `MAX_TEXT_LENGTH` |
| Privados | `_prefijo` | `_slugify` |

## Imports (orden forzado por ruff I)

```python
from __future__ import annotations   # 1. future

import re                            # 2. stdlib
from pathlib import Path

from returns.result import Result    # 3. terceros

from voiceclone.domain.models import SpeechRequest  # 4. local
```

## Manejo de errores — Result Pattern (obligatorio)

La lógica de negocio devuelve `Result[T, str]` (`Success`/`Failure`), nunca
lanza excepciones para flujo normal:

```python
def synthesize(...) -> Result[GeneratedSpeech, str]:
    if not text.strip():
        return Failure("El texto a sintetizar esta vacio.")
    ...
    return Success(generated)
```

**Consumo del Result** (patrón usado en este proyecto):

```python
result = servicio(...)
if isinstance(result, Failure):
    return result            # o manejar el error
valor = result.unwrap()
```

### Excepciones: sólo en boundaries de infraestructura

`try/except` amplio se permite **únicamente** al llamar a APIs externas
(SDK de ElevenLabs/Anthropic), y siempre: se registra con `exc_info=True`
y se traduce a `Failure`. Ver `infrastructure/elevenlabs_client.py`.

**PROHIBIDO**: `except: pass`, `except Exception: pass`, try/except anidados
para lógica de negocio.

## Inmutabilidad

Todos los DTOs son `@dataclass(frozen=True)`. Para "modificar", crear copia:

```python
history = [*history, ConversationTurn(role="user", content=msg)]
```

## Logging

```python
from voiceclone.infrastructure.logging import get_logger
logger = get_logger(__name__)
```

**PROHIBIDO** en lógica/infra: `logging.getLogger()`, `print()`.
Excepción: `cli/console.py` usa `print` deliberadamente (interfaz de usuario).

## Type hints (obligatorios)

```python
def discover_samples(input_dir: Path) -> Result[list[Path], str]: ...
```

`mypy --strict` debe pasar sobre `src/`.

## Seguridad

- Secretos sólo en `.env` (gitignored). Nunca hardcodear API keys.
- Validar todo input en los boundaries (texto vacío, rutas, formatos de audio).
- Las muestras de voz son datos personales sensibles: no se versionan ni se loguean.

## Commits

`tipo(alcance): descripción en español` — `feat`, `fix`, `refactor`, `docs`,
`test`, `chore`. Sin firma de IA.
