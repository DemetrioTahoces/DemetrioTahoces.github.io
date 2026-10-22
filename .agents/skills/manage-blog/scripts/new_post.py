#!/usr/bin/env python3
"""Crea el esqueleto de un post nuevo: HTML desde la plantilla, tarjeta, ficha y draft.

Uso (desde la raíz del repo, solo stdlib):
    python3 .agents/skills/manage-blog/scripts/new_post.py <slug> \\
        --title "Título" --tags "Etiqueta 1,Etiqueta 2,Etiqueta 3" --minutes 5 \\
        --eyebrow "Antetítulo" --description "Descripción SEO" [--date AAAA-MM-DD]

Copia las versiones ?v=N de blog/index.html, añade la tarjeta en primera posición y
sube el contador "N publicados". Deja marcadores {{...}} en el cuerpo, la tarjeta, la
ficha y el draft: check_post.py falla mientras quede alguno. No genera el diagrama.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SITE = "https://demetriotahoces.github.io"
MONTHS = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()

CARD = """                <article class="card post-card rounded-xl overflow-hidden" data-reveal>
                    <a href="posts/{slug}.html" class="block group">
                        <img src="assets/{slug}.svg" alt="{{{{ALT_TARJETA}}}}" class="w-full aspect-[16/9] object-cover border-b border-blue-400/10">
                    </a>
                    <div>
                        <div class="p-6">
                            <p class="text-sm text-blue-300 font-semibold mb-2">{date_es} · {minutes} min</p>
                            <a href="posts/{slug}.html" class="block group">
                                <h3 class="text-xl font-bold text-gray-100 mb-3 group-hover:text-blue-400 transition-colors">{title}</h3>
                            </a>
                            <p class="text-gray-400 leading-relaxed">
                                {{{{DESCRIPCION_TARJETA}}}}
                            </p>
                        </div>
                    </div>
                    <div class="px-6 pb-6 flex flex-wrap gap-2 text-sm text-gray-500">
{badges}
                    </div>
                </article>
"""


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Crea el esqueleto de un post del blog.")
    parser.add_argument("slug", help="minúsculas, ASCII y guiones")
    parser.add_argument("--title", required=True)
    parser.add_argument("--tags", required=True, help="3 etiquetas separadas por comas")
    parser.add_argument("--minutes", required=True, type=int)
    parser.add_argument("--eyebrow", default="{{ANTETITULO}}")
    parser.add_argument("--description", default="{{DESCRIPCION_SEO_150_160_CARACTERES}}")
    parser.add_argument("--date", default=datetime.date.today().isoformat())
    args = parser.parse_args(argv)

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        parser.error("slug en minúsculas, ASCII y con guiones")
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    year, month, day = (int(x) for x in args.date.split("-"))
    date_es = f"{day} {MONTHS[month - 1]} {year}"

    html_path = ROOT / "blog/posts" / f"{args.slug}.html"
    md_path = ROOT / "CV/Chatbot/docs/blog" / f"{args.slug}.md"
    txt_path = ROOT / "blog/linkedin-drafts" / f"{args.slug}.txt"
    index_path = ROOT / "blog/index.html"
    for path in (html_path, md_path, txt_path):
        if path.exists():
            parser.error(f"ya existe {path.relative_to(ROOT)}")

    index = index_path.read_text(encoding="utf-8")
    versions = dict(re.findall(r"assets/(\w+\.(?:css|js))\?v=(\d+)", index))

    # HTML desde la plantilla
    html = (ROOT / ".agents/skills/manage-blog/references/post-template.html").read_text(encoding="utf-8")
    html = re.sub(r"(?s)<!--\n  Plantilla de post.*?-->\n\n", "", html, count=1)
    html = re.sub(r"assets/(\w+\.(?:css|js))\?v=\{\{N\}\}", lambda m: f"assets/{m.group(1)}?v={versions[m.group(1)]}", html)
    html = html.replace("{{N}} min de lectura", f"{args.minutes} min de lectura")
    html = html.replace("{{DESCRIPCION_SEO_150_160_CARACTERES}}", args.description)
    for i in range(3):
        html = html.replace(f"{{{{ETIQUETA_{i + 1}}}}}", tags[i] if i < len(tags) else "")
    for key, value in {
        "TITULO": args.title, "SLUG": args.slug, "AAAA-MM-DD": args.date,
        "D mes AAAA": date_es, "ANTETITULO": args.eyebrow,
    }.items():
        html = html.replace("{{%s}}" % key, value)
    html_path.write_text(html, encoding="utf-8")

    # Tarjeta en primera posición y contador
    badges = "\n".join(f'                        <span class="badge rounded-full px-3 py-1">{t}</span>' for t in tags)
    card = CARD.format(slug=args.slug, title=args.title, date_es=date_es, minutes=args.minutes, badges=badges)
    marker = 'data-reveal-group>\n'
    index = index.replace(marker, marker + card, 1)
    index = re.sub(r"(\d+) publicados", lambda m: f"{int(m.group(1)) + 1} publicados", index, count=1)
    index_path.write_text(index, encoding="utf-8")

    # Ficha del chatbot y draft de LinkedIn
    md_path.write_text(f"""---
type: blog_post
title: "{args.title}"
route: "/blog/posts/{args.slug}.html"
date: "{args.date}"
tags: [{", ".join(f'"{t}"' for t in tags)}]
summary: "{{{{RESUMEN_UNA_FRASE}}}}"
---

# {args.title}

## Idea central {{#{{{{ID_SECCION}}}}}}

{{{{IDEA_CENTRAL}}}}

## Fuentes {{#fuentes}}

- {{{{FUENTE}}}}
""", encoding="utf-8")
    txt_path.write_text(f"{{{{DRAFT_LINKEDIN}}}}\n\nLo cuento aquí: 👇\n\n{SITE}/blog/posts/{args.slug}.html\n", encoding="utf-8")

    for path in (html_path, md_path, txt_path, index_path):
        print(f"escrito: {path.relative_to(ROOT)}")
    print("Pendiente: cuerpo, tarjeta, ficha, draft, diagrama (svg + png) y emojis. Después, check_post.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
