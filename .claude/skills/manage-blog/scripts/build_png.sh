#!/usr/bin/env bash
# SVG -> PNG 1200x630 del diagrama de un post, instalando las dependencias si faltan.
#   .agents/skills/manage-blog/scripts/build_png.sh <slug>
# Chrome se busca solo (rutas habituales y Playwright); si no aparece, define CHROME_PATH.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
SLUG="${1:?uso: build_png.sh <slug>}"
SCRIPTS=".agents/skills/manage-blog/scripts"
[ -d "$SCRIPTS/node_modules" ] || npm ci --prefix "$SCRIPTS" --silent
if [ -z "${CHROME_PATH:-}" ]; then
  CHROME_PATH="$(ls -d /opt/pw-browsers/chromium-*/chrome-linux*/chrome 2>/dev/null | head -1 || true)"
  export CHROME_PATH
fi
node "$SCRIPTS/svg-to-png.mjs" "blog/assets/$SLUG.svg" "blog/assets/$SLUG.png"
