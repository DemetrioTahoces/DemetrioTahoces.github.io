"""Tarjetas derivadas del índice del blog: "Sigue leyendo" de cada post y "Últimos artículos" de la home.

Lo comparten new_post.py (las genera) y check_post.py (las valida y, con --fix, las regenera).
La fuente de verdad es blog/index.html: título, "fecha · minutos" y etiquetas de cada tarjeta.
Solo stdlib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INDEX = ROOT / "blog/index.html"
HOME = ROOT / "index.html"
HOME_LATEST = 3
RELATED = 2

# Contenedores: lo que hay dentro se regenera entero.
HOME_BLOCK = re.compile(r'(<div class="latest-posts" data-latest-posts[^>]*>\n)(.*?)(\n\s*</div>)', re.S)
RELATED_BLOCK = re.compile(r'(<div class="related-grid" data-related-posts[^>]*>\n)(.*?)(\n\s*</div>)', re.S)


@dataclass(frozen=True)
class Card:
    slug: str
    title: str
    meta: str  # "30 octubre 2026 · 5 min"
    tags: tuple[str, ...]


def index_cards(index: str | None = None) -> list[Card]:
    """Tarjetas de blog/index.html en su orden (de más reciente a más antigua)."""
    index = INDEX.read_text(encoding="utf-8") if index is None else index
    cards = []
    for block in re.findall(r'<article class="card post-card.*?</article>', index, re.S):
        slug = re.search(r'href="posts/([a-z0-9-]+)\.html"', block)
        title = re.search(r"<h3[^>]*>(.*?)</h3>", block, re.S)
        meta = re.search(r'<p class="text-sm text-blue-300[^"]*">(.*?)</p>', block, re.S)
        tags = re.findall(r'<span class="badge rounded-full px-3 py-1">([^<]+)</span>', block)
        if slug and title and meta:
            cards.append(Card(slug.group(1), " ".join(title.group(1).split()), " ".join(meta.group(1).split()), tuple(tags)))
    return cards


def pick_related(slug: str, tags: list[str] | tuple[str, ...], cards: list[Card]) -> list[Card]:
    """Los RELATED posts con más etiquetas en común; a igualdad, el más reciente (orden del índice)."""
    others = [c for c in cards if c.slug != slug]
    ranked = sorted(others, key=lambda c: -len(set(c.tags) & set(tags)))  # sorted es estable
    return ranked[:RELATED]


def related_html(cards: list[Card]) -> str:
    """Interior de <div class="related-grid" data-related-posts> en blog/posts/<slug>.html."""
    out = []
    for c in cards:
        out.append(f"""                <a class="card related-post" href="{c.slug}.html" data-reveal>
                    <img src="../assets/{c.slug}.svg" alt="" loading="lazy">
                    <span class="related-post-body">
                        <span class="latest-post-meta">{c.meta}</span>
                        <span class="latest-post-title">{c.title}</span>
                    </span>
                </a>""")
    return "\n".join(out)


def home_latest_html(cards: list[Card]) -> str:
    """Interior de <div class="latest-posts" data-latest-posts> en index.html."""
    out = []
    for c in cards[:HOME_LATEST]:
        badges = "".join(f'<span class="badge">{t}</span>' for t in c.tags)
        out.append(f"""                <a class="card latest-post" href="blog/posts/{c.slug}.html" data-reveal>
                    <p class="latest-post-meta">{c.meta}</p>
                    <h3 class="latest-post-title">{c.title}</h3>
                    <div class="latest-post-tags">{badges}</div>
                </a>""")
    return "\n".join(out)


def related_slugs(html: str) -> list[str] | None:
    """Slugs enlazados en "Sigue leyendo", o None si el post no tiene el bloque."""
    block = RELATED_BLOCK.search(html)
    if not block:
        return None
    return re.findall(r'<a class="card related-post" href="([a-z0-9-]+)\.html"', block.group(2))


def sync_related(html: str, slugs: list[str], cards: list[Card]) -> str:
    """Regenera las tarjetas de "Sigue leyendo" con los datos actuales del índice."""
    by_slug = {c.slug: c for c in cards}
    chosen = [by_slug[s] for s in slugs if s in by_slug]
    return RELATED_BLOCK.sub(lambda m: m.group(1) + related_html(chosen) + m.group(3), html, count=1)


def sync_home(home: str, cards: list[Card]) -> str:
    """Regenera "Últimos artículos" de la home con las HOME_LATEST primeras tarjetas del índice."""
    return HOME_BLOCK.sub(lambda m: m.group(1) + home_latest_html(cards) + m.group(3), home, count=1)
