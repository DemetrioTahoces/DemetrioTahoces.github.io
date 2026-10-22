# Automatización: scripts, CI y hooks

Todos desde la raíz del repo, solo stdlib salvo `svg-to-png.mjs` (puppeteer-core, `npm ci --prefix .agents/skills/manage-blog/scripts`).

## Scripts (`scripts/`)

| Script | Qué hace |
|---|---|
| `new_post.py` | Esqueleto: HTML desde la plantilla con los `?v=N` del índice, tarjeta en primera posición, contador y ficha y draft con frontmatter. |
| `check_post.py` | Validador. Errores bloquean; avisos se revisan. `--minutes N` (objetivo del usuario), `--forbid TERM` (empresa o producto que no puede aparecer, también desde `forbidden-terms.local.txt`, ignorado por git), `--fix` (minutos y etiquetas de la tarjeta), `--check-urls` (Fuentes por red; 403 es aviso, 404/410 error). |
| `build_png.sh <slug>` | Instala dependencias si faltan, localiza Chrome y convierte el SVG en PNG 1200x630. |
| `validate.sh <slug> ...` | `check_post.py` con los mismos argumentos, skills sincronizadas, `llms.txt` regenerado y tests offline. No lanza evals. |
| `sync_skills.py [--check]` | Copia `.agents/skills` a `.claude/skills`. Con `--check` solo informa. |
| `screenshot.mjs <slug>` | Capturas de escritorio y móvil con servidor estático en marcha. |

## CI (`.github/workflows/blog.yml`)

`check_post.py --all` y `sync_skills.py --check` en PRs y pushes a `main` que tocan el blog, las fichas o las skills. Es la puerta que vale para cualquier agente (Claude Code, Codex, Cowork); los hooks solo cubren Claude Code.

## Hooks recomendados (no instalados)

1. **PreToolUse sobre `git push` (Bash):** ejecuta `check_post.py --all` y `sync_skills.py --check`, y bloquea el push si hay errores. Aquí se publica directo a `main` y GitHub Pages sirve al instante, así que CI avisa tarde. Es el único que compensa.
2. **PostToolUse sobre ediciones en `.agents/skills/**`:** ejecuta `sync_skills.py`. Comodidad, no necesidad: CI ya lo exige.
3. **No recomendados:** validar en cada edición del post (un borrador a medias falla por diseño, y solo ensucia) y cualquiera que lance las evals (prohibido).
