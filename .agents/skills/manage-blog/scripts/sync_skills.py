#!/usr/bin/env python3
"""Mantiene .claude/skills como copia exacta de .agents/skills (el original se edita en .agents).

Uso (desde la raíz del repo, solo stdlib):
    python3 .agents/skills/manage-blog/scripts/sync_skills.py          # copia .agents -> .claude
    python3 .agents/skills/manage-blog/scripts/sync_skills.py --check  # solo informa; exit 1 si difieren

Ignora node_modules y __pycache__.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / ".agents/skills"
DST = ROOT / ".claude/skills"
IGNORED = {"node_modules", "__pycache__"}


def files(base: Path) -> set[Path]:
    return {p.relative_to(base) for p in base.rglob("*")
            if p.is_file() and not IGNORED & set(p.relative_to(base).parts)}


def main(argv: list[str]) -> int:
    check = "--check" in argv
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
        print("skills desincronizadas: python3 .agents/skills/manage-blog/scripts/sync_skills.py")
        return 1
    if not changed and not extra:
        print("skills sincronizadas")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
