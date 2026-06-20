# verification_metrics.md — Cómo medir la calidad

> Nivel 2. Métrico.

## Métricas del proyecto (Gate F1, 2026-06-20)

| Métrica | Valor | Meta |
|---------|:-----:|:----:|
| Tests | 55 | — |
| Cobertura | 95% | ≥80% |
| ruff | 0 | 0 |
| mypy --strict | 0 | 0 |
| Tasa SDD (8 puntos) | 100% | ≥85% |
| Hallazgos CRITICAL/HIGH abiertos | 0 | 0 |

## Métricas de verificación CDAID

| Métrica | Fórmula | Meta |
|---------|---------|:----:|
| Paso 1ª auditoría | ítems aprobados / total | ≥85% |
| Tiempo detección regresión | fecha_detección − fecha_intro | < 1 sprint |
| Ratio correcciones | commits corrección / total | < 10% |
| Cobertura auditoría | archivos auditados / total | 100% en ≤5 sprints |

## Cómo recalcular

```bash
pytest -q --cov                      # tests + cobertura
ruff check src tests scripts         # debe dar 0
mypy src                             # debe dar 0
```

La cobertura excluye `cli/` y `__init__.py` (ver `[tool.coverage]` en
`pyproject.toml`): la CLI es presentación y se valida con la prueba de
integración real (`scripts/01_verificar_conexion.py`).

## Líneas no cubiertas (aceptadas)

Son ramas de inicialización de SDK y `OSError` de E/S difíciles de forzar sin
red/permisos; el resto de cada módulo está cubierto en Success y Failure.
