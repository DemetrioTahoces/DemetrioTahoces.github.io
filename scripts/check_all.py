#!/usr/bin/env python3
"""Puerta única de validación del repo: la usan el hook de Claude Code, el hook de git y la CI.

Uso (desde cualquier directorio, solo stdlib):
    python3 scripts/check_all.py            # rápido: blog, CV y copias derivadas
    python3 scripts/check_all.py --tests    # añade los tests offline del chatbot (requiere uv)

Ejecuta todas las comprobaciones aunque alguna falle y sale con 1 si falla cualquiera.
Nunca lanza evals.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
CHECKS = [
    ("blog", [sys.executable, str(SKILLS / "manage-blog/scripts/check_post.py"), "--all"]),
    ("cv", [sys.executable, str(SKILLS / "edit-cv/scripts/check_cv.py")]),
    ("skills y agentes", [sys.executable, str(ROOT / "scripts/sync_skills.py"), "--check"]),
]


def main(argv: list[str]) -> int:
    checks = list(CHECKS)
    if "--tests" in argv:
        uv = shutil.which("uv")
        if uv:
            checks.append(("tests chatbot", [uv, "run", "pytest", "-q"], ROOT / "CV/Chatbot"))
        else:
            print("aviso: uv no está instalado; se omiten los tests del chatbot")
    failed = []
    for name, cmd, *cwd in checks:
        result = subprocess.run(cmd, cwd=cwd[0] if cwd else ROOT, capture_output=True, text=True)
        status = "ok" if result.returncode == 0 else "FALLA"
        print(f"[{status}] {name}")
        if result.returncode:
            failed.append(name)
            print(result.stdout + result.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
