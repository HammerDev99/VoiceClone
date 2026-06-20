# project_status.md — Estado actual

> Nivel 2. Informativo. Actualizado: 2026-06-20.

## Resumen

```
F1 Núcleo (config·dominio·infra·servicios·CLI): [████████████████████] 100% ✅ APROBADO
Flujo de uso (clonar → generar → conversar):    [██████████░░░░░░░░░░] pendiente de audios + keys
```

## Fase CDAID actual

**Check completado** (Gate F1 aprobado, ver `docs/validate/AUDIT_01`). Listo para
ejecutar el flujo real en cuanto el usuario aporte muestras y configure claves.

## Hecho

- [x] Entorno virtual `.venv` (Python 3.14) + dependencias instaladas.
- [x] Estructura CDAID v2 completa (CLAUDE.md, agent_docs/, docs/).
- [x] Código: config, domain (models + persona Alexander), infrastructure
      (elevenlabs_client, anthropic_client, logging), services
      (voice_cloning, speech_synthesis, conversation), cli (main, console).
- [x] 4 scripts entrypoint numerados.
- [x] 55 tests (unit + PBT), cobertura 95%, ruff 0, mypy 0.
- [x] Auditoría multi-instrumento (/refactoring + /design-patterns) → APROBADO.
- [x] Conexión real con ElevenLabs verificada (plan starter, IVC habilitado).

## Pendiente del usuario

- [ ] Colocar muestras `.m4a` de la voz de Alexander en `audios/`.
- [ ] (Opcional) Añadir `ANTHROPIC_API_KEY` en `.env` para la conversación.
- [ ] Ejecutar `02_clonar_voz.py` → `03_generar_voz.py` → `04_conversar.py`.
- [ ] Rotar la `ELEVENLABS_API_KEY` (fue compartida en el chat).

## Backlog (diferido, ver AUDIT_01 §5)

- Reproducción de audio con ffmpeg.
- Tests `@pytest.mark.integration` contra APIs reales.
- Utilidades de gestión de voces (borrar/editar) si se amplía el alcance.

## Métricas

| Tests | Cobertura | ruff | mypy | Tasa SDD |
|:-----:|:---------:|:----:|:----:|:--------:|
| 55 | 95% | 0 | 0 | 100% |
