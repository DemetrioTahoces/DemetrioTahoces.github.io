#!/usr/bin/env python3
"""Comprueba que los CV en PDF dicen lo mismo que la web (la web es la fuente de verdad).

Uso (desde cualquier directorio, solo stdlib + pdftotext de poppler):
    python3 scripts/check_cv_pdf.py

Compara index.html con CV/cv-profesional.html (fuente del PDF resumido) y con el
texto extraído de los dos PDF:

- Puestos: mismos puestos y en el mismo orden, mismo título, empresa y fechas.
- Formación: mismas titulaciones, mismas fechas y mismo estado («Finalizado»).
- Cifras: toda cifra del CV resumido existe en la web (no hay cifras inventadas) y
  las cifras de resultados de la web (hero y métricas de cada puesto) están en el CV.
- PDF resumido: su texto es el de CV/cv-profesional.html (no está desactualizado) y
  el orden de extracción es el de lectura (cada puesto en una línea, con su Stack
  antes del siguiente puesto), que es lo que lee un ATS.
- PDF completo (vista de impresión de index.html): contiene las fechas de la web.

Sin pdftotext, en local avisa y omite la parte de PDF; en CI (CI=true) falla.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "index.html"
PRO_HTML = ROOT / "CV/cv-profesional.html"
PRO_PDF = ROOT / "assets/CV-Demetrio-Tahoces-Profesional.pdf"
FULL_PDF = ROOT / "assets/CV-Demetrio-Tahoces.pdf"
# Cifras del hero que cuentan entradas del propio CV en vez de dar un resultado:
# «2 másteres» ya se valida al comparar la formación.
HERO_SKIP = {"2 másteres Teleco e IA aplicada"}
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "path", "rect"}
BLOCK = {"p", "li", "div", "h1", "h2", "h3", "section", "ul", "header", "span"}
FIGURE = re.compile(r"(?<![\w/.,-])\d+(?:-\d+)?%?(?![\w/])")


def norm(text: str) -> str:
    """Espacios y guiones normalizados: '04/2026 — 10/2026' == '04/2026 – 10/2026'."""
    text = re.sub(r"\s*[—–-]\s*", " - ", text)
    return re.sub(r"\s+", " ", text).strip()


def figures(text: str) -> set[str]:
    text = re.sub(r"(\d)\s*[—–-]\s*(\d)", r"\1-\2", text)
    text = re.sub(r"https?://\S+|\b[\w.-]+\.(?:io|com|html)\S*", " ", text)
    text = re.sub(r"\b\d{2}/\d{4}\b|\b(?:19|20)\d{2}(?:-(?:19|20)\d{2})?\b", " ", text)
    return set(FIGURE.findall(text))


class Tree(HTMLParser):
    """Árbol mínimo de la página: nodos con tag, atributos e hijos (nodos o texto)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "#root", "attrs": {}, "children": [], "parent": None}
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": {k: v or "" for k, v in attrs}, "children": [], "parent": self.cur}
        self.cur["children"].append(node)
        if tag not in VOID:
            self.cur = node

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node["tag"] != tag:
            node = node["parent"]
        if node is not self.root:
            self.cur = node["parent"]

    def handle_data(self, data):
        self.cur["children"].append(data)


def parse(path: Path) -> dict:
    tree = Tree()
    tree.feed(path.read_text(encoding="utf-8"))
    return tree.root


def walk(node):
    for child in node["children"]:
        if isinstance(child, dict):
            yield child
            yield from walk(child)


def text(node) -> str:
    out = []
    for child in node["children"]:
        if isinstance(child, str):
            out.append(child)
        elif child["tag"] not in {"script", "style", "template"}:
            inner = text(child)
            out.append(f" {inner} " if child["tag"] in BLOCK else inner)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def has_class(node, cls: str) -> bool:
    return cls in node["attrs"].get("class", "").split()


def find(node, pred):
    return next((n for n in walk(node) if pred(n)), None)


def find_all(node, pred):
    return [n for n in walk(node) if pred(n)]


def web_data() -> dict:
    root = parse(WEB)
    jobs = []
    for card in find_all(root, lambda n: has_class(n, "job-card")):
        link = find(card, lambda n: n["tag"] == "a" and has_class(n, "card-link"))
        jobs.append({
            "id": card["attrs"].get("id"),
            "page": link["attrs"]["href"].split("/")[-1],
            "title": text(link),
            "company": text(find(card, lambda n: has_class(n, "job-company"))),
            "dates": text(find(card, lambda n: has_class(n, "job-date"))),
            "metrics": [text(li) for ul in find_all(card, lambda n: has_class(n, "job-metrics"))
                        for li in find_all(ul, lambda n: n["tag"] == "li")],
        })
    edu = {}
    for card in find_all(root, lambda n: has_class(n, "edu-card") and n["attrs"].get("id")):
        date = find(card, lambda n: has_class(n, "edu-date"))
        if date:
            edu[card["attrs"]["id"]] = text(date)
    hero = find(root, lambda n: has_class(n, "hero-metrics"))
    hero_metrics = [text(li) for li in find_all(hero, lambda n: n["tag"] == "li")] if hero else []
    corpus = [text(root)] + [text(parse(p)) for p in sorted((ROOT / "CV").glob("*.html")) if p != PRO_HTML]
    return {"jobs": jobs, "edu": edu, "hero": hero_metrics, "corpus": " ".join(corpus)}


