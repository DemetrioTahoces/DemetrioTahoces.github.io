#!/usr/bin/env python3
"""Mantiene las copias derivadas de .agents (el original se edita siempre en .agents):
.claude/skills = copia exacta de .agents/skills, y los agentes de .agents/agents/*.md se
generan como .claude/agents/*.md (Claude Code) y .codex/agents/*.toml (Codex).
Antigravity lee .agents/agents directamente.

Uso (desde la raíz del repo, solo stdlib):
    python3 scripts/sync_skills.py          # copia .agents -> .claude
    python3 scripts/sync_skills.py --check  # solo informa; exit 1 si difieren

Ignora node_modules y __pycache__.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ".agents/skills"
DST = ROOT / ".claude/skills"
IGNORED = {"node_modules", "__pycache__"}
AGENTS_SRC = ROOT / ".agents/agents"
CLAUDE_AGENTS = ROOT / ".claude/agents"
CODEX_AGENTS = ROOT / ".codex/agents"


def files(base: Path) -> set[Path]:
    return {p.relative_to(base) for p in base.rglob("*")
            if p.is_file() and not IGNORED & set(p.relative_to(base).parts)}


def split_agent(path: Path) -> tuple[dict[str, str], str]:
    _, front, body = path.read_text(encoding="utf-8").split("---\n", 2)
    meta = {}
    for line in front.splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body.lstrip("\n")


def toml_str(text: str) -> str:
    return '"""\n' + text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"') + '"""'


def derived_agents() -> dict[Path, str]:
    out: dict[Path, str] = {}
    for src in sorted(AGENTS_SRC.glob("*.md")) if AGENTS_SRC.exists() else []:
        meta, body = split_agent(src)
        claude = ["---", f"name: {meta['name']}", f"description: {meta['description']}"]
        claude += [f"tools: {meta['tools']}"] if meta.get("tools") else []
        claude += [f"model: {meta['claude_model']}"] if meta.get("claude_model") else []
        claude += [f"effort: {meta['claude_effort']}"] if meta.get("claude_effort") else []
        out[CLAUDE_AGENTS / src.name] = "\n".join(claude) + "\n---\n\n" + body
        codex = [f'name = "{meta["name"]}"', f'description = "{meta["description"]}"']
        codex += [f'model = "{meta["codex_model"]}"'] if meta.get("codex_model") else []
        codex += [f'model_reasoning_effort = "{meta["codex_reasoning_effort"]}"'] if meta.get("codex_reasoning_effort") else []
        codex += [f'sandbox_mode = "{meta["codex_sandbox_mode"]}"'] if meta.get("codex_sandbox_mode") else []
        codex.append("developer_instructions = " + toml_str(body))
        out[CODEX_AGENTS / (src.stem + ".toml")] = "\n".join(codex) + "\n"
    return out


def sync_agents(check: bool) -> int:
    derived = derived_agents()
    stale = 0
    for path, content in derived.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            print(f"{'difiere' if check else 'generado'}: {path.relative_to(ROOT)}")
            stale += 1
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
    for base, pattern in ((CLAUDE_AGENTS, "*.md"), (CODEX_AGENTS, "*.toml")):
        for path in sorted(base.glob(pattern)) if base.exists() else []:
            if path not in derived:
                print(f"{'sobra' if check else 'borrado'}: {path.relative_to(ROOT)}")
                stale += 1
                if not check:
                    path.unlink()
    if check and stale:
        print("agentes desincronizados: python3 scripts/sync_skills.py")
        return 1
    return 0


def main(argv: list[str]) -> int:
    check = "--check" in argv
    rc = sync_agents(check)
    src, dst = files(SRC), files(DST) if DST.exists() else set()
    changed = [p for p in sorted(src) if not (DST / p).is_file() or (DST / p).read_bytes() != (SRC / p).read_bytes()]
    extra = sorted(dst - src)
    for p in changed:
        print(f"{'difiere' if check else 'copiado'}: {p}")
        if not check:
            (DST / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SRC / p, DST / p)
    for p in extra:
        print(f"{'sobra en .claude' if check else 'borrado'}: {p}")
        if not check:
            (DST / p).unlink()
    if check and (changed or extra):
        print("skills desincronizadas: python3 scripts/sync_skills.py")
        return 1
    if not changed and not extra and rc == 0:
        print("skills y agentes sincronizados")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
