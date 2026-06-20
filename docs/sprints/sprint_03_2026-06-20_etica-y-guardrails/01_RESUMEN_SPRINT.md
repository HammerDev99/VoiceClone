# Sprint 03 — Ética del duelo, guardrails de seguridad y fricción positiva

**Fecha inicio**: 2026-06-20
**Objetivo**: Reescribir la persona con guardrails psicológicos validados en la
literatura sobre "griefbots"; añadir un backstop de crisis **a nivel de código**
(independiente del LLM); introducir consentimiento informado y fricción positiva
en la interfaz Streamlit.
**Planning**: `docs/plannings/planning_03_2026-06-20_etica-duelo-guardrails/`
**Metodología**: SDD / CDAID v2 (Plan → Do → Check → Act)

## Estado General

```
Sprint 03: [████████████] 100% (7/7 SPECs)
```

| Fase | Total | Completados |
|------|:-----:|:-----------:|
| A — Persona (prompt + temperature + tests) | 3 | 3 |
| B — Guardrails de aplicación (backstop crisis) | 4 | 4 |
| C — Consentimiento + fricción (Streamlit) | 3 | 3 |
| D — Verificación (gate, docs, audit) | 3 | 3 |

> Nota: B-01/B-02 se entregaron en un único módulo/commit; C-01/C-02/C-03 en un
> único commit de UI. El recuento de "7 SPECs" agrupa por unidad de entrega.

## Registro de Progreso

| Fecha | SPEC | Descripción | Commit | Tests |
|-------|------|-------------|--------|:-----:|
| 2026-06-20 | B-01/B-02 | `domain/safety.py`: detección de crisis + `CRISIS_RESPONSE` (Línea 106) | `6f9bd9b` | +15 |
| 2026-06-20 | B-03/B-04 | Corte de camino en `generate_reply` (sin invocar a Claude); log sin contenido | `8c4d306` | +2 |
| 2026-06-20 | A-01/A-03 | Reescritura del system prompt (Vínculos Continuos + 7 guardrails) + tests | `f457d7b` | +3 |
| 2026-06-20 | A-02 | `temperature` configurable (default 0.4, acotada) en las 4 capas | `6d72208` | +6 |
| 2026-06-20 | C-01/C-02/C-03 | Consentimiento, aviso de pausa y caption reforzado (Streamlit) | `29b518b` | +1 |

## Métricas de Verificación

| Métrica | Pre | Post | Δ |
|---------|:---:|:----:|:-:|
| Tests | 69 | 96 | +27 |
| ruff | 0 | 0 | = |
| mypy --strict | 0 | 0 | = |
| Cobertura `safety.py` | — | 100% | nuevo |

## Decisiones Tomadas

| # | Decisión | Razón |
|---|----------|-------|
| 1 | Framing de Vínculos Continuos (no "cierre"/sanación) | Evita prometer "curar" el duelo; coherente con la literatura clínica |
| 2 | Backstop de crisis en código, no solo en el prompt | El LLM puede fallar bajo variación de muestreo; el backstop es determinista |
| 3 | Recurso único verificado: Línea 106 (Colombia, gratuita, 24h) | Un número genérico/inventado es peor que un solo recurso verificado |
| 4 | `temperature` default 0.4, acotada a [0.0, 1.0] | Reduce alucinación/sycophancy sin volver el tono rígido |
| 5 | Consentimiento (no autenticación fuerte) + aviso suave (no bloqueo) | Proporcional a un memorial familiar; fricción, no muro |
| 6 | El log de crisis registra la señal, nunca el contenido | Privacidad y dignidad (regla crítica #5) |

## Trazas de Delegación

| Decisión | Propuesta IA | Aprobación Humano |
|----------|-------------|-------------------|
| Ejecutar planning 03 (orden seguridad→tono) | Sí (orden B→A→C del planning) | "seguiremos con planning 03" |
| Contenido del planning (SPECs, recurso de crisis, framing) | — | Planning formal aportado por el usuario |