def pro_data() -> dict:
    root = parse(PRO_HTML)
    jobs = []
    for job in find_all(root, lambda n: has_class(n, "job")):
        title = find(job, lambda n: has_class(n, "job-title"))
        link = find(title, lambda n: n["tag"] == "a")
        lead = "".join(c for c in title["children"] if isinstance(c, str))
        jobs.append({
            "page": link["attrs"]["href"].split("/")[-1],
            "title": re.sub(r"\s*·\s*$", "", lead.strip()),
            "org": text(link),
            "line": re.sub(r"\s+", " ", text(title)),
            "dates": text(find(title, lambda n: has_class(n, "dates"))),
            "has_stack": find(job, lambda n: has_class(n, "stack")) is not None,
        })
    edu = {}
    for item in find_all(root, lambda n: has_class(n, "edu-item")):
        link = find(item, lambda n: n["tag"] == "a")
        edu[link["attrs"]["href"].split("#")[-1]] = {
            "dates": text(find(item, lambda n: has_class(n, "dates"))), "text": text(item)}
    return {"jobs": jobs, "edu": edu, "text": text(find(root, lambda n: has_class(n, "page")))}


def pdf_text(path: Path, exe: str) -> str:
    out = subprocess.run([exe, "-enc", "UTF-8", str(path), "-"], capture_output=True, check=True)
    return re.sub(r"\s+", " ", out.stdout.decode("utf-8"))


def alnum(value: str) -> str:
    return re.sub(r"[^0-9a-záéíóúüñ]", "", value.lower())


def compare_html(web: dict, pro: dict, errors: list[str]) -> None:
    web_pages = [j["page"] for j in web["jobs"]]
    pro_pages = [j["page"] for j in pro["jobs"]]
    if pro_pages != web_pages:
        errors.append(f"puestos distintos o en otro orden: web {web_pages} / CV resumido {pro_pages}")
    by_page = {j["page"]: j for j in pro["jobs"]}
    for w in web["jobs"]:
        p = by_page.get(w["page"])
        if not p:
            continue
        where = f"puesto {w['id']}"
        if norm(p["title"]) != norm(w["title"]):
            errors.append(f"{where}: título «{p['title']}» en el CV resumido y «{w['title']}» en la web")
        if norm(p["org"]).lower() not in norm(w["company"]).lower():
            errors.append(f"{where}: empresa «{p['org']}» en el CV resumido no aparece en «{w['company']}»")
        if norm(p["dates"]) != norm(w["dates"]):
            errors.append(f"{where}: fechas «{p['dates']}» en el CV resumido y «{w['dates']}» en la web")

    if set(pro["edu"]) != set(web["edu"]):
        errors.append(f"formación distinta: web {sorted(web['edu'])} / CV resumido {sorted(pro['edu'])}")
    for anchor, wdate in web["edu"].items():
        p = pro["edu"].get(anchor)
        if not p:
            continue
        dates, _, status = (part.strip() for part in wdate.partition("·"))
        if norm(p["dates"]) != norm(dates):
            errors.append(f"formación {anchor}: fechas «{p['dates']}» en el CV resumido y «{dates}» en la web")
        if status and status.lower() not in p["text"].lower():
            errors.append(f"formación {anchor}: la web dice «{status}» y el CV resumido no")
        if not status and "finalizado" in p["text"].lower():
            errors.append(f"formación {anchor}: el CV resumido dice «finalizado» y la web no")

    for fig in sorted(figures(pro["text"]) - figures(web["corpus"])):
        errors.append(f"cifra «{fig}» en el CV resumido que no aparece en la web")
    pro_figs = figures(pro["text"])
    results = [m for j in web["jobs"] for m in j["metrics"]] + [h for h in web["hero"] if h not in HERO_SKIP]
    for metric in results:
        for fig in sorted(figures(metric) - pro_figs):
            errors.append(f"cifra «{fig}» de la web («{metric}») no aparece en el CV resumido")


def compare_pdfs(web: dict, pro: dict, exe: str, errors: list[str]) -> None:
    txt = pdf_text(PRO_PDF, exe)
    if alnum(txt) != alnum(pro["text"]):
        errors.append(f"{PRO_PDF.name} no corresponde a CV/cv-profesional.html: regenéralo (comando en README.md)")
    pos = 0
    for i, job in enumerate(pro["jobs"]):
        start = txt.find(job["line"], pos)
        if start < 0:
            errors.append(f"{PRO_PDF.name}: «{job['line']}» no se extrae en una línea y en orden de lectura")
            break
        nxt = pro["jobs"][i + 1]["line"] if i + 1 < len(pro["jobs"]) else "PROYECTO DESTACADO"
        end = txt.find(nxt, start + 1)
        if job["has_stack"] and "Stack:" not in txt[start:end if end > 0 else None]:
            errors.append(f"{PRO_PDF.name}: el Stack de {job['org']} no se extrae dentro de su puesto")
        pos = start + 1
    full = norm(pdf_text(FULL_PDF, exe))
    for w in web["jobs"]:
        if norm(w["dates"]) not in full:
            errors.append(f"{FULL_PDF.name}: faltan las fechas «{w['dates']}» de {w['id']}; regenéralo")
    for anchor, wdate in web["edu"].items():
        if norm(wdate) not in full:
            errors.append(f"{FULL_PDF.name}: falta «{wdate}» de {anchor}; regenéralo")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    web, pro = web_data(), pro_data()
    compare_html(web, pro, errors)
    exe = shutil.which("pdftotext")
    if exe:
        compare_pdfs(web, pro, exe, errors)
    else:
        msg = "pdftotext (poppler-utils) no está instalado: no se ha comprobado el texto de los PDF"
        (errors if os.environ.get("CI") else warnings).append(msg)
    for w in warnings:
        print(f"AVISO: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"{len(web['jobs'])} puestos, {len(web['edu'])} titulaciones, {len(figures(pro['text']))} cifras "
          f"del CV resumido; {len(errors)} errores, {len(warnings)} avisos")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
