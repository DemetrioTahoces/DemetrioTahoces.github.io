# AGENTS.md

Instrucciones de trabajo para agentes que modifiquen este repositorio.

## Perfil del usuario

- El usuario prefiere respuestas en castellano.
- Valora respuestas directas, críticas y realistas.
- Tiene perfil de ingeniería software con foco backend y telecomunicaciones.
- Le interesan especialmente DDD, Arquitectura Hexagonal, CQRS, microservicios, Kubernetes, Docker, IA, agentes, RAG, MCP, evaluación de LLMs, emprendimiento, software, IoT e inversiones.
- Si hay supuestos débiles, incoherencias o riesgos técnicos, indícalos explícitamente.

## Resumen del repositorio

- Tipo: sitio estático de CV profesional publicado en GitHub Pages, más backend serverless para un chatbot RAG.
- URL pública principal: `https://demetriotahoces.github.io/`.
- Frontend: HTML estático sin build step. El CSS/JS compartido vive en `assets/` (`tokens.css`, `cv.css`, `blog.css`, `cv.js`); inline solo quedan el gate `motion-ready`, el favicon y los metadatos de cada página.
- Backend: FastAPI + LangChain (`create_agent`) en `CV/Chatbot/`, desplegado en Vercel. Documentación completa en `CV/Chatbot/README.md`.
- Base de conocimiento: documentos Markdown con frontmatter en `CV/Chatbot/docs/`.

## Estructura relevante

- `index.html`: página principal del CV.
- `CV/*.html`: páginas detalladas de experiencia, formación y proyectos.
- `CV/chatbot.html`: interfaz web del asistente del CV.
- `CV/chatbot-widget.js`: widget del chatbot.
- `CV/Chatbot/api/index.py`: entrada FastAPI serverless.
- `CV/Chatbot/core/`: configuración, conocimiento (`knowledge.py`), agente, prompts, tool `read_blog_article`, servidor MCP, tracing y generador de `llms.txt`.
- `CV/Chatbot/middleware/`: logging, rate limiting y bloqueo temporal por abuso (`abuse_guard.py`, store Upstash Redis, fail-open).
- `CV/Chatbot/docs/*.md`: documentos que alimentan el chatbot (frontmatter obligatorio).
- `CV/Chatbot/test/`: tests offline con pytest (modelo falso, sin API key).
- `CV/Chatbot/evals/`: dataset y evals contra el modelo real.
- `llms.txt`: índice del sitio para LLMs, generado desde `CV/Chatbot/docs/`.
- `.github/workflows/chatbot.yml`: CI del chatbot (solo tests offline).
- `.github/workflows/chatbot-evals.yml`: evals, solo con lanzamiento manual por un humano.
- `blog/`: blog técnico estático.
- `FundamentosIA/`: página estática sobre estrategia de adopción de IA.
- `assets/tokens.css`: design tokens (`:root`) de todo el sitio — colores, radios, sombras, `--font-body`/`--font-display`, `--shell-max`.
- `assets/cv.css`: estilos compartidos de `index.html` y `CV/*.html` (también los consume el blog): base, nav, cards, heroes, timeline de experiencia y el sistema de animación `data-reveal`.
- `assets/blog.css`: estilos específicos del blog (prosa de artículo, callout/warning, tablas, post-cards; fija `--shell-max: 64rem`).
- `assets/cv.js`: reveals con stagger sobre `[data-reveal]`/`[data-reveal-group]`, scroll-spy del nav, jump-nav (`[data-section-nav]`) y estado `.is-scrolled`.
- `assets/og-card.svg`: imagen Open Graph compartida.
- `README.md`: documentación operativa para humanos.

## Frontend

