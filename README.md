# CV profesional - Demetrio Tahoces

Repositorio del CV profesional de Demetrio Tahoces, publicado como sitio estático en GitHub Pages y complementado con un chatbot RAG desplegable en Vercel.

## Qué contiene

- `index.html`: página principal del CV.
- `CV/`: páginas HTML detalladas de experiencia, formación y proyectos.
- `CV/chatbot.html`: interfaz web del asistente del CV.
- `CV/chatbot-widget.js`: widget embebible del chatbot.
- `CV/Chatbot/`: backend FastAPI + LangChain del asistente (ver su README).
- `CV/Chatbot/docs/`: base de conocimiento Markdown del asistente.
- `llms.txt`: índice del sitio para LLMs, generado desde `CV/Chatbot/docs/`.
- `blog/`: blog técnico estático.
- `assets/`: recursos compartidos, como la tarjeta Open Graph; `assets/vendor/`, copias locales con versión fija de marked y DOMPurify.
- `404.html`, `robots.txt` y `sitemap.xml` (generado con `python3 scripts/build_sitemap.py`).

## Arquitectura

El proyecto combina dos superficies independientes:

1. Frontend estático servido por GitHub Pages.
2. Backend serverless en Vercel para el chatbot del CV.

La parte pública no tiene proceso de build. Los HTML usan estilos y scripts compartidos en `assets/`; las utilidades de Tailwind están en `assets/tailwind.css`, generado con `python3 scripts/build_tailwind.py` y versionado (solo hay que regenerarlo al usar una utilidad nueva; `scripts/check_css.py` lo detecta). Desde CDN solo se cargan Google Fonts y Phosphor Icons (versión fija con `integrity`); marked.js y DOMPurify, que pintan y sanean el HTML del modelo en el chat, son copias locales con versión fija en `assets/vendor/`.

El chatbot usa FastAPI y LangChain (`create_agent`) con Claude Haiku 5.5 (`claude-haiku-5-5`). El CV completo y los artículos del blog van en el primer mensaje como bloques `search_result` cacheados, uno por sección con su URL; si el blog no cabe en `BLOG_IN_PROMPT_MAX_CHARS`, va su índice y los artículos se leen con una herramienta. También expone un servidor MCP de solo lectura en `/api/mcp`; el botón «MCP» de `CV/chatbot.html` abre un modal con la URL y el comando de Claude Code para copiarlos.

## Desarrollo local del frontend

Desde la raíz del repositorio:

```powershell
python -m http.server 8000
```

Después abre:

```text
http://localhost:8000/
```

Páginas útiles:

- `http://localhost:8000/index.html`
- `http://localhost:8000/CV/chatbot.html`
- `http://localhost:8000/blog/`

## Backend del chatbot

Toda la documentación del asistente (arquitectura, endpoints, configuración, tests y evals) está en [CV/Chatbot/README.md](CV/Chatbot/README.md).

Arranque rápido desde `CV/Chatbot`:

```powershell
uv sync
uv run uvicorn api.index:app --reload --port 3000
uv run pytest
```

## Despliegue

### Frontend

El frontend se despliega con GitHub Pages. Un push a `main` publica los archivos estáticos en:

```text
https://demetriotahoces.github.io/
```

No hay paso de build, bundler ni generación de assets. Lo único generado y versionado son `assets/tailwind.css` y `sitemap.xml`, y `scripts/check_all.py` falla si alguno no está al día.

### Backend

El backend se despliega en Vercel (preset FastAPI, raíz `CV/Chatbot`, dependencias desde `pyproject.toml` + `uv.lock`). Cada PR genera un preview y `main` publica en producción. No añadas rewrites hacia `api/index.py`: FastAPI recibiría la ruta reescrita y respondería 404.

Variables de entorno en Vercel: al menos `API_KEY` y `MODEL_NAME`. Lista completa en [CV/Chatbot/README.md](CV/Chatbot/README.md#configuración).

## Mantenimiento del contenido

Cuando se cambie contenido curricular, conviene mantener sincronizadas estas superficies:

- `index.html`
- páginas detalladas de `CV/*.html`
- documentos Markdown de `CV/Chatbot/docs/*.md`
- `assets/CV-Demetrio-Tahoces.pdf` (descargable desde la cabecera): se genera desde la hoja `@media print` de `index.html`. Regenéralo tras cualquier cambio de contenido con el servidor local levantado (`python -m http.server 8000`):

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 --print-to-pdf="$PWD\assets\CV-Demetrio-Tahoces.pdf" "http://localhost:8000/"
```

- `assets/CV-Demetrio-Tahoces-Profesional.pdf`: CV resumido de una página, de una sola columna y apto para ATS. Su fuente es `CV/cv-profesional.html` (`noindex`). Tras editarla, comprueba que sigue cabiendo en una página y regenera el PDF:

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 --user-data-dir="$env:TEMP\edgecv" --print-to-pdf="$PWD\assets\CV-Demetrio-Tahoces-Profesional.pdf" "file:///$((Resolve-Path CV\cv-profesional.html).Path -replace '\\','/')"
```

El chatbot responde a partir de la base documental Markdown. Si una experiencia, tecnología o formación aparece en la web pública pero no en `CV/Chatbot/docs/`, el asistente puede no conocerla o responder de forma incompleta. Tras cambiar documentos, regenera `llms.txt` con `uv run python -m core.llms_txt` desde `CV/Chatbot`.

## Convenciones del repositorio

- Mantener el frontend como HTML estático, con el CSS y JS compartidos en `assets/` (ver `AGENTS.md`).
- No introducir un sistema de build frontend salvo decisión explícita.
- Evitar dependencias nuevas para cambios puramente visuales o de contenido.
- Mantener el contenido en castellano profesional, concreto y verificable.
- Revisar enlaces internos y rutas relativas después de mover páginas o assets.
