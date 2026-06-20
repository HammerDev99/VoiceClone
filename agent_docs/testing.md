# testing.md — Cómo ejecutar y escribir tests

> Nivel 2. Operativo.

## Comandos

```bash
pytest                       # toda la suite (los 'integration' se omiten por defecto)
pytest -x                    # detener en el primer fallo
pytest --cov                 # con cobertura (config en pyproject.toml)
pytest tests/test_models.py  # un archivo concreto
pytest -m integration        # SÓLO las pruebas que tocan APIs reales (requieren keys)
```

## Estructura

```
tests/
  conftest.py              fixture make_settings (factory de Settings)
  test_models.py           DTOs: inmutabilidad y propiedades
  test_settings.py         carga de .env y persistencia de VOICE_ID
  test_persona.py          identidad de Alexander
  test_voice_cloning.py    discover_samples + clone_voice (mocks)
  test_speech_synthesis.py slugify, formato, synthesize (mocks + PBT)
  test_conversation.py     to_message_params + validaciones de generate_reply
```

## Principios

- **Sin red en tests unitarios**: las llamadas a ElevenLabs/Anthropic se
  *mockean* con `monkeypatch` sobre el módulo `el` o el SDK. Nunca se gasta
  cuota ni se requieren keys reales para `pytest`.
- **Success y Failure**: cada servicio se prueba en su camino feliz y en al
  menos un camino de error.
- **Property-based testing** (Hypothesis): para invariantes, p.ej. `_slugify`
  siempre produce un nombre de archivo seguro y no vacío.
- **Integración** (opcional): marcar con `@pytest.mark.integration` las pruebas
  que llamen a las APIs reales; se ejecutan a propósito, no por defecto.

## Patrón de mock de un servicio

```python
monkeypatch.setattr(ss.el, "text_to_speech", lambda *_: Success(b"FAKEAUDIO"))
result = ss.synthesize(MagicMock(), settings, "Hola")
```

## Cobertura objetivo

≥ 80% sobre `src/voiceclone` (se excluyen `cli/` y `__init__.py`, ver
`[tool.coverage]` en `pyproject.toml`).
