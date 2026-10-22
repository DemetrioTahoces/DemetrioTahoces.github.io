#!/usr/bin/env python3
"""SVG a PNG 1200x630 del diagrama de un post, instalando las dependencias si faltan.

Uso (desde cualquier directorio del repo):
    python3 .agents/skills/manage-blog/scripts/build_png.py <slug>

Chrome se busca solo (rutas habituales y Playwright); si no aparece, define CHROME_PATH.
Necesita node y npm. Solo stdlib.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    slug = argv[0]
    svg = ROOT / "blog/assets" / f"{slug}.svg"
    if not svg.is_file():
        print(f"no existe {svg.relative_to(ROOT)}")
        return 1
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm:
        print("hacen falta node y npm")
        return 1
    if not (SCRIPTS / "node_modules").is_dir():
        subprocess.run([npm, "ci", "--prefix", str(SCRIPTS), "--silent"], cwd=ROOT, check=True)
    env = os.environ.copy()
    if not env.get("CHROME_PATH"):
        found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
        if found:
            env["CHROME_PATH"] = found[0]
    png = svg.with_suffix(".png")
    return subprocess.run([node, str(SCRIPTS / "svg-to-png.mjs"), str(svg), str(png)], cwd=ROOT, env=env).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
