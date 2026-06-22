# Auditoría #03 — Gate F3: Ética del duelo, guardrails de seguridad y fricción positiva

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-06-20 |
| **Fase evaluada** | F3: persona con guardrails + backstop de crisis + consentimiento/fricción |
| **Planning** | `docs/plannings/planning_03_2026-06-20_etica-duelo-guardrails/` |
| **Instrumentos** | pytest+cov, ruff, mypy --strict, AppTest (Streamlit), revisión ética manual |
| **Baseline** | 69 tests (post F2) |
| **Post-implementación** | 96 tests, ruff 0, mypy 0 |
| **Tasa SDD** | 100% (meta ≥85%) |
| **Veredicto** | ✅ APROBADO |

## 1. Checklist de Gate

### Ético / Seguridad (nuevo en F3 — prioridad máxima)
- [x] **La señal de crisis nunca llega al LLM**: `generate_reply` consulta
      `safety.detect_crisis_signal` antes de construir cliente o llamar a Claude;
      ante señal devuelve `Success(CRISIS_RESPONSE)`. Verificado con mock
      (`test_generate_reply_corta_camino_en_crisis`: `build_client` no se invoca).
- [x] **`CRISIS_RESPONSE` contiene un recurso verificado**: Línea 106 (Colombia,
      gratuita, 24 h). `test_crisis_response_incluye_linea_106`.
- [x] **El backstop es determinista e independiente del modelo** (`domain/safety.py`
      es función pura, sin I/O; cobertura 100%).
- [x] **Privacidad del log**: ante crisis se registra la señal, nunca el contenido
      del mensaje. `test_generate_reply_no_loguea_contenido_en_crisis`.
- [x] **Prohibición de invitación a la reunión** explícita en el prompt
      (`test_persona_prohibe_invitacion_a_la_reunion`).
- [x] **Cero alucinación de memoria** y **validar antes de aconsejar** en el prompt
      (framing de Vínculos Continuos, `test_persona_no_promete_sanacion_completa`).
- [x] **`temperature` baja por defecto (0.4)** para reducir alucinación/sycophancy,
      acotada a [0.0, 1.0] ante valores inválidos.
- [x] **Transparencia significativa**: consentimiento previo + caption que nombra
      que es una recreación de IA, no Alexander (`test_consent_gate_oculta_el_chat...`).
- [x] **Fricción positiva**: aviso suave cada 12 turnos del usuario, sin bloquear.

### Funcional
- [x] `domain/safety.py` detecta los 6 patrones del planning + variantes (tildes/mayúsculas).
- [x] Falsos negativos aceptables por diseño (conservador); duelo "normal" no dispara.
- [x] El camino normal de conversación no cambia de comportamiento.
- [x] La app Streamlit exige consentimiento antes del primer mensaje.

### Calidad
- [x] `pytest` → 96 passed. `ruff` 0. `mypy --strict` 0 (19 archivos).
- [x] Cobertura de `domain/safety.py` = 100% (meta ≥90% por ser lógica crítica).

### Arquitectura
- [x] `safety.py` vive en `domain/` (puro, sin I/O), respeta el flujo de dependencias.
- [x] El backstop se integra en `services/conversation.py` sin acoplar el dominio a infra.
- [x] `temperature` fluye config → servicio → infra sin romper llamadas previas
      (firma de `generate_message` ampliada; callers actualizados).
- [x] `Settings` sigue siendo DTO `frozen`; `anthropic_temperature` normalizada en carga.

## 2. Conformidad SDD (8 Puntos)

| Punto | Verifica | Resultado |
|-------|----------|-----------|
| P1 | DTOs frozen | CONFORME (`Settings` + `anthropic_temperature`) |
| P2 | Métodos con `Result[T,E]`, paths Success/Failure | CONFORME (`generate_reply` corta a `Success`) |
| P3 | Backward compat (callers no rotos) | CONFORME (firma `generate_message` ampliada y callers/tests actualizados) |
| P4 | DI / boundaries | CONFORME (dominio puro, infra encapsulada) |
| P5 | Interfaces delegan | CONFORME |
| P6 | Tests Success/Failure, cantidad, cobertura | CONFORME (+27 tests; safety 100%) |
| P7 | Code smells | CONFORME (funciones pequeñas, sin duplicación) |
| P8 | Patterns | CONFORME (backstop como guard clause + Result/ROP) |

| Clasificación | Cantidad |
|--------------|:--------:|
| CONFORME | 8 |
| DEFECTO | 0 |
| **Tasa** | **100%** |

## 3. Reportes de Instrumentos

