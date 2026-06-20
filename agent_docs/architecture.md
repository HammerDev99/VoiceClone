# architecture.md — Cómo está construido

> Nivel 2. Descriptivo.

## Capas y dependencias

```
            ┌─────────────┐
   scripts/ │  01..04     │  entrypoints (ajustan sys.path)
            └──────┬──────┘
                   ▼
            ┌─────────────┐
       cli/ │ main, console│  presentación: comandos cmd_*, salida al usuario
            └──────┬──────┘
                   ▼
   services/ ┌───────────────────────────────────────────┐
            │ voice_cloning · speech_synthesis · conversation │  orquestación
            └──────┬───────────────────────┬──────────────┘
                   ▼                        ▼
 infrastructure/ ┌──────────────────┐   ┌──────────────────┐
                │ elevenlabs_client │   │ anthropic_client │   boundaries (SDK + Result)
                │ logging          │   └──────────────────┘
                └──────────────────┘
                   ▼
        domain/ ┌──────────────────────┐   config/ ┌──────────┐
               │ models (DTOs) · persona│         │ settings │
               └──────────────────────┘          └──────────┘
```

**Regla de dependencia**: las capas superiores dependen de las inferiores,
nunca al revés. `domain` no depende de nada del proyecto. `infrastructure`
aísla los SDK externos y devuelve siempre `Result`.

## Flujo: clonar voz

```
02_clonar_voz.py → cli.cmd_clone → _setup (settings + cliente EL)
  → services.voice_cloning.clone_voice
      → discover_samples(audios/)         # valida .m4a/.mp3/...
      → el.create_instant_voice(...)      # IVC, abre archivos binarios
      → settings.save_voice_id(...)       # persiste en .env
```

## Flujo: conversar (persona + voz)

```
04_conversar.py → cli.cmd_converse → _setup
  loop:
    usuario escribe → services.conversation.generate_reply
        → ac.build_client + ac.generate_message   # Claude + system prompt (persona)
    respuesta texto → services.speech_synthesis.synthesize
        → el.text_to_speech → guarda output/*.mp3
    historial = [*historial, turno_user, turno_assistant]   # inmutable
```

## Decisiones clave

| Decisión | Razón |
|----------|-------|
| IVC (no PVC) | Funciona con pocas muestras `.m4a`; disponible en plan starter. |
| `eleven_multilingual_v2` | Mejor calidad multilingüe (español). |
| Claude para la persona | Capa conversacional con system prompt; modelo más capaz del entorno. |
| Dos clientes en `infrastructure/` | Simetría y DIP: aísla ambos SDK, facilita testeo (corrección H-01). |
| `Result[T, str]` | Errores explícitos sin excepciones para flujo normal. |
| `sys.path` en scripts | Evita instalar el paquete; tests usan `pythonpath=["src"]`. |

## Modelo de datos (DTOs, todos `frozen`)

`VoiceSample`, `ClonedVoice`, `SpeechRequest`, `GeneratedSpeech`,
`ConversationTurn`, `AccountInfo`, `VoiceTuning`. Ver `src/voiceclone/domain/models.py`.

## Canales de presentación (reutilizan `services/`)

El núcleo (`domain` + `infrastructure` + `services`) es agnóstico del canal. Sobre
él se montan distintas "caras":

| Canal | Entrypoint | Estado |
|-------|-----------|:------:|
| **Terminal** | `cli/` + `scripts/01..06` | ✅ |
| **Web** (familia) | `streamlit_app.py` (Streamlit) — chat + voz + selector de preset | ✅ desplegado |
| **WhatsApp** (futuro) | backend FastAPI con webhook → reutiliza `conversation` + `speech_synthesis` | 🗺️ roadmap (Twilio) |

**Principio clave**: añadir un canal nuevo (p.ej. WhatsApp) **no** toca el núcleo;
solo se escribe un adaptador de entrada/salida que llama a los servicios existentes.
El canal WhatsApp requerirá un servicio con **webhook público** (Streamlit no sirve
para webhooks). Ver `agent_docs/project_status.md` → Roadmap.

## Afinado de voz (calidad)

`domain/voice_presets.py` define presets (`VoiceTuning`) validados a oído
(`calido_sereno`, `natural`). `speech_synthesis.synthesize` acepta un `tuning`
explícito o resuelve el preset por defecto de `settings.voice_preset`. La app web
permite elegirlo en vivo.