- Edita los HTML directamente.
- Patrón de estilos: los estilos y scripts compartidos viven en `assets/tokens.css` + `assets/cv.css` (+ `assets/blog.css` en el blog) + `assets/cv.js`, enlazados con query de versión (`?v=N`). Inline en cada HTML solo quedan el gate `motion-ready` en el `<head>`, el favicon y los metadatos. `CV/chatbot.html` mantiene su `<style>` propio pero consume `assets/tokens.css`.
- Cache-busting: GitHub Pages cachea ~10 minutos. Si cambias un fichero de `assets/*.css|js` de forma incompatible con el HTML, incrementa el `?v=N` de sus `<link>`/`<script>` en el mismo commit.
- Los colores salen SIEMPRE de los tokens (`var(--accent)`, etc.); no introduzcas colores nuevos hardcodeados.
- Tipografía: Space Grotesk (display: h1, h2, `.section-title`, `.site-brand`, h3 de cards) + Inter 300–800 (cuerpo), en una única petición a Google Fonts con `preconnect`.
- No introduzcas bundlers, `package.json`, frameworks frontend ni pasos de compilación salvo petición explícita.
- Las dependencias frontend se cargan por CDN, principalmente Tailwind CSS, Google Fonts (Inter y Space Grotesk), Chart.js, Phosphor Icons, marked.js y DOMPurify (sanitiza el markdown de la IA en el chatbot).
- Mantén el tono visual existente: tema oscuro, profesional, técnico y sobrio.
- Sistema de animación: marca elementos con `data-reveal` (variantes `fade`/`scale`/`line`; por defecto desliza 18px) y agrupa con `data-reveal-group` para stagger. `assets/cv.js` los revela con IntersectionObserver bajo el gate `html.motion-ready`; sin JS o con `prefers-reduced-motion` todo queda visible. Los efectos ligados al scroll (línea de trayectoria del timeline, parallax del hero) van solo bajo `@supports (animation-timeline: view())` con estado final estático como fallback.
- En animaciones de entrada por scroll, evita dejar contenido invisible hasta que esté demasiado dentro del viewport. El contenido debe empezar a revelarse prácticamente al entrar en pantalla, especialmente en móvil; prioriza continuidad visual sobre efectos de aparición llamativos.
- Revisa rutas relativas, enlaces internos, anclas, metadatos SEO/Open Graph y navegación cuando cambies páginas.

## Backend del chatbot

- Haz cambios backend dentro de `CV/Chatbot/`.
- Dependencias en `CV/Chatbot/pyproject.toml` con versiones fijadas en `uv.lock` (Python 3.14, `.python-version`). Tras cambiar dependencias ejecuta `uv lock` y commitea el lock.
- La configuración se lee desde variables de entorno o `CV/Chatbot/.env` mediante `CV/Chatbot/core/config.py`. Variables y valores por defecto: tabla en `CV/Chatbot/README.md` y plantilla en `.env.example` (modelo por defecto `gpt-6-luna`).
- Endpoints: `POST /api/chat/stream`, `POST /api/chat`, `POST /api/feedback`, `GET /api/health` y el servidor MCP de solo lectura en `POST /api/mcp`.
- El backend es stateless: el frontend envía los últimos mensajes en `history`. No reintroduzcas memoria en servidor (`MemorySaver`).
- El CV completo va en el system prompt (cacheado); los artículos del blog se leen con la tool `read_blog_article` (solo blog). Mantén el prompt estable y la fecha al final para no romper la caché.
- CORS se configura solo en FastAPI (`ALLOWED_ORIGINS`); no hay `vercel.json`. Vercel usa el preset FastAPI (entrypoint `api/index.py`). No añadas rewrites hacia `api/index.py`: FastAPI recibiría la ruta reescrita y respondería 404.

## Contenido curricular y RAG

Cuando se modifique información profesional, no actualices solo una superficie si el cambio afecta al contenido público y al chatbot.

Superficies que suelen requerir sincronización:

- `index.html`
- `CV/*.html`
- `CV/Chatbot/docs/*.md`
- `assets/CV-Demetrio-Tahoces.pdf` (se regenera desde la vista de impresión de `index.html`; comando en `README.md`)

Regla práctica: si una experiencia, tecnología, formación, responsabilidad o logro aparece en la web pública y el chatbot debería poder responder sobre ello, debe existir también una representación razonable en los documentos Markdown de `CV/Chatbot/docs/`.

Mantén el contenido en castellano profesional, concreto y defendible. Evita marketing vacío, claims inflados y listas de buzzwords sin evidencia.

Trazabilidad de las respuestas: cada encabezado `##`/`###` de `CV/Chatbot/docs/*.md` declara el `id` de la sección HTML que lo respalda (`## Contexto {#contexto}`) y el chatbot cita cada párrafo con esa URL. Si renombras, añades o quitas una sección en `index.html`, `CV/*.html` o `blog/posts/*.html`, actualiza el `id` y el ancla del Markdown a la vez; los `id` son estables (no los cambies aunque cambie el título). `uv run pytest` valida que cada ancla exista en su página.

