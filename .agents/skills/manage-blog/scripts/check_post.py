#!/usr/bin/env python3
"""Valida que un post del blog está completo y sincronizado en todas sus superficies.

Uso (desde la raíz del repo, solo stdlib):
    python3 .agents/skills/manage-blog/scripts/check_post.py <slug>
    python3 .agents/skills/manage-blog/scripts/check_post.py --all

Errores (exit 1) = el post no se puede cerrar. Avisos = revisar a mano.
Las anclas `{#id}` de la ficha del chatbot las valida `uv run pytest` en CV/Chatbot.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SITE = "https://demetriotahoces.github.io"
WORDS_PER_MINUTE = 220
MONTHS = {m: i for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(), 1)}
DASHES = re.compile("[—–]")


class Page(HTMLParser):
    """Recoge metadatos, enlaces, ids y el texto de `.article-prose`."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.links: list[tuple[str, str]] = []
        self.ids: list[str] = []
        self.jsonld: list[str] = []
        self.title = ""
        self.prose: list[str] = []
        self.text: list[str] = []
        self._stack: list[str] = []
        self._prose_depth: int | None = None
        self._in_jsonld = False
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = {k: v or "" for k, v in attrs}
        if tag not in ("meta", "link", "img", "br", "hr", "input", "source", "path"):
            self._stack.append(tag)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "meta":
            key = a.get("property") or a.get("name")
            if key:
                self.meta[key] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical":
            self.meta["canonical"] = a.get("href", "")
        for attr in ("href", "src"):
            if attr in a:
                self.links.append((tag, a[attr]))
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True
        if tag == "title":
            self._in_title = True
        if "article-prose" in a.get("class", "").split() and self._prose_depth is None:
            self._prose_depth = len(self._stack)

    def handle_endtag(self, tag):
        if self._prose_depth is not None and len(self._stack) == self._prose_depth:
            self._prose_depth = -1  # cerrado; no volver a abrir
        if self._stack:
            self._stack.pop()
        self._in_jsonld = self._in_jsonld and tag != "script"
        self._in_title = self._in_title and tag != "title"

    def handle_data(self, data):
        if self._in_jsonld:
            self.jsonld.append(data)
        elif self._in_title:
            self.title += data
        elif "script" not in self._stack and "style" not in self._stack:
            self.text.append(data)
            if self._prose_depth not in (None, -1):
                self.prose.append(data)


def parse(path: Path) -> Page:
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


def spanish_date(text: str) -> str | None:
    match = re.search(r"(\d{1,2}) (\w+) (\d{4})", text)
    if not match or match.group(2) not in MONTHS:
        return None
    day, month, year = match.groups()
    return f"{year}-{MONTHS[month]:02d}-{int(day):02d}"


