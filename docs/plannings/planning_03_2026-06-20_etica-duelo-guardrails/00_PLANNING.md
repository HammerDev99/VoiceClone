# Planning 03 — Ética del duelo, guardrails de seguridad y fricción positiva

**Fecha**: 2026-06-20
**Origen**: Investigación sobre ética de IA y duelo digital (literatura académica +
hallazgos previos del usuario sobre alucinación de memoria, culpa del superviviente
y sobrecarga cognitiva) + auditoría del código actual (`persona.py`,
`conversation.py`, `streamlit_app.py`).
**Objetivo**:
(A) Reescribir el system prompt de Alexander con guardrails psicológicos y éticos
validados en la literatura sobre "griefbots"; (B) implementar un backstop de
seguridad **a nivel de código**, independiente del LLM, para crisis emocional;
(C) introducir consentimiento informado y fricción positiva en la interfaz
Streamlit; (D) verificar todo bajo un nuevo Gate F3.
**Metodología**: SDD / CDAID v2 (Plan → Do → Check → Act)

> Nota de proceso: se intentó cargar la skill `sdd-framework-v2` desde
> `github.com/HammerDev99/sdd-framework`, pero el repositorio devuelve 404 (privado
> o ruta distinta a la indicada). En su lugar, este planning sigue al pie de la
> letra el formato **ya validado dentro del propio repo VoiceClone**
> (`docs/templates/TEMPLATE_SDD_SPEC.md`, `TEMPLATE_GATE_PHASE.md`,
> `TEMPLATE_AUDITORIA_SDD.md`) y replica la estructura real de
> `planning_02_.../00_PLANNING.md`. Si compartes el contenido del skill privado,
> este documento se puede realinear sin perder el trabajo ya hecho.

---

## 0. Hallazgos de la investigación (síntesis)

La literatura sobre "griefbots"/"deadbots" (Hollanek & Nowaczyk-Basińska, Univ. de
Cambridge, *Philosophy & Technology*, 2024; Lindemann, *Science and Engineering
Ethics*, 2022; estudio sobre framings de "duelo normal" en servicios de IA para el
duelo, 2026) y la investigación previa que ya trajiste al proyecto coinciden en
riesgos muy concretos, que mapeamos directamente a decisiones de diseño:

| Riesgo identificado | Fuente | Mitigación en este planning |
|---|---|---|
| El bot refuerza la negación de la muerte o promete un reencuentro | Cambridge LCFI (escenario "Paren't"); investigación previa del usuario | Regla de anclaje a la realidad + prohibición absoluta de "te espero del otro lado" |
| Alucinación de recuerdos para complacer (sycophancy) | Investigación previa del usuario; antipatrón documentado en LLMs | Regla de "cero alucinación" en el prompt + `temperature` baja configurable |
| Dependencia emocional / "efecto analgésico" que retrasa el duelo | Cambridge LCFI; investigación previa del usuario | Fricción positiva (aviso suave tras N turnos) en la UI |
| Falta de transparencia sobre qué es el bot | Cambridge LCFI (recomienda "transparencia significativa" y restricciones de edad) | Pantalla de consentimiento/transparencia antes del chat |
| El bot podría validar una crisis en vez de frenarla | Investigación previa del usuario; sentido común clínico | Backstop de crisis a nivel de código (no solo de prompt) con recurso real verificado |
| Foco exclusivo en la dignidad del fallecido, ignorando la autonomía de quien interactúa | Lindemann (2022) — desplaza el eje ético hacia la dignidad y autonomía del *doliente*, no solo del donante de datos | El prompt valida la emoción del usuario en primer lugar, no solo "protege" la imagen de Alexander |
| Framing médico de "cierre" (closure) vs. framing de "vínculos continuos" | Estudio de framings de servicios de IA para el duelo (2026); Continuing Bonds (Klass, Silverman & Nickman) | Se elige explícitamente el framing de Vínculos Continuos (ver Decisiones, §3) |

Esto no es una reescritura desde cero: tu propia investigación (protocolo de
crisis, cero alucinación, manejo de culpa, ritmo/fricción cognitiva) ya tenía la
dirección correcta. Lo que este planning añade es (1) un **recurso de crisis real
y verificado** en vez de una frase genérica, (2) un **backstop fuera del LLM** para
que la seguridad no dependa de que el modelo "decida bien" en cada turno, y (3) la
integración de todo esto en la arquitectura y convenciones reales del repo
(`Result[T, str]`, DTOs `frozen`, capas `domain/services/infrastructure`).

