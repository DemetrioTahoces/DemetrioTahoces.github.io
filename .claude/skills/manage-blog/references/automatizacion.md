# Automatización: scripts, CI y hooks

Todos desde la raíz del repo, solo stdlib salvo `svg-to-png.mjs` (puppeteer-core, `npm ci --prefix .agents/skills/manage-blog/scripts`).

## Scripts (`scripts/`)

| Script | Qué hace |
|---|---|
| `new_post.py` | Esqueleto: HTML desde la plantilla con los `?v=N` del índice, tarjeta en primera posición, contador y ficha y draft con frontmatter. |
| `check_post.py` | Validador. Errores bloquean; avisos se revisan. `--minutes N` (objetivo del usuario), `--forbid TERM` (empresa o producto que no puede aparecer, también desde `forbidden-terms.local.txt`, ignorado por git), `--fix` (minutos y etiquetas de la tarjeta), `--check-urls` (Fuentes por red; 403 es aviso, 404/410 error). |
| `build_png.py <slug>` | Instala dependencias si faltan, localiza Chrome y convierte el SVG en PNG 1200x630. |
| `validate.py <slug> ...` | `check_post.py` con los mismos argumentos, `scripts/sync_skills.py --check`, `llms.txt` regenerado y tests offline. No lanza evals. |
| `screenshot.mjs <slug>` | Capturas de escritorio y móvil con servidor estático en marcha. |

## Puertas transversales (`scripts/`, mapa en `.agents/README.md`)

`scripts/check_all.py` es la definición única de "validado": `check_post.py --all`, `check_cv.py` y `sync_skills.py --check` (con `--tests`, los tests offline del chatbot). Lo usan tres puertas:

- **CI** (`blog.yml`, `cv.yml`): vale para cualquier agente, pero avisa tarde, porque aquí se publica directo a `main` y GitHub Pages sirve al instante.
- **Hook de git** (`.githooks/pre-push`): vale para Claude Code, Codex, Antigravity y pushes manuales. Se activa con `python3 scripts/install_hooks.py` (`core.hooksPath`, una vez por clon; el hook `SessionStart` de Claude Code lo hace solo). Saltar puntualmente: `--no-verify`.
- **Hook de Claude Code** (`.claude/settings.json`, `scripts/pre_push_gate.py`): bloquea el push desde el agente (exit 2) con el motivo devuelto al modelo.

- Todo es Python stdlib salvo el wrapper `sh` del hook de git, que usa `python3` o `python`.
- El hook de Claude Code detecta un push en cualquier parte de la orden, también dentro de un mensaje de commit: ejecuta antes lo que haga falta (por ejemplo `sync_skills.py`) en una orden aparte.
- Desactivar el de Claude Code sin tocar el repo: `"disableAllHooks": true` en `.claude/settings.local.json` (no se versiona). Desactivar el de git: `git config --unset core.hooksPath`.

No se valida en cada edición (un borrador a medias falla por diseño) ni hay hooks que lancen evals (prohibido).
