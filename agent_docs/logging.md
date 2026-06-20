# logging.md — Cómo hacer logging

> Nivel 2. Prescriptivo.

## Uso

```python
from voiceclone.infrastructure.logging import get_logger

logger = get_logger(__name__)

logger.debug("Detalle técnico (rutas, tamaños).")
logger.info("Evento de negocio (voz creada, audio generado).")
logger.warning("Situación recuperable (no se pudo persistir VOICE_ID).")
logger.error("Error funcional", exc_info=True)   # solo dentro de except
```

## Reglas

- **Siempre** `get_logger(__name__)`. Nunca `logging.getLogger()` ni `print()`.
- `exc_info=True` únicamente dentro de un bloque `except`.
- El nivel se controla con `LOG_LEVEL` en `.env` (DEBUG/INFO/WARNING/ERROR).
- Los logs van a **stderr**; la salida de usuario de la CLI va a **stdout**
  vía `cli/console.py` (esa es la única excepción autorizada para `print`).

## Privacidad

Nunca registrar: API keys, contenido íntegro de las muestras de voz, ni datos
personales sensibles. Registrar metadatos (nº de muestras, bytes, `voice_id`)
es aceptable.

## Implementación

`infrastructure/logging.py` configura el root una sola vez (idempotente) con
formato `HH:MM:SS | NIVEL | módulo | mensaje`.
