#!/usr/bin/env python3
"""Regenera assets/tailwind.css con las utilidades de Tailwind que usa el sitio.

Uso (desde cualquier directorio del repo; necesita node y npx):
    python3 scripts/build_tailwind.py

El sitio no tiene build: assets/tailwind.css es un fichero generado que se versiona y
se publica tal cual. Solo hay que regenerarlo cuando se use una clase de utilidad nueva;
scripts/check_css.py (dentro de scripts/check_all.py) avisa de las clases sin regla.
Misma versión que servía el CDN (cdn.tailwindcss.com -> 3.4.17), así que el resultado
es idéntico al que se veía con el script del CDN.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.4.17"
OUTPUT = ROOT / "assets/tailwind.css"
# Todo lo que puede escribir clases de utilidad: páginas, JS que genera HTML y las plantillas
# con las que se crean posts nuevos.
CONTENT = [
    "index.html",
    "CV/*.html",
    "CV/chatbot-widget.js",
    "blog/index.html",
    "blog/posts/*.html",
    "assets/cv.js",
    ".agents/skills/manage-blog/references/post-template.html",
    ".agents/skills/manage-blog/scripts/new_post.py",
]
HEADER = ("/* Generado por scripts/build_tailwind.py (Tailwind {v}). No editar a mano: "
          "regenerar tras usar una clase de utilidad nueva. */\n")


def main() -> int:
    npx = shutil.which("npx")
    if not npx:
        print("hace falta node con npx")
        return 1
    cmd = [npx, "--yes", f"tailwindcss@{VERSION}", "-o", str(OUTPUT), "--minify",
           "--content", ",".join(CONTENT)]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode:
        return result.returncode
    css = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text(HEADER.format(v=VERSION) + css.lstrip(), encoding="utf-8", newline="\n")
    print(f"escrito: {OUTPUT.relative_to(ROOT)} ({len(css) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
