# Sprint 01 — Clonado IVC + TTS + Persona

**Fecha inicio**: 2026-06-20
**Objetivo**: Implementar el núcleo del memorial: clonar voz (IVC), generar TTS
y conversar con la persona de Alexander.
**Planning**: `docs/plannings/planning_01_2026-06-20_setup-voiceclone/`
**Metodología**: SDD / CDAID v2

## Estado General

```
Sprint 01: [████████████████████] 100% (13/13 SPECs)
```

| Fase | Total | Completados |
|------|:-----:|:-----------:|
| A — Núcleo | 6 | 6 |
| B — Servicios y CLI | 4 | 4 |
| C — Verificación | 3 | 3 |

## Registro de Progreso

| Fecha | SPEC | Descripción | Tests |
|-------|------|-------------|:-----:|
| 06-20 | A-01 | settings + save_voice_id | +5 |
| 06-20 | A-02 | DTOs frozen | +7 |
| 06-20 | A-03 | persona Alexander | +3 |
| 06-20 | A-04 | logging | — |
| 06-20 | A-05 | cliente ElevenLabs | +13 |
| 06-20 | A-06 | cliente Anthropic | +5 |
| 06-20 | B-01 | servicio clonado | +5 |
| 06-20 | B-02 | servicio síntesis | +6 |
| 06-20 | B-03 | servicio conversación | +6 |
| 06-20 | B-04 | CLI + scripts 01..04 | (integración) |
| 06-20 | C-01 | suite de tests | 55 total |
| 06-20 | C-02 | auditoría refactor/patterns | — |
| 06-20 | C-03 | integración real ElevenLabs | ✅ |

## Métricas de Verificación

| Métrica | Pre | Post | Δ |
|---------|:---:|:----:|:-:|
| Tests | 0 | 55 | +55 |
| Cobertura | — | 95% | — |
| ruff | — | 0 | — |
| mypy | — | 0 | — |

## Decisiones Tomadas

| # | Decisión | Razón |
|---|----------|-------|
| 1 | IVC en vez de PVC | Pocas muestras `.m4a`, plan starter |
| 2 | Claude para la persona | Personalidad conversacional con system prompt |
| 3 | Encapsular Anthropic en infra (H-01) | Simetría/DIP, testabilidad |
| 4 | `user.subscription.get()` (INT-01) | Firma real del SDK v2.53 |

## Trazas de Delegación

| Decisión | Propuesta IA | Aprobación Humano |
|----------|-------------|-------------------|
| Tipo de clonado y alcance | 3 opciones presentadas | Usuario eligió IVC + persona |
| Capa conversacional con Claude | Propuesta por defecto | Confirmada por contexto |
| Lanzar /refactoring + /design-patterns | — | Solicitado por el usuario |

## Resultado

Gate F1 **APROBADO** (`docs/validate/AUDIT_01_2026-06-20_GATE_F1_CORE.md`).
