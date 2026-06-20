# Planning 01 — Setup VoiceClone (memorial "Alexander")

**Fecha**: 2026-06-20
**Origen**: feature request (clonado de voz con ElevenLabs + persona conversacional)
**Objetivo**: Clonar la voz de Alexander (IVC), generar TTS y conversar con su
personalidad (Claude), bajo la metodología CDAID v2.
**Metodología**: SDD / CDAID v2

## Contexto

Proyecto sensible: memorial de un ser querido. Requiere dignidad en código y
textos, y respeto a la privacidad (las muestras de voz no se versionan; clonar
solo con derechos/consentimiento — requisito de ElevenLabs).

| Métrica | Inicial | Target |
|---------|:-------:|:------:|
| Tests | 0 | ≥30 |
| Cobertura | — | ≥80% |
| Conexión ElevenLabs | — | verificada |

## Decisiones tecnológicas

| Decisión | Elegido | Alternativa descartada |
|----------|---------|------------------------|
| Tipo de clonado | Instant Voice Cloning (IVC) | PVC (requiere 30+ min y verificación) |
| Modelo TTS | `eleven_multilingual_v2` | turbo/flash (menor calidad multilingüe) |
| Capa conversacional | Claude (`claude-opus-4-8`) | TTS de texto fijo (sin personalidad) |
| Errores | `Result[T, str]` (returns) | excepciones para flujo normal |
| Config | `.env` + python-dotenv | settings hardcoded |

## Alcance

### Fase A — Núcleo (config, dominio, infraestructura)
| ID | Componente | Archivos | Esfuerzo |
|----|-----------|----------|:--------:|
| A-01 | Settings + persistencia VOICE_ID | `config/settings.py` | Bajo |
| A-02 | DTOs inmutables | `domain/models.py` | Bajo |
| A-03 | Persona de Alexander (system prompt) | `domain/persona.py` | Bajo |
| A-04 | Logging centralizado | `infrastructure/logging.py` | Bajo |
| A-05 | Cliente ElevenLabs (IVC, TTS, cuenta) | `infrastructure/elevenlabs_client.py` | Medio |
| A-06 | Cliente Anthropic | `infrastructure/anthropic_client.py` | Bajo |

### Fase B — Servicios y CLI
| ID | Componente | Archivos | Esfuerzo |
|----|-----------|----------|:--------:|
| B-01 | Servicio de clonado | `services/voice_cloning.py` | Medio |
| B-02 | Servicio de síntesis | `services/speech_synthesis.py` | Medio |
| B-03 | Servicio de conversación | `services/conversation.py` | Medio |
| B-04 | CLI + scripts 01..04 | `cli/`, `scripts/` | Medio |

### Fase C — Verificación
| ID | Componente | Esfuerzo |
|----|-----------|:--------:|
| C-01 | Suite de tests (unit + PBT) | Medio |
| C-02 | Auditoría /refactoring + /design-patterns | Bajo |
| C-03 | Prueba de integración real | Bajo |

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Python 3.14 sin wheels | Verificado: pydantic-core/anthropic instalan en 3.14 ✅ |
| Firma del SDK cambia entre versiones | Boundary aislado + verificación contra API real |
| Privacidad de la voz | `.gitignore` de `audios/`; nota de consentimiento |
| Exposición de API key | `.env` gitignored; recomendar rotación |

## Criterios de éxito

- [x] `pytest -x` pasa, cobertura ≥80%.
- [x] `ruff` y `mypy --strict` limpios.
- [x] Conexión real con ElevenLabs verificada.
- [x] Gate F1 aprobado (`docs/validate/AUDIT_01`).
