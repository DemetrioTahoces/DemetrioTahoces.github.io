#!/usr/bin/env python3
"""Activa los hooks de git versionados (.githooks) en este clon. Idempotente, solo stdlib.

Uso: python3 scripts/install_hooks.py [--json]
Lo ejecutan solos SessionStart de Claude Code (.claude/settings.json), SessionStart de
Antigravity (.agents/hooks.json, con --json) y .agents/environment.json en Antigravity
cloud; en Codex o un clon manual, ejecútalo una vez. Desactivar: git config --unset core.hooksPath
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str]) -> int:
    json_mode = "--json" in argv
    current = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if current != ".githooks":
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=ROOT, check=True)
        if not json_mode:
            print("hooks de git activados: core.hooksPath=.githooks")
    hook = ROOT / ".githooks/pre-push"
    if hook.exists():
        hook.chmod(hook.stat().st_mode | 0o111)
    if json_mode:
        print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
