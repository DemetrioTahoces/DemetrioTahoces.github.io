#!/usr/bin/env python3
"""Comprueba que las tarjetas del CV respetan los umbrales de tamaño.

Uso (desde la raíz del repo, solo stdlib):
    python3 .agents/skills/edit-cv/scripts/check_cv.py

Umbrales y criterio: references/umbrales.md. Mide caracteres de texto visible.
Errores (exit 1) = una tarjeta supera un máximo. Avisos = por debajo de un
mínimo o fuera del rango orientativo; revisar a mano.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

# (máximo duro, mínimo orientativo). Ver references/umbrales.md.
DETAIL = {
    "normal": {"subtitle": 100, "bullets": (2, 4), "bullet": (80, 200), "total": 550},
    "featured": {"subtitle": 130, "bullets": (2, 5), "bullet": (80, 220), "total": 900},
}
JOB_DESC = {"normal": 170, "current": 250}
CONTEXT = (250, 450)
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "path"}


def clean(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", "".join(parts)).strip()


class Cards(HTMLParser):
    """Extrae detail-cards, job-cards y el bloque #contexto de una página."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[dict] = []
        self.context: list[str] = []
        self._stack: list[tuple[str, set[str]]] = []  # (tag, roles abiertos aquí)
        self._card: dict | None = None
        self._field: list[str] | None = None
        self._in_context = False
        self._in_h2 = False

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = {k: v or "" for k, v in attrs}
        cls = a.get("class", "").split()
        roles: set[str] = set()
        if tag == "div" and ("detail-card" in cls or "job-card" in cls) and self._card is None:
            self._card = {"id": a.get("id", "?"), "kind": "detail" if "detail-card" in cls else "job",
                          "featured": "data-featured" in a, "h3": False, "subtitle": [], "bullets": [],
                          "desc": [], "date": []}
            roles.add("card")
        elif tag == "section" and a.get("id") == "contexto":
            self._in_context = True
            roles.add("context")
        elif self._card is not None:
            c = self._card
            if tag == "h3":
                c["h3"] = True
            if tag == "li":
                c["bullets"].append([])
                self._field = c["bullets"][-1]
                roles.add("field")
            elif tag == "p" and "text-gray-400" in cls and self._field is None:
                target = c["subtitle"] if c["kind"] == "detail" else c["desc"]
                if not target:
                    self._field = target
                    roles.add("field")
            elif tag == "span" and "rounded-full" in cls and c["kind"] == "job":
                self._field = c["date"]
                roles.add("field")
        if tag == "h2" and self._in_context:
            self._in_h2 = True
            roles.add("h2")
        self._stack.append((tag, roles))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self._stack:
            t, roles = self._stack.pop()
            if "field" in roles:
                self._field = None
            if "h2" in roles:
                self._in_h2 = False
            if "context" in roles:
                self._in_context = False
            if "card" in roles:
                self.cards.append(self._card)
                self._card = None
            if t == tag:
                break

    def handle_data(self, data):
        if self._field is not None:
            self._field.append(data)
        if self._in_context and not self._in_h2:
            self.context.append(data)


def check_detail(page: str, card: dict, errors: list, warnings: list) -> None:
    level = "featured" if card["featured"] else "normal"
    lim = DETAIL[level]
    where = f"{page}#{card['id']}" + (" (destacada)" if card["featured"] else "")
    subtitle = clean(card["subtitle"])
    bullets = [clean(b) for b in card["bullets"]]
    total = sum(map(len, bullets))
    if len(subtitle) > lim["subtitle"]:
        errors.append(f"{where}: subtítulo de {len(subtitle)} caracteres (máx. {lim['subtitle']})")
    lo, hi = lim["bullets"]
    if len(bullets) > hi:
        errors.append(f"{where}: {len(bullets)} bullets (máx. {hi})")
    elif len(bullets) < lo:
        warnings.append(f"{where}: {len(bullets)} bullet(s) (mín. orientativo {lo})")
    lo, hi = lim["bullet"]
    for i, b in enumerate(bullets, 1):
        if len(b) > hi:
            errors.append(f"{where}: bullet {i} de {len(b)} caracteres (máx. {hi})")
        elif len(b) < lo:
            warnings.append(f"{where}: bullet {i} de {len(b)} caracteres (mín. orientativo {lo})")
    if total > lim["total"]:
        errors.append(f"{where}: {total} caracteres en bullets (máx. {lim['total']})")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[str] = []

    home = Cards()
    home.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    for c in home.cards:
        if c["kind"] != "job":
            continue
        current = "presente" in clean(c["date"]).lower()
        hi = JOB_DESC["current" if current else "normal"]
        n = len(clean(c["desc"]))
        rows.append(f"  index.html#{c['id']:26} desc={n}/{hi}")
        if n > hi:
            errors.append(f"index.html#{c['id']}: descripción de {n} caracteres (máx. {hi}"
                          f"{', experiencia actual' if current else ''})")

    for path in sorted((ROOT / "CV").glob("*.html")):
        page = Cards()
        page.feed(path.read_text(encoding="utf-8"))
        name = f"CV/{path.name}"
        # Solo tarjetas de contribución (con h3). Las de sección (h2, p. ej. tfg.html) no se miden.
        details = [c for c in page.cards if c["kind"] == "detail" and c["h3"]]
        featured = [c["id"] for c in details if c["featured"]]
        if len(featured) > 1:
            errors.append(f"{name}: {len(featured)} tarjetas destacadas ({', '.join(featured)}); máx. 1 por página")
        for c in details:
            check_detail(name, c, errors, warnings)
            bullets = [clean(b) for b in c["bullets"]]
            rows.append(f"  {name}#{c['id']:26} sub={len(clean(c['subtitle'])):>3} "
                        f"bullets={len(bullets)} max={max(map(len, bullets), default=0):>3} "
                        f"total={sum(map(len, bullets)):>4}{' *' if c['featured'] else ''}")
        if page.context:
            n = len(clean(page.context))
            if not CONTEXT[0] <= n <= CONTEXT[1]:
                warnings.append(f"{name}#contexto: {n} caracteres (rango orientativo {CONTEXT[0]}–{CONTEXT[1]})")

    print("Medidas (caracteres de texto visible; * = destacada):")
    print("\n".join(rows))
    for w in warnings:
        print(f"AVISO: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"\n{len(errors)} errores, {len(warnings)} avisos")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
