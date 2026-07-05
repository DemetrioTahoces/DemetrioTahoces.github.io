# CV profesional - Demetrio Tahoces

Repositorio del CV profesional de Demetrio Tahoces, publicado como sitio estático en GitHub Pages y complementado con un chatbot RAG desplegable en Vercel.

## Qué contiene

- `index.html`: página principal del CV.
- `CV/`: páginas HTML detalladas de experiencia, formación y proyectos.
- `CV/chatbot.html`: interfaz web del asistente del CV.
- `CV/chatbot-widget.js`: widget embebible del chatbot.
- `CV/Chatbot/`: backend FastAPI + LangGraph del asistente.
- `CV/Chatbot/docs/`: base documental Markdown usada como contexto RAG.
- `blog/`: blog técnico estático.
- `FundamentosIA/`: página estática sobre estrategia de adopción de IA.
- `assets/`: recursos compartidos, como la tarjeta Open Graph.

## Arquitectura

El proyecto combina dos superficies independientes:

1. Frontend estático servido por GitHub Pages.
2. Backend serverless en Vercel para el chatbot del CV.

La parte pública no tiene proceso de build. Los HTML usan estilos y scripts inline, con dependencias cargadas desde CDN, principalmente Tailwind CSS, Google Fonts, Chart.js, Phosphor Icons y marked.js.

El chatbot usa FastAPI, LangGraph y LangChain. Expone endpoints bajo `/api/*` y consulta los documentos Markdown de `CV/Chatbot/docs/` mediante herramientas internas de lectura y búsqueda.

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
- `http://localhost:8000/FundamentosIA/`

## Desarrollo local del backend del chatbot

Desde `CV/Chatbot`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api.index:app --reload --host 0.0.0.0 --port 3000
```

Health check:

```text
http://localhost:3000/api/health
```

Documentación OpenAPI local:

```text
http://localhost:3000/api/docs
```

## Variables de entorno

El backend lee configuración desde variables de entorno o desde un archivo `.env` en `CV/Chatbot`.

Variables principales:

| Variable | Obligatoria | Valor por defecto | Descripción |
| --- | --- | --- | --- |
| `API_KEY` | Sí | Vacío | API key del proveedor LLM configurado. |
| `PROVIDER_NAME` | No | `gemini` | Proveedor del modelo. Valores esperados: `gemini` u `openai`. |
| `MODEL_NAME` | No | `gemini-2.5-flash-lite` | Modelo usado por el agente. |
| `RATE_LIMIT_PER_MINUTE` | No | `5` | Límite de peticiones por minuto. |
| `RATE_LIMIT_PER_HOUR` | No | `20` | Límite de peticiones por hora. |
| `ALLOWED_ORIGINS` | No | GitHub Pages y localhost | Orígenes permitidos para CORS. |
| `LOG_LEVEL` | No | `INFO` | Nivel de logging. |
| `DOCS_PATH` | No | `docs` | Ruta relativa a los documentos Markdown del RAG. |

Ejemplo mínimo:

```env
API_KEY=tu_api_key
PROVIDER_NAME=gemini
MODEL_NAME=gemini-2.5-flash-lite
```

## Endpoints del chatbot

- `GET /api/health`: comprueba estado del servicio y documentos cargados.
- `POST /api/chat`: devuelve una respuesta completa en JSON.
- `POST /api/chat/stream`: devuelve respuesta en streaming mediante SSE.

Ejemplo de petición:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:3000/api/chat `
  -ContentType 'application/json' `
  -Body '{"message":"Resume la experiencia de Demetrio en backend","session_id":"local"}'
```

## Comprobaciones

Hay scripts de comprobación del backend en `CV/Chatbot/test/`.

Desde `CV/Chatbot`:

```powershell
python test/test_rate_limit.py
```

Para probar el agente contra el proveedor LLM configurado:

```powershell
python test/test_agent.py
```

Esta segunda comprobación requiere `API_KEY` válida y puede consumir tokens del proveedor configurado.

## Despliegue

### Frontend

El frontend se despliega con GitHub Pages. Un push a `main` publica los archivos estáticos en:

```text
https://demetriotahoces.github.io/
```

No hay paso de build, bundler ni generación de assets.

### Backend

El backend del chatbot se despliega en Vercel usando:

```text
CV/Chatbot/vercel.json
```

Las rutas `/api/*` se reescriben hacia `api/index.py`.

En Vercel deben configurarse las variables de entorno necesarias, especialmente `API_KEY`, `PROVIDER_NAME` y `MODEL_NAME` si se quiere sobrescribir el modelo por defecto.

## Mantenimiento del contenido

Cuando se cambie contenido curricular, conviene mantener sincronizadas estas superficies:

- `index.html`
- páginas detalladas de `CV/*.html`
- documentos Markdown de `CV/Chatbot/docs/*.md`

El chatbot responde a partir de la base documental Markdown. Si una experiencia, tecnología o formación aparece en la web pública pero no en `CV/Chatbot/docs/`, el asistente puede no conocerla o responder de forma incompleta.

## Convenciones del repositorio

- Mantener el frontend como HTML estático con CSS y JS inline.
- No introducir un sistema de build frontend salvo decisión explícita.
- Evitar dependencias nuevas para cambios puramente visuales o de contenido.
- Mantener el contenido en castellano profesional, concreto y verificable.
- Revisar enlaces internos y rutas relativas después de mover páginas o assets.
