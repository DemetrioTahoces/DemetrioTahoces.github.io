#!/usr/bin/env python3
"""Comprueba que cada clase usada en el HTML del sitio tiene alguna regla CSS.

Uso (desde cualquier directorio del repo, solo stdlib):
    python3 scripts/check_css.py

Sin build, una clase de utilidad que no esté en assets/tailwind.css no hace nada y no
da ningún error en el navegador. Este check lo detecta. Si falla por una utilidad de
Tailwind, regenerar con `python3 scripts/build_tailwind.py`; si es una clase propia, añadir
la regla en assets/cv.css o assets/blog.css. Las clases que solo sirven de gancho para JS
o para los checks van en HOOKS.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "CV/*.html", "blog/index.html", "blog/posts/*.html",
         ".agents/skills/manage-blog/references/post-template.html"]
STYLESHEETS = ["assets/tailwind.css", "assets/tokens.css", "assets/cv.css", "assets/blog.css"]
# Clases sin estilo propio a propósito: ganchos de JS, de los checks o de la impresión.
HOOKS = {
    "experience-list",  # contenedor de la línea de tiempo (index.html)
    "no-print",         # se oculta solo en @media print
    "tfm-card",         # tarjeta del TFM en CV/imagine800.html
    "ai-content", "ai-content-box", "ai-status-container", "ai-status-text",  # JS de CV/chatbot.html
}
# Iconos de Phosphor: su CSS se carga de la CDN en CV/chatbot.html y en el widget.
HOOK_PREFIXES = ("ph-",)
HOOKS.add("ph")
CLASS_ATTR = re.compile(r'\bclass="([^"]*)"')
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
SELECTOR_CLASS = re.compile(r"\.((?:\\.|[A-Za-z0-9_-])+)")
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
COMMENT = re.compile(r"/\*.*?\*/", re.S)


def defined_classes(css: str) -> set[str]:
    css = COMMENT.sub("", css)
    # Solo los selectores: lo que va antes de cada "{" (los valores no declaran clases).
    selectors = " ".join(re.findall(r"([^{}]+)\{", css))
    return {re.sub(r"\\(.)", r"\1", m) for m in SELECTOR_CLASS.findall(selectors)}


def main() -> int:
    shared: set[str] = set()
    for name in STYLESHEETS:
        path = ROOT / name
        if path.is_file():
            shared |= defined_classes(path.read_text(encoding="utf-8"))
    missing: dict[str, set[str]] = {}
    for pattern in PAGES:
        for path in sorted(ROOT.glob(pattern)):
            html = HTML_COMMENT.sub("", path.read_text(encoding="utf-8"))
            local = shared | {c for block in STYLE_BLOCK.findall(html) for c in defined_classes(block)}
            for attr in CLASS_ATTR.findall(html):
                if "{{" in attr or "${" in attr:
                    continue
                for cls in attr.split():
                    if cls not in local and cls not in HOOKS and not cls.startswith(HOOK_PREFIXES):
                        missing.setdefault(str(path.relative_to(ROOT)).replace("\\", "/"), set()).add(cls)
    for page, classes in sorted(missing.items()):
        print(f"{page}: clases sin regla CSS: {', '.join(sorted(classes))}")
    if missing:
        print("\nSi son utilidades de Tailwind: python3 scripts/build_tailwind.py. "
              "Si son clases propias: añadir la regla en assets/cv.css o assets/blog.css.")
        return 1
    print("ok: todas las clases del HTML tienen regla CSS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
