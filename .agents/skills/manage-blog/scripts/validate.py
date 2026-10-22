#!/usr/bin/env python3
"""Validación completa de un post, sin pasos manuales. Solo stdlib; funciona en Windows, macOS y Linux.

Uso (desde cualquier directorio del repo):
    python3 .agents/skills/manage-blog/scripts/validate.py <slug> [--minutes N] [--forbid TERM ...] [--check-urls] [--fix]

Ejecuta check_post.py con esos argumentos, comprueba las skills sincronizadas, regenera llms.txt
y lanza los tests offline del chatbot. Nunca ejecuta las evals (las lanza un humano).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent


def run(cmd: list[str], cwd: Path = ROOT) -> int:
    return subprocess.run(cmd, cwd=cwd).returncode


def main(argv: list[str]) -> int:
    failed = run([sys.executable, str(SCRIPTS / "check_post.py"), *argv]) != 0
    failed |= run([sys.executable, str(SCRIPTS / "sync_skills.py"), "--check"]) != 0
    uv = shutil.which("uv")
    if not uv:
        print("aviso: uv no está instalado; se omiten llms.txt y los tests del chatbot")
    else:
        chatbot = ROOT / "CV/Chatbot"
        failed |= run([uv, "run", "python", "-m", "core.llms_txt"], chatbot) != 0
        failed |= run([uv, "run", "pytest", "-q"], chatbot) != 0
        if subprocess.run(["git", "diff", "--quiet", "--", "llms.txt"], cwd=ROOT).returncode:
            print("aviso: llms.txt regenerado, hay que commitearlo")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
