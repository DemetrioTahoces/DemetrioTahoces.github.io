# Automatización: scripts, CI y hooks

Todos desde la raíz del repo, solo stdlib salvo `svg-to-png.mjs` (puppeteer-core, `npm ci --prefix .agents/skills/manage-blog/scripts`).

## Scripts (`scripts/`)

| Script | Qué hace |
|---|---|
| `new_post.py` | Esqueleto: HTML desde la plantilla con los `?v=N` del índice, tarjeta en primera posición, contador y ficha y draft con frontmatter. |
| `check_post.py` | Validador. Errores bloquean; avisos se revisan. `--minutes N` (objetivo del usuario), `--forbid TERM` (empresa o producto que no puede aparecer, también desde `forbidden-terms.local.txt`, ignorado por git), `--fix` (minutos y etiquetas de la tarjeta), `--check-urls` (Fuentes por red; 403 es aviso, 404/410 error). |
| `build_png.py <slug>` | Instala dependencias si faltan, localiza Chrome y convierte el SVG en PNG 1200x630. |
| `validate.py <slug> ...` | `check_post.py` con los mismos argumentos, skills sincronizadas, `llms.txt` regenerado y tests offline. No lanza evals. |
| `sync_skills.py [--check]` | Copia `.agents/skills` a `.claude/skills` y genera `.claude/agents/*.md` y `.codex/agents/*.toml` desde `.agents/agents/*.md`. Con `--check` solo informa. |
| `screenshot.mjs <slug>` | Capturas de escritorio y móvil con servidor estático en marcha. |

## CI (`.github/workflows/blog.yml`)

`check_post.py --all` y `sync_skills.py --check` en PRs y pushes a `main` que tocan el blog, las fichas o las skills. Es la puerta que vale para cualquier agente (Claude Code, Codex, Cowork); los hooks solo cubren Claude Code.

## Hook instalado (`.claude/settings.json`, versionado)

`scripts/pre_push_gate.py` es un hook PreToolUse sobre Bash: si la orden contiene `git push`, ejecuta `check_post.py --all` y `sync_skills.py --check` y bloquea el push (exit 2) si hay errores. Aquí se publica directo a `main` y GitHub Pages sirve al instante, así que CI avisaría tarde. Cualquier otra orden pasa sin coste.

- Va en el repo, así que vale en local y en sesiones cloud, pero solo en Claude Code. CI sigue siendo la puerta para Codex o Cowork.
- Usa `python` (como `.claude/launch.json`) y es stdlib. Todos los scripts son Python, sin bash, para que funcionen igual en Windows.
- Detecta `git push` en cualquier parte de la orden, también dentro de un mensaje de commit: ejecuta antes lo que haga falta (por ejemplo `sync_skills.py`) en una orden aparte.
- Para desactivarlo en tu máquina sin tocar el repo: `"disableAllHooks": true` en `.claude/settings.local.json` (no se versiona), o quita el bloque de `settings.json`.

No se valida en cada edición (un borrador a medias falla por diseño) ni hay hooks que lancen evals (prohibido).
