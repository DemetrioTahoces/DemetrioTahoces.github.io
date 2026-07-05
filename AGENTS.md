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
- Frontend: HTML estático con estilos y scripts inline. No hay build step.
- Backend: FastAPI + LangGraph + LangChain en `CV/Chatbot/`, desplegable en Vercel.
- Base RAG: documentos Markdown en `CV/Chatbot/docs/`.

## Estructura relevante

- `index.html`: página principal del CV.
- `CV/*.html`: páginas detalladas de experiencia, formación y proyectos.
- `CV/chatbot.html`: interfaz web del asistente del CV.
- `CV/chatbot-widget.js`: widget del chatbot.
- `CV/Chatbot/api/index.py`: entrada FastAPI serverless.
- `CV/Chatbot/core/`: configuración, agente, prompts y herramientas RAG.
- `CV/Chatbot/middleware/`: logging y rate limiting.
- `CV/Chatbot/docs/*.md`: documentos que alimentan el chatbot.
- `CV/Chatbot/test/`: scripts de comprobación del backend.
- `blog/`: blog técnico estático.
- `FundamentosIA/`: página estática sobre estrategia de adopción de IA.
- `assets/`: recursos compartidos.
- `README.md`: documentación operativa para humanos.

## Frontend

- Edita los HTML directamente.
- Mantén el patrón actual: CSS y JavaScript inline dentro de los HTML.
- No introduzcas bundlers, `package.json`, frameworks frontend ni pasos de compilación salvo petición explícita.
- Las dependencias frontend se cargan por CDN, principalmente Tailwind CSS, Google Fonts, Chart.js, Phosphor Icons y marked.js.
- Mantén el tono visual existente: tema oscuro, profesional, técnico y sobrio.
- Revisa rutas relativas, enlaces internos, anclas, metadatos SEO/Open Graph y navegación cuando cambies páginas.

## Backend del chatbot

- Haz cambios backend dentro de `CV/Chatbot/`.
- Las dependencias están en `CV/Chatbot/requirements.txt`.
- La configuración se lee desde variables de entorno o `.env` mediante `CV/Chatbot/core/config.py`.
- Variables relevantes:
  - `API_KEY`
  - `PROVIDER_NAME`
  - `MODEL_NAME`
  - `RATE_LIMIT_PER_MINUTE`
  - `RATE_LIMIT_PER_HOUR`
  - `ALLOWED_ORIGINS`
  - `LOG_LEVEL`
  - `DOCS_PATH`
- Endpoints principales:
  - `GET /api/health`
  - `POST /api/chat`
  - `POST /api/chat/stream`
- Vercel usa `CV/Chatbot/vercel.json` para reescribir `/api/*` hacia `api/index.py`.

## Contenido curricular y RAG

Cuando se modifique información profesional, no actualices solo una superficie si el cambio afecta al contenido público y al chatbot.

Superficies que suelen requerir sincronización:

- `index.html`
- `CV/*.html`
- `CV/Chatbot/docs/*.md`

Regla práctica: si una experiencia, tecnología, formación, responsabilidad o logro aparece en la web pública y el chatbot debería poder responder sobre ello, debe existir también una representación razonable en los documentos Markdown de `CV/Chatbot/docs/`.

Mantén el contenido en castellano profesional, concreto y defendible. Evita marketing vacío, claims inflados y listas de buzzwords sin evidencia.

## Blog

- El blog está en `blog/`.
- Mantén el estilo estático e inline del resto del proyecto.
- Si se añaden artículos que el chatbot deba conocer, añade o sincroniza también el contenido Markdown correspondiente bajo `CV/Chatbot/docs/`, normalmente en una subcarpeta si el patrón existente lo permite.

## Desarrollo local

Frontend desde la raíz:

```powershell
python -m http.server 8000
```

Backend desde `CV/Chatbot`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api.index:app --reload --host 0.0.0.0 --port 3000
```

Comprobaciones backend desde `CV/Chatbot`:

```powershell
python test/test_rate_limit.py
python test/test_agent.py
```

`test_agent.py` requiere `API_KEY` válida y puede consumir tokens del proveedor configurado.

## Despliegue

- Frontend: push a `main` publica en GitHub Pages.
- Backend: desplegado en Vercel desde `CV/Chatbot/`.
- No hay build del frontend.
- No asumas CI, linting o suite de tests automatizada en la raíz: no existe en este proyecto.

## Convenciones de edición

- Mantén los cambios acotados a la petición.
- No reestructures el proyecto salvo petición explícita.
- No elimines contenido curricular existente salvo instrucción clara.
- Usa rutas y nombres ya presentes en el repositorio.
- Añade comentarios solo cuando aclaren lógica no obvia.
- No introduzcas dependencias nuevas para cambios de contenido o presentación simple.
- Antes de cerrar una tarea, revisa que los enlaces/rutas afectadas sigan teniendo sentido.