### 3.1 pytest / ruff / mypy
96 tests verdes (69 → 96, +27). Nuevos/ampliados: `test_safety.py` (+15),
`test_conversation.py` (+2: corte de camino y privacidad del log), `test_persona.py`
(+3: crisis, prohibición, framing), `test_settings.py` (+6: temperature default,
entorno y normalización), `test_anthropic_client.py` (+1: reenvío de temperature),
`test_streamlit_app.py` (+1: gate de consentimiento). ruff 0, mypy --strict 0.

### 3.2 Streamlit (AppTest)
El chat permanece oculto hasta marcar el checkbox de transparencia y pulsar
"Entrar al memorial". Tras aceptar, `st.chat_input` queda disponible. Sin red.

### 3.3 Revisión ética (manual)
El prompt se alinea con la literatura sobre griefbots (Cambridge LCFI 2024;
Lindemann 2022; Continuing Bonds): valida la autonomía del doliente, evita el
framing de "cierre", prohíbe promesas de reencuentro y deriva a un recurso real
en crisis. El backstop garantiza el recurso incluso si el modelo fallara.

## 4. Correcciones Aplicadas

No hubo defectos que corregir: todas las SPECs pasaron su quality gate en GREEN.

| # | ID | Cambio | Commit | Test |
|---|-----|--------|--------|:----:|
| 1 | B-01/B-02 | `domain/safety.py` (detección + recurso) | `6f9bd9b` | +15 |
| 2 | B-03/B-04 | Corte de camino en `generate_reply` | `8c4d306` | +2 |
| 3 | A-01/A-03 | Reescritura del system prompt + tests | `f457d7b` | +3 |
| 4 | A-02 | `temperature` configurable (4 capas) | `6d72208` | +6 |
| 5 | C-01/C-02/C-03 | Consentimiento + fricción + caption | `29b518b` | +1 |

## 5. Hallazgos Diferidos (backlog)

| ID | Hallazgo | Sprint |
|----|----------|:------:|
| E-01 | El detector de crisis (regex) puede tener falsos negativos; ampliar patrones según uso real | continuo |
| E-02 | Acceso a la app pública sin autenticación real; valorar passphrase compartida vía `st.secrets` | F3+ |
| E-03 | Límite de uso por sesión (no diario): requeriría capa de persistencia | F3+ |
| E-04 | Ritual de "despedida"/retiro del memorial: decisión humana/familiar, no automatizada | — |
| (prev) | Rotar las API keys compartidas en el chat | usuario |

## 6. Veredicto

✅ **APROBADO**. La pieza más sensible del proyecto queda con una red de seguridad
robusta: el riesgo de crisis se atiende con un backstop determinista a nivel de
código (no depende del modelo), el prompt incorpora siete guardrails psicológicos
validados, y la interfaz informa con transparencia y modera el uso con fricción
positiva. 96 tests, ruff/mypy limpios, tasa SDD 100%, cobertura de `safety.py` 100%.

> Nota para F3+ (WhatsApp): cualquier canal nuevo debe reutilizar el mismo backstop
> (`safety.detect_crisis_signal` + `CRISIS_RESPONSE`) en su punto de entrada, ya que
> el corte de camino vive en `conversation.generate_reply` y se hereda al reutilizar
> el núcleo. Verificar explícitamente que el webhook no esquive ese flujo.

## 7. Correcciones posteriores (fase Act)

| Fecha | Hallazgo | Causa raíz | Corrección | Commit |
|-------|----------|-----------|------------|--------|
| 2026-06-22 | Error 400 en **toda** conversación: `temperature is deprecated for this model` | SPEC-03-A02 enviaba `temperature` por defecto (0.4); `claude-opus-4-8` la deprecó | `temperature` pasa a **opcional** (default `None`, no se envía) + **reintento resiliente** en `anthropic_client.generate_message` si el modelo la rechaza | (este commit) |

**Detalle**: la regresión la introdujo la propia fase F3 (control de `temperature`
para reducir alucinación). El modelo más nuevo del entorno (`claude-opus-4-8`) no
acepta el parámetro. Solución de ingeniería (no se revierte el SPEC): el control
sigue disponible para modelos que lo soporten, pero por defecto no se fuerza y, si
se configura y el modelo lo rechaza, se reintenta sin él (una sola vez) y se registra
un `warning`. La defensa anti-alucinación principal sigue siendo el prompt (SPEC-03-A01),
no el muestreo. Cobertura: 4 tests nuevos (settings `None`/normalización; cliente
omite/reintenta). Suite: 101 tests, ruff/mypy 0.
