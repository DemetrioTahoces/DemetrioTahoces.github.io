# .agents

Mapa de lo que usan los agentes de coding en este repositorio (Claude Code, Codex, Antigravity). Las instrucciones generales están en `AGENTS.md`; aquí, dónde vive cada cosa y qué puerta la valida.

## Originales y copias

| Qué | Original (se edita aquí) | Copia o derivado | Cómo se genera |
|---|---|---|---|
| Skills | `.agents/skills/<skill>/` | `.claude/skills/<skill>/` | `python3 scripts/sync_skills.py` |
| Agentes | `.agents/agents/<agente>.md` | `.claude/agents/<agente>.md` (Claude Code), `.codex/agents/<agente>.toml` (Codex) | `python3 scripts/sync_skills.py` |
| Antigravity | Lee `AGENTS.md`, `.agents/skills` y `.agents/agents` directamente | no hay | no aplica |

Las copias no se editan a mano. Tras tocar un original, ejecuta `sync_skills.py` y commitea original y copias juntos.

## Skills y agentes

- `edit-cv`: contenido curricular. Validador: `.agents/skills/edit-cv/scripts/check_cv.py`.
- `manage-blog`: artículos. Delega la redacción en el agente `blog-writer`. Validadores y scripts: `.agents/skills/manage-blog/scripts/` (detalle en `references/automatizacion.md`).
- `blog-writer`: Opus con effort medium en Claude Code. Para Codex y Antigravity, tabla de modelos en el propio agente.

## Scripts transversales (`scripts/`)

| Script | Qué hace |
|---|---|
| `check_all.py [--tests]` | Puerta única: blog, CV y copias derivadas. `--tests` añade los tests offline del chatbot (requiere `uv`). Nunca lanza evals. |
| `sync_skills.py [--check]` | Genera y comprueba las copias de skills y agentes. |
| `pre_push_gate.py` | Hook PreToolUse de Claude Code: ejecuta `check_all.py` ante un push desde el agente. |
| `install_hooks.py` | Activa `core.hooksPath=.githooks` en el clon. |

## Puertas de validación

| Puerta | Cubre | Cuándo |
|---|---|---|
| Hook de Claude Code (`.claude/settings.json`) | Solo Claude Code | Antes de un push desde el agente; en `SessionStart` activa el hook de git |
| Hook de git (`.githooks/pre-push`) | Cualquier agente o push manual | Antes de cada push, una vez ejecutado `scripts/install_hooks.py` (Claude Code lo hace solo). Saltar: `--no-verify` |
| CI (`blog.yml`, `cv.yml`, `chatbot.yml`) | Todo | Después del push; avisa tarde porque aquí se publica directo a `main` |

Evals: solo las ejecuta un humano (`AGENTS.md`).
