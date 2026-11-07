#!/usr/bin/env python3
"""Genera sitemap.xml con las páginas públicas del sitio (solo stdlib).

Uso (desde cualquier directorio del repo):
    python3 scripts/build_sitemap.py          # reescribe sitemap.xml
    python3 scripts/build_sitemap.py --check  # falla si sitemap.xml no está al día (lo usa check_all.py)

Entra cada página con <link rel="canonical"> que no lleve noindex: la URL es su canonical,
así que añadir un post o una página de CV basta con regenerar. Sin <lastmod>: GitHub Pages
no lo da y sacarlo de git exigiría el historial completo en la CI.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
PAGES = ["index.html", "CV/*.html", "blog/index.html", "blog/posts/*.html"]
CANONICAL_RE = re.compile(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"')
NOINDEX_RE = re.compile(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', re.I)


def urls() -> list[str]:
    found = []
    for pattern in PAGES:
        for page in sorted(ROOT.glob(pattern)):
            html = page.read_text(encoding="utf-8")
            match = CANONICAL_RE.search(html)
            if match and not NOINDEX_RE.search(html) and "{{" not in match.group(1):
                found.append(match.group(1))
    # La home primero; el resto, en orden alfabético.
    return sorted(dict.fromkeys(found), key=lambda u: (u.count("/") > 3, u))


def render() -> str:
    entries = "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls())
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!-- Generado por scripts/build_sitemap.py: no lo edites a mano. -->\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )


def main(argv: list[str]) -> int:
    expected = render()
    if "--check" in argv:
        current = SITEMAP.read_text(encoding="utf-8") if SITEMAP.exists() else ""
        if current != expected:
            print("sitemap.xml no está al día: ejecuta python3 scripts/build_sitemap.py")
            return 1
        return 0
    SITEMAP.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Escrito {SITEMAP.relative_to(ROOT)} ({expected.count('<url>')} URLs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
