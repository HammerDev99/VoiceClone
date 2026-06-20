# docs/validate/ — Auditorías (fase Check del PDCA)

Un archivo por auditoría. Cada `AUDIT_NN_*.md` consolida todo (checklist,
conformidad SDD, reportes de instrumentos, correcciones y veredicto).

## Convención de nombres

```
AUDIT_{NN}_{YYYY-MM-DD}_{SLUG}.md
SLUG: GATE_F{N}_{FASE} | REAUDIT_F{N} | QA_FINAL | SECURITY_SCAN
```

## Historial

| # | Fecha | Alcance | Veredicto | Tasa SDD |
|---|-------|---------|-----------|:--------:|
| 01 | 2026-06-20 | Gate F1 — Núcleo (config, dominio, infra, servicios, CLI) | ✅ APROBADO | 100% |
| 02 | 2026-06-20 | Gate F2 — Calidad de voz (presets) + interfaz Streamlit + despliegue | ✅ APROBADO | 100% |

## Instrumentos de verificación usados

- `pytest` + `pytest-cov` (unit + PBT con Hypothesis)
- `ruff` (lint + formato), `mypy --strict` (tipos)
- Skill `/refactoring` (smells de Fowler)
- Skill `/design-patterns` (GoF + SOLID)
- Prueba de integración real contra la API de ElevenLabs
