# Gate F{N} — {Nombre Fase}

**Fecha**: YYYY-MM-DD
**Decisión**: ✅ APROBADO / ⛔ BLOQUEADO

## Criterios de paso (todos obligatorios)

- [ ] `pytest -x` pasa (0 fallos).
- [ ] Cobertura ≥ 80%.
- [ ] `ruff check` = 0.
- [ ] `mypy src` = 0.
- [ ] Tasa SDD (8 puntos) ≥ 85%.
- [ ] 0 hallazgos CRITICAL / HIGH abiertos.
- [ ] Auditoría consolidada creada en `docs/validate/AUDIT_{NN}_*.md`.

## Autoridad de aprobación

- Gates F1–F4: automática si se cumplen los criterios.
- Gate F5 (integración/deploy): requiere revisión humana explícita.

## Resultado

{Resumen de métricas y veredicto, enlazando al AUDIT correspondiente.}
