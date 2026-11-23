# .agents

Mapa de lo que usan los agentes de coding en este repositorio (Claude Code, Codex, Antigravity). Las instrucciones generales están en `AGENTS.md`; aquí, dónde vive cada cosa y qué puerta la valida.

## Originales y copias

| Qué | Original (se edita aquí) | Copia o derivado | Cómo se genera |
|---|---|---|---|
| Skills | `.agents/skills/<skill>/` | `.claude/skills/<skill>/` | `python3 scripts/sync_skills.py` |
| Agentes | `.agents/agents/<agente>.md` | `.claude/agents/<agente>.md` (Claude Code), `.codex/agents/<agente>.toml` (Codex) | `python3 scripts/sync_skills.py` |
| Entorno cloud (Antigravity) | `.agents/environment.json` | no hay | lo ejecuta la VM al arrancar (`poppler-utils`, hook git, `puppeteer-core`, `uv sync`) |
| Hooks (Antigravity) | `.agents/hooks.json` | no hay | `SessionStart` activa `.githooks`; `PreToolUse` sobre `run_command` lanza `pre_push_gate.py` |
| Antigravity | Lee `AGENTS.md`, `.agents/skills/`, `.agents/hooks.json` y `.agents/environment.json` directamente; los agentes de `.agents/agents/*.md` los registra el orquestador con `define_subagent` + `invoke_subagent` | no hay | no aplica |

Las copias no se editan a mano. Tras tocar un original, ejecuta `sync_skills.py` y commitea original y copias juntos.

## Skills y agentes

- `edit-cv`: contenido curricular. Validador: `.agents/skills/edit-cv/scripts/check_cv.py`.
- `manage-blog`: artículos. Delega la redacción en el agente `blog-writer`. Validadores y scripts: `.agents/skills/manage-blog/scripts/` (detalle en `references/automatizacion.md`).
- `blog-writer`: Opus con effort medium en Claude Code. Para Codex y Antigravity, tabla de modelos e invocación en el propio agente.

## Scripts transversales (`scripts/`)

| Script | Qué hace |
|---|---|
| `build_cv_pdfs.py` | Regenera los dos CV en PDF (`assets/CV-Demetrio-Tahoces.pdf` y `assets/CV-Demetrio-Tahoces-Profesional.pdf`) en Linux/Antigravity, macOS y Windows usando Chrome/Chromium/Edge headless, comprueba 1 página en el profesional y lanza `check_cv_pdf.py`. |
| `check_cv_pdf.py` | Compara la web con el CV resumido y el texto de los dos PDF (puestos, fechas, formación, cifras, orden de lectura ATS). Necesita `pdftotext`. |
| `check_all.py [--tests]` | Puerta única: blog, CV, CV web vs PDF, CSS, sitemap y copias derivadas. `--tests` añade los tests offline del chatbot (requiere `uv`). Nunca lanza evals. |
| `sync_skills.py [--check]` | Genera y comprueba las copias de skills y agentes. |
| `pre_push_gate.py` | Hook PreToolUse de Claude Code y Antigravity: ejecuta `check_all.py` ante un push desde el agente. |
| `install_hooks.py` | Activa `core.hooksPath=.githooks` en el clon (`--json` para `SessionStart` de Antigravity). |
| `build_sitemap.py [--check]` | Genera `sitemap.xml` desde los canonical de las páginas; `--check` (en `check_all.py`) falla si no está al día. |

## Puertas de validación

| Puerta | Cubre | Cuándo |
|---|---|---|
| Hook de Claude Code (`.claude/settings.json`) | Solo Claude Code | Antes de un push desde el agente; en `SessionStart` activa el hook de git |
| Hook de Antigravity (`.agents/hooks.json`) | Antigravity (local y cloud) | Antes de un push en `run_command`; en `SessionStart` activa el hook de git |
| Hook de git (`.githooks/pre-push`) | Cualquier agente o push manual | Antes de cada push, una vez ejecutado `scripts/install_hooks.py` (automático en Claude Code y Antigravity vía `SessionStart`, y en Antigravity cloud vía `.agents/environment.json`). Saltar: `--no-verify` |
| CI (`blog.yml`, `cv.yml`, `chatbot.yml`) | Todo | Después del push; avisa tarde porque aquí se publica directo a `main` |

Evals: solo las ejecuta un humano (`AGENTS.md`).