def check(slug: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    html_path = ROOT / "blog/posts" / f"{slug}.html"
    md_path = ROOT / "CV/Chatbot/docs/blog" / f"{slug}.md"
    txt_path = ROOT / "blog/linkedin-drafts" / f"{slug}.txt"
    url = f"{SITE}/blog/posts/{slug}.html"

    for path in (html_path, md_path, txt_path):
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            errors.append(f"falta o está vacío: {path.relative_to(ROOT)}")
    if errors:
        return errors, warnings

    page = parse(html_path)
    fm = frontmatter(md_path)

    # Metadatos SEO / OG / Twitter
    for key in ("description", "og:title", "og:description", "og:image", "twitter:card",
                "twitter:title", "twitter:description", "twitter:image"):
        if not page.meta.get(key):
            errors.append(f"HTML sin meta {key}")
    for key in ("canonical", "og:url"):
        if page.meta.get(key) != url:
            errors.append(f"{key} debe ser {url} (es {page.meta.get(key)!r})")
    if page.meta.get("og:type") != "article":
        errors.append("og:type debe ser article")
    for key in ("og:image", "twitter:image"):
        image = page.meta.get(key, "")
        if image.startswith(SITE) and not (ROOT / image.removeprefix(SITE + "/")).is_file():
            errors.append(f"{key} apunta a un fichero inexistente: {image}")
        if image.endswith(".svg"):
            warnings.append(f"{key} es SVG: LinkedIn y X no lo renderizan, usa el PNG 1200x630")

    # JSON-LD
    try:
        ld = json.loads("".join(page.jsonld))
    except json.JSONDecodeError as exc:
        errors.append(f"JSON-LD inválido: {exc}")
        ld = {}
    if ld:
        if ld.get("@type") != "BlogPosting":
            errors.append("JSON-LD @type debe ser BlogPosting")
        if ld.get("mainEntityOfPage") != url:
            errors.append("JSON-LD mainEntityOfPage no coincide con la URL del post")
        if ld.get("datePublished") != fm.get("date"):
            errors.append(f"JSON-LD datePublished ({ld.get('datePublished')}) != date de la ficha ({fm.get('date')})")
        if ld.get("image") != page.meta.get("og:image"):
            warnings.append("JSON-LD image distinta de og:image")

    # Ficha del chatbot
    if fm.get("type") != "blog_post":
        errors.append("ficha: type debe ser blog_post")
    if fm.get("route") != f"/blog/posts/{slug}.html":
        errors.append(f"ficha: route debe ser /blog/posts/{slug}.html")
    for key in ("title", "date", "tags", "summary"):
        if not fm.get(key):
            errors.append(f"ficha: falta {key}")
    if "## Fuentes" not in md_path.read_text(encoding="utf-8"):
        warnings.append("ficha: sin sección final '## Fuentes'")

    # Enlaces relativos
    for tag, link in page.links:
        if re.match(r"(https?:|mailto:|data:|#)", link):
            continue
        target = (html_path.parent / link.split("#")[0].split("?")[0]).resolve()
        if not target.exists():
            errors.append(f"enlace roto en <{tag}>: {link}")

    # Ids duplicados
    duplicated = {i for i in page.ids if page.ids.count(i) > 1}
    if duplicated:
        errors.append(f"ids duplicados: {sorted(duplicated)}")

    # Tiempo de lectura
    words = len(" ".join(page.prose).split())
    minutes = max(1, round(words / WORDS_PER_MINUTE))
    declared = re.search(r"(\d+) min de lectura", " ".join(page.text))
    if not declared:
        errors.append("HTML sin 'N min de lectura'")
    elif abs(int(declared.group(1)) - minutes) > 1:
        warnings.append(f"lectura declarada {declared.group(1)} min, estimada {minutes} min ({words} palabras)")
    if not 3 <= minutes <= 8:
        warnings.append(f"lectura estimada {minutes} min fuera del rango 3-8")

    # Em/en dash (auditoría humanizer)
    for path, text in ((html_path, " ".join(page.text)), (txt_path, txt_path.read_text(encoding="utf-8"))):
        if DASHES.search(text):
            errors.append(f"em/en dash en {path.relative_to(ROOT)}")

    # Draft de LinkedIn copiable
    draft = txt_path.read_text(encoding="utf-8")
    if url not in draft:
        errors.append(f"draft de LinkedIn sin la URL pública {url}")
    if re.search(r"\*\*|\]\(|^#{1,6} |^\s*[-*] ", draft, re.M):
        errors.append("draft de LinkedIn con sintaxis Markdown")

    # Tarjeta del índice
    index = (ROOT / "blog/index.html").read_text(encoding="utf-8")
    cards = re.findall(r'<article class="card post-card.*?</article>', index, re.S)
    card = next((c for c in cards if f'href="posts/{slug}.html"' in c), None)
    if card is None:
        errors.append("blog/index.html sin tarjeta para el post")
    elif spanish_date(card) != fm.get("date"):
        errors.append(f"fecha de la tarjeta ({spanish_date(card)}) != ficha ({fm.get('date')})")
    card_dates = [spanish_date(c) or "" for c in cards]
    if card_dates != sorted(card_dates, reverse=True):
        errors.append("tarjetas del índice no ordenadas de más reciente a más antigua")
    posts = sorted(p.stem for p in (ROOT / "blog/posts").glob("*.html"))
    counter = re.search(r"(\d+) publicados?", index)
    if not counter or int(counter.group(1)) != len(posts) or len(cards) != len(posts):
        errors.append(f"contador/tarjetas del índice no cuadran con {len(posts)} posts en blog/posts")

    # Versiones de assets iguales que en el índice
    versions = lambda text: dict(re.findall(r"assets/(\w+\.(?:css|js))\?v=(\d+)", text))
    if versions(html_path.read_text(encoding="utf-8")) != versions(index):
        warnings.append("?v=N de assets distinto entre el post y blog/index.html")

    return errors, warnings


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    slugs = sorted(p.stem for p in (ROOT / "blog/posts").glob("*.html")) if argv[0] == "--all" else argv
    failed = False
    for slug in slugs:
        errors, warnings = check(slug)
        status = "ERROR" if errors else "OK"
        print(f"[{status}] {slug}")
        for msg in errors:
            print(f"  error: {msg}")
        for msg in warnings:
            print(f"  aviso: {msg}")
        failed |= bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