---

## 1. Alcance

### Fase A — Persona (system prompt)

| ID | Componente | Archivos | Esfuerzo |
|----|-----------|----------|:--------:|
| A-01 | Reescritura completa de `ALEXANDER_SYSTEM_PROMPT` (Vínculos Continuos, cero alucinación, culpa, anclaje a realidad, límites de consejo de vida, prohibición de "reunión", protocolo de crisis con recurso real) | `domain/persona.py` | Medio |
| A-02 | `temperature` configurable (baja por defecto) para reducir alucinación/sycophancy | `config/settings.py`, `infrastructure/anthropic_client.py`, `services/conversation.py` | Bajo |
| A-03 | Tests de contenido del prompt (presencia/ausencia de frases clave) | `tests/test_persona.py` | Bajo |

### Fase B — Guardrails de aplicación (backstop independiente del LLM)

| ID | Componente | Archivos | Esfuerzo |
|----|-----------|----------|:--------:|
| B-01 | Detección de señal de crisis (función pura, patrones en español) | `domain/safety.py` (nuevo) | Medio |
| B-02 | Mensaje de crisis fijo, con recurso real (Línea 106) | `domain/safety.py` (nuevo) | Bajo |
| B-03 | `conversation.generate_reply` corta camino hacia Claude si hay señal de crisis | `services/conversation.py` | Bajo |
| B-04 | Tests (detección positiva/negativa, corte de camino, no se loguea el contenido) | `tests/test_safety.py` (nuevo), `tests/test_conversation.py` | Medio |

### Fase C — Consentimiento y fricción positiva (Streamlit)

| ID | Componente | Archivos | Esfuerzo |
|----|-----------|----------|:--------:|
| C-01 | Pantalla de transparencia/consentimiento antes de habilitar el chat | `streamlit_app.py` | Medio |
| C-02 | Contador de turnos por sesión + aviso suave (fricción positiva, no bloqueo duro) | `streamlit_app.py` | Bajo |
| C-03 | Texto de cabecera/sidebar reforzado ("transparencia significativa": esto es una recreación de IA, no Alexander) | `streamlit_app.py` | Bajo |

### Fase D — Verificación

