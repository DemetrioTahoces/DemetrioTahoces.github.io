#!/usr/bin/env python3
"""Hook PreToolUse de Claude Code: bloquea el push si el repo no valida.

Lee de stdin el JSON del hook. Si la orden de Bash contiene `git push`, ejecuta
scripts/check_all.py; un error sale con código 2 y el motivo en stderr, que Claude Code
devuelve al modelo. Cualquier otra orden pasa sin coste. Solo stdlib.
Los demás agentes y los pushes manuales los cubre .githooks/pre-push (scripts/install_hooks.py).
Se desactiva quitando el hook de .claude/settings.json.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CHECK_ALL = Path(__file__).resolve().parent / "check_all.py"


def main() -> int:
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        return 0
    if not re.search(r"\bgit\s+(?:-\S+\s+)*push\b", command):
        return 0
    result = subprocess.run([sys.executable, str(CHECK_ALL)], capture_output=True, text=True)
    if result.returncode:
        print("Push bloqueado: el repo no valida. Corrige y vuelve a empujar.\n" + result.stdout + result.stderr, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
