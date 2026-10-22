#!/usr/bin/env bash
# Validación completa de un post, sin pasos manuales. Desde cualquier directorio del repo.
#   .agents/skills/manage-blog/scripts/validate.sh <slug> [--minutes N] [--forbid TERM ...] [--check-urls] [--fix]
# Ejecuta check_post.py, comprueba las skills sincronizadas, regenera llms.txt y lanza los tests offline.
# Nunca ejecuta las evals (las lanza un humano).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
python3 .agents/skills/manage-blog/scripts/check_post.py "$@"
python3 .agents/skills/manage-blog/scripts/sync_skills.py --check
(cd CV/Chatbot && uv run python -m core.llms_txt >/dev/null && uv run pytest -q 2>&1 | tail -1)
git diff --quiet -- llms.txt || echo "aviso: llms.txt regenerado, hay que commitearlo"
