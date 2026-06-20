# Despliegue — Streamlit Community Cloud

> ✅ **Estado: desplegado con éxito** (2026-06-20). Esta guía documenta el
> procedimiento y sirve para re-desplegar o reproducir el despliegue.

La interfaz de la familia (`streamlit_app.py`) se despliega en
**Streamlit Community Cloud** (https://share.streamlit.io), el mismo patrón del
proyecto `disciplinajudicialai`: sin Docker, sin Procfile; solo el repo en
GitHub, `requirements.txt` y los secretos gestionados en la UI.

## Cómo funciona la configuración

- **Local**: la app lee las claves de `.env` (vía `python-dotenv`).
- **Nube**: no hay `.env`. Las claves se definen en *Secrets* (formato TOML) y la
  app las vuelca a variables de entorno mediante el puente `st.secrets → os.environ`
  (`_bridge_secrets_to_env` en `streamlit_app.py`). Así `load_settings()` funciona
  igual en ambos entornos.

## Requisitos previos

- La voz ya debe estar **clonada** (tienes `VOICE_ID`). El clonado se hace en
  local (`scripts/02_clonar_voz.py`); en la nube solo se conversa.
- Cuenta de GitHub y de Streamlit Community Cloud (gratuita).

## Pasos

### 1. Subir el proyecto a GitHub

```bash
git remote add origin https://github.com/<tu-usuario>/voiceclone.git
git push -u origin main
```

> `.env`, `audios/` y `output/` están en `.gitignore` y **no** se suben.
> Los secretos viajan solo por la UI de Streamlit, nunca por el repo.

### 2. Crear la app en Streamlit Community Cloud

1. Entra en https://share.streamlit.io e inicia sesión con GitHub.
2. *Create app* → *Deploy a public app from GitHub*.
3. Configura las **coordenadas**:
   - **Repository**: `<tu-usuario>/voiceclone`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`

### 3. Configurar los secretos

En *Advanced settings → Secrets* (o luego en *App → Settings → Secrets*), pega el
contenido de [`.streamlit/secrets.toml.example`](../.streamlit/secrets.toml.example)
con los **valores reales**:

```toml
ELEVENLABS_API_KEY = "sk_..."
ANTHROPIC_API_KEY = "sk-ant-..."
VOICE_ID = "YGZ9Wy0OURezjISirtC4"
VOICE_PRESET = "calido_sereno"
# (resto de claves de la plantilla)

# Opcional — analítica web (Umami): pega el snippet completo de tu panel.
ANALYTICS_SCRIPT = '<script defer src="https://analytics.sprintjudicial.com/script.js" data-website-id="747d8b89-4c3d-4b25-9b79-e538bd831bce"></script>'
```

> **Analítica (Umami)**: es opcional y solo se activa en la nube. La app lee el
> secreto `ANALYTICS_SCRIPT` y, si está presente, inyecta el `<script>` una sola
> vez en el `<head>` (extrae `src` y `data-website-id` del snippet). En local no
> hace falta; si el secreto no está, la analítica queda desactivada. Solo registra
> páginas vistas en Umami: **no** envía el contenido de las conversaciones.

### 4. Desplegar

Pulsa **Deploy**. En unos minutos tendrás una URL pública
(`https://<algo>.streamlit.app`) que puedes compartir con la familia.

## Mantenimiento

- **Actualizar la app**: haz `git push` a `main`; Community Cloud detecta el cambio
  y vuelve a desplegar automáticamente.
- **Cambiar secretos/voz/preset**: edítalos en *App → Settings → Secrets* (no
  requiere re-deploy).
- **Versión de Streamlit**: se resuelve desde `requirements.txt`.

## Notas

- El sistema de archivos en la nube es **efímero**: el audio que genera la app es
  temporal (se sirve en la sesión y se reproduce); no se conserva entre reinicios.
- Si el repo es privado, solo podrás tener una app privada gratuita; hazla pública
  para compartirla ampliamente.
- ⚠️ Rota las API keys que se hayan expuesto antes de hacer público el proyecto.
