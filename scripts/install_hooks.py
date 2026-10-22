#!/usr/bin/env python3
"""Activa los hooks de git versionados (.githooks) en este clon. Idempotente, solo stdlib.

Uso: python3 scripts/install_hooks.py
Lo ejecuta solo el hook SessionStart de Claude Code; en Codex, Antigravity o un clon manual,
ejecútalo una vez. Desactivar: git config --unset core.hooksPath
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    current = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if current != ".githooks":
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=ROOT, check=True)
        print("hooks de git activados: core.hooksPath=.githooks")
    hook = ROOT / ".githooks/pre-push"
    if hook.exists():
        hook.chmod(hook.stat().st_mode | 0o111)
    return 0


if __name__ == "__main__":
    sys.exit(main())