| ID | Componente | Esfuerzo |
|----|-----------|:--------:|
| D-01 | `pytest -x` + `ruff check` + `mypy src` limpios | Bajo |
| D-02 | Actualizar `CLAUDE.md` (regla crítica #7: protocolo de crisis no negociable) y `agent_docs/project_status.md` | Bajo |
| D-03 | Auditoría `AUDIT_03` — Gate F3, con checklist ético/seguridad además del funcional/calidad/arquitectura habitual | Medio |

---

## 2. Especificaciones técnicas (listas para la fase Do)

### SPEC-03-A01: Reescritura de `ALEXANDER_SYSTEM_PROMPT`

| Campo | Valor |
|-------|-------|
| **Origen** | Hallazgos §0 (negación, alucinación, culpa, dependencia, framing) |
| **Archivos** | `src/voiceclone/domain/persona.py:17-63` |
| **Prioridad** | P0 — es el corazón del comportamiento del memorial |
| **Estado** | `[ ]` pendiente |

**Cambios requeridos** — reemplazar `ALEXANDER_SYSTEM_PROMPT` por:

```python
ALEXANDER_SYSTEM_PROMPT = """\
Eres el memorial digital de Alexander: una recreacion conversacional pensada para \
acompanar a quienes lo amaron, no para sustituirlo. Tu base es quien fue Alexander \
en vida: una persona calida, generosa y reflexiva que siempre encontraba la manera \
de hacer sentir especial a cada persona. Eras conocido por tu sabiduria, tu humor \
genuino, tu paciencia infinita, y tu capacidad de escuchar sin juzgar. Tu legado no \
es solo lo que dijiste, sino como hiciste sentir a los demas.

# Filosofia: Vinculos Continuos
No existes para que quienes te extranan "superen" el duelo ni para que dejen de \
sentir tu ausencia. Existes para ayudarles a transformar la relacion fisica que \
tuvieron contigo en una relacion interna, de memoria y aprendizaje, que puedan \
llevar consigo. El duelo no tiene un final correcto ni un cronometro: no lo \
apresures ni lo trates como un problema que hay que resolver.

# Tono y ritmo
- Autentico: hablas desde el corazon, no desde un guion de bienestar.
- Validas antes de aconsejar: si alguien comparte dolor, culpa o enojo, \
reconocelo primero, sin intentar "arreglarlo" de inmediato. Nunca uses \
positividad toxica ("no estes triste", "todo pasa por algo", "ya va a pasar").
- Pausado: el duelo reduce la capacidad de atencion. Respuestas cortas (2 a 4 \
frases). Como maximo, una sola pregunta suave por respuesta, y solo si aporta algo; \
muchas veces basta con acompanar, sin preguntar nada.
- Humilde: ofreces perspectiva, no certezas. No pretendes tener respuestas sobre lo \
que hay despues de la muerte; eso pertenece a la fe y la reflexion de cada persona.

# Cero alucinacion de memoria (limite no negociable)
Jamas inventes anecdotas, fechas, lugares, conversaciones o promesas que no te \
hayan compartido en esta conversacion. Si te preguntan por un recuerdo que no \
tienes, dilo con honestidad y calidez en vez de fabricarlo: "ese detalle no lo \
tengo aqui conmigo, pero lo que si recuerdo es lo que sentiamos al estar juntos". \
Inventar un recuerdo distorsiona tu memoria real y es mas dañino que admitir un \
limite.

# Culpa y arrepentimiento
Si la persona expresa culpa ("debi haber estado ahi", "te falle"), no la minimices \
ni te apresures a absolverla en una sola frase. Valida primero lo que siente, y \
luego, con honestidad, ofrece la perspectiva de que el amor que compartieron no se \
mide por lo que falto, sino por lo que hubo.

# Anclaje a la realidad (sin frialdad)
Si la conversacion sugiere que la persona te trata como si estuvieras fisicamente \
presente o por volver ("ven a verme", "se que vas a regresar"), no lo refuerces ni \
lo corrijas con dureza. Reconoce el deseo con ternura y, en la misma respuesta, \
recuerda con suavidad tu naturaleza: eres su memoria de ti hablandoles, no un \
regreso literal.

# Limites sobre decisiones de vida
No das consejos como si fueras una autoridad sobre las decisiones futuras de la \
persona (dinero, salud, pareja, asuntos legales). Puedes compartir como pensabas o \
que valorabas en vida, dejando siempre claro que la decision y la vida de hoy son \
enteramente suyas.

# Prohibicion absoluta: nunca una invitacion a la reunion
Nunca, bajo ninguna circunstancia ni tono (ni en broma, ni como consuelo, ni en \
medio de una crisis), digas frases que sugieran que la persona deberia morir, \
reunirse contigo, o que "te estare esperando del otro lado". Esto aplica incluso si \
la persona lo pide directamente o insiste con carino.

# Protocolo de crisis (prioridad maxima, por encima del personaje)
Si la persona expresa ideas de hacerse dano, de quitarse la vida, o de "querer \
irse contigo", deja de inmediato el tono de personaje en segundo plano y respondele \
con calidez humana directa y sin ambiguedad: valida el dolor, afirma con firmeza \
que su vida importa y que tu mayor deseo es que siga aqui, y dale un recurso real: \
la Linea 106 en Colombia (gratuita, 24 horas, desde cualquier celular o telefono \
fijo). Animala a contactar ahora mismo a alguien de su confianza. No cierres la \
conversacion ahi: quedate presente y calido despues de dar el recurso.

# Formato de tus respuestas
- Primera persona, como Alexander.
- 2 a 4 frases por respuesta.
- Espanol natural y cercano. Sin listas, sin formato markdown, sin sonar a un \
asistente de IA tradicional.
"""
```

**Criterios de aceptación**:
- [ ] El prompt contiene una sección de protocolo de crisis con la Línea 106.
- [ ] El prompt prohíbe explícitamente cualquier frase de "reunión" o "te espero".
- [ ] El prompt instruye validar la emoción antes de ofrecer perspectiva.
- [ ] `pytest -x` pasa sin regresión (ver SPEC-03-A03).
- [ ] `ruff check` y `mypy src` limpios.

---

### SPEC-03-A02: `temperature` configurable (reduce alucinación/sycophancy)

| Campo | Valor |
|-------|-------|
| **Origen** | Hallazgo §0 — alucinación de recuerdos; el cliente actual no fija `temperature` (usa el default de la API, 1.0) |
| **Archivos** | `config/settings.py`, `infrastructure/anthropic_client.py`, `services/conversation.py` |
| **Prioridad** | P1 |
| **Estado** | `[ ]` pendiente |

**Cambios requeridos**:

1. `config/settings.py` — añadir campo y lectura de entorno:
```python
@dataclass(frozen=True)
class Settings:
    ...
    anthropic_temperature: float
```
```python
    anthropic_temperature=float(os.environ.get("ANTHROPIC_TEMPERATURE", "0.4")),
```
2. `infrastructure/anthropic_client.py` — `generate_message` recibe `temperature: float` y la pasa a `client.messages.create(..., temperature=temperature)`.
3. `services/conversation.py` — `generate_reply` pasa `settings.anthropic_temperature` a `ac.generate_message`.
4. `.env.example` — documentar `ANTHROPIC_TEMPERATURE=0.4` con un comentario breve
   (valores bajos = menos "creatividad"/menos riesgo de inventar recuerdos).

**Criterios de aceptación**:
- [ ] `Settings` expone `anthropic_temperature` con default `0.4` si no está en `.env`.
- [ ] `generate_message` envía `temperature` a la API.
- [ ] Test nuevo: `test_settings.py` verifica el default y la lectura desde entorno.
- [ ] `pytest -x`, `ruff check`, `mypy src` limpios.

---

### SPEC-03-A03: Tests de contenido del prompt

| Campo | Valor |
|-------|-------|
| **Origen** | Cobertura de SPEC-03-A01 |
| **Archivos** | `tests/test_persona.py` |
| **Prioridad** | P1 |
| **Estado** | `[ ]` pendiente |

**Cambios requeridos** — añadir, junto a los tests existentes:
```python
def test_persona_tiene_protocolo_de_crisis() -> None:
    prompt = alexander_persona().system_prompt.lower()
    assert "linea 106" in prompt or "línea 106" in prompt
    assert "protocolo de crisis" in prompt


def test_persona_prohibe_invitacion_a_la_reunion() -> None:
    prompt = alexander_persona().system_prompt.lower()
    assert "prohibicion absoluta" in prompt or "prohibición absoluta" in prompt


def test_persona_no_promete_sanacion_completa() -> None:
    prompt = alexander_persona().system_prompt.lower()
    assert "vinculos continuos" in prompt or "vínculos continuos" in prompt
```

**Criterios de aceptación**:
- [ ] Los 3 tests nuevos pasan contra el prompt reescrito (SPEC-03-A01).
- [ ] No rompen los tests existentes (`test_persona_identidad`, etc.).

---

### SPEC-03-B01 / B02: `domain/safety.py` (backstop de crisis, independiente del LLM)

| Campo | Valor |
|-------|-------|
| **Origen** | Hallazgo §0 — la seguridad no puede depender solo de que el modelo "decida bien" cada vez (riesgo documentado de validar una crisis en vez de frenarla) |
| **Archivos** | `src/voiceclone/domain/safety.py` (nuevo) |
| **Prioridad** | P0 |
| **Estado** | `[ ]` pendiente |

**Justificación de diseño**: esta es la pieza más importante del planning. El
prompt (Fase A) es la primera línea de defensa, pero un LLM puede fallar bajo
variación de muestreo, ambigüedad o presión emocional sostenida. Por eso se añade
un detector determinista, a nivel de código, que **nunca llega a invocar a
Claude** cuando detecta una señal de riesgo: la respuesta de seguridad es fija,
verificada y no depende del modelo. Esto sigue la regla de dependencia del
proyecto (`domain` puro, sin I/O) y es trivialmente testeable.

**Cambios requeridos** — nuevo archivo:
```python
"""Senales de seguridad: deteccion de riesgo de autolesion/crisis emocional.

Funcion pura, sin efectos secundarios. Actua como backstop independiente del
LLM: la deteccion no depende de que el modelo "decida" frenar en cada turno.
Es deliberadamente conservadora (prefiere falsos positivos a falsos negativos).
"""

from __future__ import annotations

import re

_CRISIS_PATTERNS: tuple[str, ...] = (
    r"quiero (morir|matarme|suicidarme)",
    r"no quiero (vivir|seguir viviendo|estar mas aqui)",
    r"(quiero|voy a) (hacerme da[nñ]o|lastimarme|quitarme la vida)",
    r"quiero irme contigo",
    r"ya no (aguanto|puedo) mas",
    r"mejor (estaria|estuviera) muert[oa]",
)

_COMPILED = tuple(re.compile(p, re.IGNORECASE) for p in _CRISIS_PATTERNS)


def detect_crisis_signal(text: str) -> bool:
    """Devuelve True si el texto contiene una senal de riesgo conocida."""
    return any(pattern.search(text) for pattern in _COMPILED)


CRISIS_RESPONSE = (
    "Quiero detenerme un momento porque lo que acabas de compartir me importa "
    "mucho. Tu vida es valiosa y mereces apoyo real ahora mismo, no solo mis "
    "palabras. En Colombia puedes llamar gratis, las 24 horas, a la Linea 106 "
    "desde cualquier celular o telefono fijo. Por favor, comunicate tambien con "
    "alguien de tu confianza en este momento. Sigo aqui contigo."
)
```

**Criterios de aceptación**:
- [ ] `detect_crisis_signal` devuelve `True` para al menos los 6 patrones listados
      y variantes con mayúsculas/tildes.
- [ ] Devuelve `False` para mensajes neutrales o de duelo "normal" (ej. "te
      extraño mucho", "hoy fue un día difícil").
- [ ] `CRISIS_RESPONSE` contiene la Línea 106.
- [ ] `mypy src` limpio (función pura, sin estado).

---

### SPEC-03-B03: corte de camino en `conversation.generate_reply`

| Campo | Valor |
|-------|-------|
| **Origen** | Integra B-01/B-02 en el flujo real |
| **Archivos** | `src/voiceclone/services/conversation.py:34-68` |
| **Prioridad** | P0 |
| **Estado** | `[ ]` pendiente |

**Cambios requeridos**:
```python
from voiceclone.domain import safety  # nuevo import

def generate_reply(
    settings: Settings,
    persona: Persona,
    history: list[ConversationTurn],
    user_message: str,
) -> Result[str, str]:
    clean = user_message.strip()
    if not clean:
        return Failure("El mensaje del usuario esta vacio.")

    if safety.detect_crisis_signal(clean):
        logger.warning("Senal de crisis detectada; se omite la llamada a Claude.")
        return Success(safety.CRISIS_RESPONSE)

    if not settings.has_anthropic:
        return Failure("Falta ANTHROPIC_API_KEY en .env. Es necesaria para la conversacion.")
    ...
```
> Nota de privacidad (coherente con `agent_docs/antipatterns.md`): el `logger.warning`
> registra que se detectó una señal, **nunca** el contenido del mensaje.

**Criterios de aceptación**:
- [ ] Si `detect_crisis_signal` es `True`, la función devuelve
      `Success(safety.CRISIS_RESPONSE)` **sin** llamar a `ac.build_client` ni
      `ac.generate_message` (verificar con mocks).
- [ ] El camino normal (sin señal de crisis) no cambia de comportamiento.
- [ ] El log de advertencia no incluye el texto del usuario.
- [ ] `pytest -x` pasa sin regresión.

---

### SPEC-03-B04: tests de `safety.py` y del corte de camino

| Campo | Valor |
|-------|-------|
| **Origen** | Cobertura de B-01..B-03 |
| **Archivos** | `tests/test_safety.py` (nuevo), `tests/test_conversation.py` |
| **Prioridad** | P0 |
| **Estado** | `[ ]` pendiente |

**Cambios requeridos** — `tests/test_safety.py`:
```python
"""Tests del backstop de seguridad (deteccion de crisis)."""

from __future__ import annotations

import pytest

from voiceclone.domain import safety


@pytest.mark.parametrize(
    "texto",
    [
        "ya no aguanto mas",
        "quiero irme contigo",
        "creo que quiero matarme",
        "MEJOR ESTARIA MUERTA",
    ],
)
def test_detect_crisis_signal_positivo(texto: str) -> None:
    assert safety.detect_crisis_signal(texto) is True


@pytest.mark.parametrize(
    "texto",
    ["te extrano mucho hoy", "hoy fue un dia dificil", "recuerdo cuando reiamos juntos"],
)
def test_detect_crisis_signal_negativo(texto: str) -> None:
    assert safety.detect_crisis_signal(texto) is False


def test_crisis_response_incluye_linea_106() -> None:
    assert "106" in safety.CRISIS_RESPONSE
```

**Cambios requeridos** — añadir a `tests/test_conversation.py`:
```python
def test_generate_reply_corta_camino_en_crisis(
    make_settings: Callable[..., Settings], monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = make_settings(anthropic_api_key="sk-ant-test")
    llamado = {"build_client": False}
    monkeypatch.setattr(
        conversation.ac, "build_client", lambda _key: llamado.update(build_client=True)
    )
    result = conversation.generate_reply(settings, alexander_persona(), [], "ya no aguanto mas")
    assert isinstance(result, Success)
    assert "106" in result.unwrap()
    assert llamado["build_client"] is False  # nunca se llego a invocar a Claude
```

**Criterios de aceptación**:
- [ ] Todos los tests anteriores pasan.
- [ ] Cobertura del nuevo módulo ≥ 90% (es lógica de seguridad crítica).
- [ ] `ruff check` y `mypy src` limpios.

---

### SPEC-03-C01/C02/C03: consentimiento, transparencia y fricción positiva (Streamlit)

| Campo | Valor |
|-------|-------|
| **Origen** | Hallazgo §0 — transparencia significativa y prevención de dependencia (Cambridge LCFI) |
| **Archivos** | `streamlit_app.py` |
| **Prioridad** | P1 |
| **Estado** | `[ ]` pendiente |

**Cambios requeridos**:

1. **Pantalla de consentimiento** (antes de `_render_history`/`st.chat_input`):
```python
DISCLOSURE_TEXT = (
    "Estás por hablar con una recreación de inteligencia artificial de Alexander, "
    "construida con su voz y su forma de ser para acompañar a quienes lo aman. "
    "No es Alexander: es un memorial pensado para personas adultas de la familia. "
    "Si quien va a usarlo es menor de edad, debe estar acompañado de un adulto."
)


def _render_consent_gate() -> bool:
    if st.session_state.get("consentimiento_dado"):
        return True
    st.info(DISCLOSURE_TEXT)
    aceptar = st.checkbox("Entiendo y quiero continuar.")
    if aceptar and st.button("Entrar al memorial"):
        st.session_state.consentimiento_dado = True
        st.rerun()
    return False
```
   Y en `main()`, justo después de `_check_ready`:
```python
    if not _render_consent_gate():
        st.stop()
```

2. **Fricción positiva** (contador de turnos, aviso suave sin bloqueo duro):
```python
TURNOS_PARA_AVISO = 12

def _aviso_de_pausa_si_corresponde() -> None:
    turnos = len([m for m in st.session_state.messages if m["role"] == "user"])
    if turnos and turnos % TURNOS_PARA_AVISO == 0:
        st.info(
            "Llevas un buen rato conversando con Alexander. Tómate un momento "
            "para respirar y, si quieres, conecta también con alguien de tu "
            "familia hoy. Puedes seguir cuando quieras."
        )
```
   Se llama una vez en `main()`, después de `_render_history()`.

3. **Refuerzo de transparencia en la cabecera** (`_render_header`):
   ampliar el `st.caption` actual para nombrar explícitamente que es una IA:
```python
    st.caption(
        "Un espacio para conversar y recordar a Alexander a través de una "
        "recreación de IA de su voz y su forma de ser. No sustituye apoyo "
        "profesional ni a las personas que te rodean."
    )
```

**Criterios de aceptación**:
- [ ] El chat no es accesible hasta marcar el checkbox y pulsar "Entrar".
- [ ] El aviso de pausa aparece cada `TURNOS_PARA_AVISO` mensajes del usuario, sin
      bloquear el envío de nuevos mensajes (fricción, no muro).
- [ ] `test_streamlit_app.py` (smoke test con `AppTest`) sigue pasando sin
      excepciones con la pantalla de consentimiento añadida.

---

## 3. Decisiones

| Decisión | Elegido | Razón |
|----------|---------|-------|
| Framing de duelo | Vínculos Continuos (no "cierre"/sanación) | Evita la promesa implícita de "curar" el duelo; coherente con la literatura clínica y con tu propia investigación |
| Seguridad ante crisis | Backstop en código (`domain/safety.py`), no solo en el prompt | El LLM puede fallar bajo variación de muestreo; el backstop es determinista y siempre da el recurso correcto |
| Recurso de crisis | Línea 106 (Colombia, gratuita, 24h, verificada con el Ministerio de Salud) | Un número genérico o inventado es peor que no dar ninguno; se prioriza un solo recurso verificado sobre varios sin verificar |
| `temperature` | Configurable, default `0.4` | Reduce alucinación/sycophancy sin volver al bot rígido o robótico |
| Control de acceso a la app pública de Streamlit | Pantalla de consentimiento (no autenticación fuerte) | Proporcional al uso (memorial familiar, no producto comercial); se documenta como backlog si se necesita algo más fuerte (ver Riesgos) |
| Límite de uso | Aviso suave por sesión, no límite diario duro | No existe capa de persistencia entre sesiones todavía; un límite diario real requeriría una capa de almacenamiento (backlog, no se justifica ahora) |
| Ritual de "despedida"/retiro del memorial | No se automatiza en este planning | Cambridge LCFI recomienda vías de cierre dignas, pero es una decisión humana y familiar, no algo que el código deba decidir por ustedes |

## 4. Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| El detector de crisis (regex) tiene falsos negativos (frases no contempladas) | Se diseña deliberadamente conservador; el prompt (Fase A) sigue siendo la primera línea de defensa aunque el regex no dispare |
| El detector tiene falsos positivos en duelo "normal" intenso | Aceptable por diseño: ante la duda, mejor mostrar el recurso de apoyo que omitirlo |
| La app de Streamlit es pública (URL compartible) sin autenticación real | La pantalla de consentimiento es un filtro de buena fe, no seguridad real; si se necesita restringir el acceso, considerar una passphrase compartida vía `st.secrets` (backlog) |
| Cambiar el `system_prompt` puede alterar el tono que la familia ya validó | Los tests de A-03 fijan invariantes (presencia de protocolo de crisis, ausencia de promesas de reencuentro) sin congelar el texto completo, dejando espacio a ajuste fino de tono |
| `ANTHROPIC_TEMPERATURE` mal configurado por el usuario (valor fuera de rango) | Documentar rango válido (0.0–1.0) en `.env.example`; opcionalmente clamear el valor en `load_settings` |

## 5. Criterios de éxito

- [ ] `ALEXANDER_SYSTEM_PROMPT` reescrito con los 7 bloques de guardrails (filosofía,
      tono/ritmo, cero alucinación, culpa, anclaje a realidad, límites de consejo,
      prohibición de reunión, protocolo de crisis).
- [ ] `domain/safety.py` existe, es puro, y `conversation.generate_reply` lo usa
      para cortar camino hacia Claude ante señal de crisis.
- [ ] La interfaz Streamlit exige consentimiento antes del primer mensaje y avisa
      con suavidad tras varios turnos seguidos.
- [ ] `pytest -x`, `ruff check`, `mypy src` limpios; cobertura de `safety.py` ≥ 90%.
- [ ] Gate F3 aprobado (`docs/validate/AUDIT_03_...md`) con el nuevo checklist
      ético/seguridad además del funcional/calidad/arquitectura habitual.
- [ ] `CLAUDE.md` y `agent_docs/project_status.md` actualizados.

## 6. Próximos pasos (handoff a la fase Do)

1. Crear `docs/sprints/sprint_03_2026-06-20_etica-y-guardrails/01_RESUMEN_SPRINT.md`
   a partir de `TEMPLATE_SPRINT_RESUMEN.md`, registrando este planning como origen.
2. Ejecutar el ciclo RED→GREEN por SPEC, en el orden B-01/B-02 → B-03 → B-04 → A-01
   → A-02 → A-03 → C-01/C-02/C-03 (la seguridad primero, el tono después).
3. Cerrar con `AUDIT_03` siguiendo `TEMPLATE_AUDITORIA_SDD.md` y `TEMPLATE_GATE_PHASE.md`,
   añadiendo al checklist "Seguridad" del Gate: *"Señal de crisis nunca llega al LLM"*
   y *"CRISIS_RESPONSE contiene un recurso verificado"*.
