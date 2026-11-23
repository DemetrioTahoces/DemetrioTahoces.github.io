#!/usr/bin/env python3
"""Hook PreToolUse para Claude Code (.claude/settings.json) y Antigravity (.agents/hooks.json):
bloquea el push si el repo no valida.

Detecta el contrato por el JSON de stdin:
- Antigravity: `toolCall.args.CommandLine`; devuelve JSON en stdout (`decision: allow|deny`) y exit 0.
- Claude Code: `tool_input.command`; un error sale con código 2 y el motivo en stderr.

Si la orden contiene `git push`, ejecuta scripts/check_all.py; cualquier otra orden pasa sin coste.
Solo stdlib. Los demás agentes y los pushes manuales los cubre .githooks/pre-push.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CHECK_ALL = Path(__file__).resolve().parent / "check_all.py"
PUSH_RE = re.compile(r"\bgit\s+(?:-\S+\s+)*push\b")


def respond_antigravity(decision: str, reason: str | None = None) -> int:
    out = {"decision": decision}
    if reason:
        out["reason"] = reason
    print(json.dumps(out, ensure_ascii=False))
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    is_antigravity = "toolCall" in payload or "hookEventName" in payload
    if is_antigravity:
        args = payload.get("toolCall", {}).get("args", {})
        command = args.get("CommandLine", "") if isinstance(args, dict) else ""
    else:
        tool_input = payload.get("tool_input", {})
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""

    if not isinstance(command, str) or not PUSH_RE.search(command):
        return respond_antigravity("allow") if is_antigravity else 0

    result = subprocess.run([sys.executable, str(CHECK_ALL)], capture_output=True, text=True)
    if result.returncode:
        msg = "Push bloqueado: el repo no valida. Corrige y vuelve a empujar.\n" + result.stdout + result.stderr
        if is_antigravity:
            return respond_antigravity("deny", msg)
        print(msg, file=sys.stderr)
        return 2
    return respond_antigravity("allow") if is_antigravity else 0


if __name__ == "__main__":
    sys.exit(main())
