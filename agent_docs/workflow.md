# workflow.md — Cómo trabajar con CDAID v2

> Nivel 2 de divulgación progresiva. Procesal: cómo avanzar el proyecto.

## Ciclo PDCA

```
Plan (docs/plannings/) → Do (docs/sprints/) → Check (docs/validate/) → Act (en AUDIT_*.md)
```

| Fase | Dónde | Qué se produce |
|------|-------|----------------|
| **Plan** | `docs/plannings/` | SPECs con criterios de aceptación verificables |
| **Do** | `docs/sprints/` | Código + tests (TDD), tracking por SPEC |
| **Check** | `docs/validate/` | Auditoría consolidada `AUDIT_NN_*.md` |
| **Act** | dentro del AUDIT | Correcciones CRITICAL/HIGH con TDD |

## Flujo por SPEC (fase Do)

1. **Ready**: el SPEC tiene criterios de aceptación claros.
2. **Explorar**: leer código y patrones existentes antes de tocar nada.
3. **RED**: escribir el/los test(s) que validan cada criterio → deben fallar.
4. **GREEN**: implementar lo mínimo para que pasen.
5. **Quality gate**: `pytest -x` + `ruff check` + `mypy src`.
6. **Revisar**: agentes revisores (code-reviewer, python-reviewer).
7. **Done**: tests verdes + gate limpio + SPEC marcado `[x]`.
8. **Tracking**: registrar en el resumen del sprint (fecha, SPEC, +tests).

## Investigación antes de implementar (regla del usuario)

Antes de escribir código nuevo: buscar implementaciones existentes (GitHub,
registros de paquetes) y confirmar APIs con documentación oficial (Context7).
Aquí se aplicó: el SDK `elevenlabs` y `anthropic` se confirmaron vía Context7.

## Comandos rápidos

```bash
pytest -x                       # tests (integration se omite por defecto)
pytest --cov                    # con cobertura
ruff check src tests scripts    # lint
ruff format src tests scripts   # formateo
mypy src                        # tipos (estricto, solo src)
```

## Dónde mirar

- Convenciones de código → `code_conventions.md`
- Tests → `testing.md`
- Métricas → `verification_metrics.md`
- Arquitectura → `architecture.md`
- Qué NO hacer → `antipatterns.md`
- Problemas comunes → `troubleshooting.md`
