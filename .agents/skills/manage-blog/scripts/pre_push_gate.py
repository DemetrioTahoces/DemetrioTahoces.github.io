#!/usr/bin/env python3
"""Hook PreToolUse de Claude Code: bloquea `git push` si el blog o las skills no validan.

Lee de stdin el JSON del hook. Si la orden de Bash contiene `git push`, ejecuta
check_post.py --all y sync_skills.py --check; un error sale con código 2 y el motivo
en stderr, que Claude Code devuelve al modelo. Cualquier otra orden pasa sin coste.
Solo stdlib. Se desactiva quitando el hook de .claude/settings.json.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
CHECKS = (["check_post.py", "--all"], ["sync_skills.py", "--check"])


def main() -> int:
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        return 0
    if not re.search(r"\bgit\s+(?:-\S+\s+)*push\b", command):
        return 0
    problems = []
    for script, *args in CHECKS:
        result = subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True)
        if result.returncode:
            problems.append(f"{script}:\n{result.stdout}{result.stderr}")
    if problems:
        print("Push bloqueado: el blog o las skills no validan. Corrige y vuelve a empujar.\n" + "\n".join(problems), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