Cada documento de `CV/Chatbot/docs/` lleva frontmatter YAML con `type` (`cv`, `formacion` o `blog_post`), `title`, `route` (ruta pública), `summary`, `tags` y `order` (CV/formación) o `date` (blog). Tras añadir o cambiar documentos, regenera `llms.txt` con `uv run python -m core.llms_txt` y ejecuta `uv run pytest` desde `CV/Chatbot` (un test valida el frontmatter y que `llms.txt` esté al día).

## Blog

- El blog está en `blog/`.
- El blog consume los assets compartidos (`tokens.css` + `cv.css` + `blog.css` + `cv.js`, rutas `../assets/` desde `blog/` y `../../assets/` desde `blog/posts/`). Los estilos de prosa de artículo viven en `assets/blog.css`, no inline.
- Si se añaden artículos que el chatbot deba conocer, añade o sincroniza también el contenido Markdown correspondiente bajo `CV/Chatbot/docs/`, normalmente en una subcarpeta si el patrón existente lo permite.

## Desarrollo local

Frontend desde la raíz:

```powershell
python -m http.server 8000
```

Backend desde `CV/Chatbot` (requiere `uv`):

```powershell
uv sync
uv run uvicorn api.index:app --reload --host 0.0.0.0 --port 3000
```

Comprobaciones backend desde `CV/Chatbot`:

```powershell
uv run pytest            # tests offline, sin API key
uv run pytest -m evals   # evals contra el modelo real: SOLO las ejecuta un humano (ver abajo)
```

**Evals: solo las ejecuta un humano, a mano.** Consumen tokens de pago en cada ejecución. Ningún agente (Claude Code incluido), pipeline de CI, hook, Routine ni automatización puede ejecutar `pytest -m evals` ni lanzar el workflow `chatbot-evals.yml`, tampoco para "verificar" un cambio. Si cambias el prompt, el modelo o los documentos, pide al humano que ejecute las evals y lo indicas en la PR. Sí puedes añadir o editar casos en `evals/dataset.yaml` (uno por cada fallo real detectado).

## Despliegue

- Frontend: push a `main` publica en GitHub Pages.
- Backend: desplegado en Vercel desde `CV/Chatbot/`.
- No hay build del frontend.
- CI solo para el chatbot: `.github/workflows/chatbot.yml` ejecuta solo los tests offline en PRs y pushes a `main`. Las evals están fuera del pipeline automático: `.github/workflows/chatbot-evals.yml` solo tiene `workflow_dispatch` y lo lanza un humano desde la pestaña Actions. El frontend no tiene CI ni build.

## Convenciones de edición

- Mantén los cambios acotados a la petición.
- No reestructures el proyecto salvo petición explícita.
- No elimines contenido curricular existente salvo instrucción clara.
- Usa rutas y nombres ya presentes en el repositorio.
- Añade comentarios solo cuando aclaren lógica no obvia.
- No introduzcas dependencias nuevas para cambios de contenido o presentación simple.
- Antes de cerrar una tarea, revisa que los enlaces/rutas afectadas sigan teniendo sentido.

## Instrucciones adicionales

Lo siguiente aplica solo al modo Cowork y no está cubierto por AGENTS.md.

- Ignora `.venv`, `CV/Chatbot/.venv`, `node_modules` y `__pycache__` en exploraciones, búsquedas o auditorías: son dependencias empaquetadas, no código propio del proyecto. Incluirlas satura resultados y contexto sin aportar nada.
- No ejecutes `git commit` ni `git push` salvo petición explícita. El usuario gestiona el historial y decide cuándo publicar.
- Antes de crear contenido nuevo, comprueba si ya existe una skill local aplicable en `.agents/skills/`: `edit-cv` para cambios de contenido curricular, `manage-blog` para artículos y assets de blog (incluye conversión SVG→PNG para drafts de LinkedIn). Úsalas en vez de reinventar el flujo.
- Edita los archivos finales directamente en su ruta real del repo (el HTML, el Markdown, los assets). El paso intermedio por la carpeta de outputs es solo para género de imágenes o borradores exploratorios que aún no tienen destino claro.
- Nunca leas, muestres ni copies el contenido de `CV/Chatbot/.env` — contiene la API key del proveedor LLM.
- `python -m http.server` y `uvicorn ... --reload` son solo para verificación manual puntual; no hay CI ni build. No los lances por defecto, solo si la tarea concreta lo requiere.