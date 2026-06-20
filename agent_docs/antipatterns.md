# antipatterns.md — Qué NO hacer

> Nivel 2. Prohibitivo.

## Errores

- ❌ `except: pass` o `except Exception: pass` (silenciar errores).
- ❌ `try/except` para flujo normal de negocio → usar `Result[T, str]`.
- ❌ `try/except` amplio fuera de `infrastructure/` (solo permitido en los
  boundaries de SDK, con `exc_info=True` + `Failure`).

## Estado y datos

- ❌ Mutar DTOs → son `frozen`. Crear copias nuevas.
- ❌ `dict`/`str` sueltos para conceptos del dominio cuando hay un DTO.
- ❌ Variables globales mutables compartidas.

## Logging / salida

- ❌ `print()` en lógica o infraestructura (solo `cli/console.py`).
- ❌ `logging.getLogger()` directo → usar `get_logger`.
- ❌ Loguear API keys o el audio/voz de las personas.

## Secretos y privacidad

- ❌ Hardcodear API keys (van en `.env`, gitignored).
- ❌ Versionar `audios/` o `output/` (datos personales / generados).
- ❌ Clonar una voz sin consentimiento o derechos sobre ella.

## ElevenLabs / Anthropic

- ❌ Instanciar los SDK fuera de `infrastructure/` → romper DIP (ver H-01 en
  `docs/validate/AUDIT_01`).
- ❌ Asumir la firma de la API sin verificar contra la versión instalada
  (el SDK v2.53 usa `user.subscription.get()`, no `user.info()`).
- ❌ Enviar textos enormes a TTS sin validar (`MAX_TEXT_LENGTH`).

## Proceso

- ❌ Mezclar refactor + feature en el mismo commit.
- ❌ Marcar un SPEC como `done` sin tests verdes + gate limpio.
