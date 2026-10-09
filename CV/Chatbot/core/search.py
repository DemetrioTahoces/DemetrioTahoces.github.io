"""
Keyword search over the knowledge base sections (BM25), for the MCP `search` tool.

The corpus is a few hundred sections, so an in-memory index built once per
instance is enough: no embeddings, no external service. Accents and case are
folded and a crude plural strip lets "microservicio" match "microservicios".
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from core.knowledge import Document, KnowledgeBase, Section, get_knowledge_base

SNIPPET_CHARS = 700
_K1, _B = 1.5, 0.75
_TITLE_BOOST = 3  # section and document titles count as if repeated
_WORD_RE = re.compile(r"[a-z0-9][a-z0-9+#.]*[a-z0-9+#]|[a-z0-9]")
_STOPWORDS = frozenset(
    """a al algo como con cual cuales de del el en es esta este esto la las lo los mas me mi muy no o para pero
    por que se sin sobre su sus te tiene tu un una uno y ya ha han he hay
    an and are as at be by did do does for from has have he his how in is it its of on or the to was what
    when where which who with""".split()
)


def _fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def _stem(word: str) -> str:
    """Drop a final 's' and then a final 'e', so singular and plural meet ("sensor"/"sensores", "clase"/"clases")."""
    if len(word) > 3 and word.endswith("s"):
        word = word[:-1]
    if len(word) > 4 and word.endswith("e"):
        word = word[:-1]
    return word


def tokenize(text: str) -> list[str]:
    return [_stem(w) for w in _WORD_RE.findall(_fold(text)) if w not in _STOPWORDS]


@dataclass(frozen=True)
class SearchHit:
    document: Document
    section: Section
    score: float

    def as_dict(self) -> dict:
        content = self.section.content
        snippet = content if len(content) <= SNIPPET_CHARS else content[:SNIPPET_CHARS].rsplit(" ", 1)[0] + " …"
        return {
            "document": self.document.name,
            "document_title": self.document.title,
            "section": self.section.title,
            "url": self.document.section_url(self.section),
            "snippet": snippet,
            "truncated": len(content) > SNIPPET_CHARS,
        }


class SectionIndex:
    def __init__(self, kb: KnowledgeBase):
        self.entries: list[tuple[Document, Section, Counter, int]] = []
        for doc in kb.cv_documents + kb.blog_documents:
            for section in doc.sections:
                terms = Counter(tokenize(section.content))
                for term in tokenize(f"{doc.title} {section.title}"):
                    terms[term] += _TITLE_BOOST
                self.entries.append((doc, section, terms, sum(terms.values())))
        self.avg_len = sum(e[3] for e in self.entries) / len(self.entries) if self.entries else 1.0
        df = Counter(term for *_, terms, _ in self.entries for term in terms)
        n = len(self.entries)
        self.idf = {term: math.log(1 + (n - f + 0.5) / (f + 0.5)) for term, f in df.items()}

    def search(self, query: str, limit: int = 5) -> list[SearchHit]:
        query_terms = set(tokenize(query))
        hits = []
        for doc, section, terms, length in self.entries:
            score = 0.0
            for term in query_terms:
                tf = terms.get(term, 0)
                if tf:
                    score += self.idf[term] * tf * (_K1 + 1) / (tf + _K1 * (1 - _B + _B * length / self.avg_len))
            if score > 0:
                hits.append(SearchHit(doc, section, score))
        hits.sort(key=lambda h: (-h.score, h.document.order, h.document.name))
        return hits[:limit]


@lru_cache(maxsize=1)
def get_section_index() -> SectionIndex:
    return SectionIndex(get_knowledge_base())
