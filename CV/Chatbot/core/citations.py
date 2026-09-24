"""
Validation of the links the model writes to the public site.

The model is told to cite sections with URLs copied from its context, but it
can still invent an anchor, a path or a domain. Before reaching the user, every
link that points to the site (or looks like it) is rewritten to its canonical
URL: known page + known anchor, known page without the invented anchor, or no
link at all. External links (LinkedIn, universities, email) are left untouched.
"""

from __future__ import annotations

import re
from urllib.parse import unquote, urlsplit

from core.config import settings
from core.knowledge import KnowledgeBase, get_knowledge_base, normalize_route_path

CITATION_MARK = "↗"
# Markdown links [text](url) and [text](<url> "title"); images are handled the same way.
_MD_LINK_RE = re.compile(r"(?P<lead>[ \t]?)(?P<bang>!?)\[(?P<text>[^\]\n]*)\]\(\s*<?(?P<url>[^)\s>]*)>?(?:\s+\"[^\"\n]*\")?\s*\)")
# Bare URLs (GFM autolinks) and <https://...> autolinks.
_BARE_URL_RE = re.compile(r"(?<![\w(\[/])(?P<open><?)(?P<url>(?:https?://|www\.)[^\s<>()\[\]]+)(?P<close>>?)")
_TRAILING_PUNCT = ".,;:!?'\"*_"
_SITE_HOST = urlsplit(settings.public_site_url).hostname or ""
_SITE_KEY = _SITE_HOST.split(".", 1)[0]  # 'demetriotahoces': also catches invented domains
_HOST_RE = re.compile(r"^[\w-]+(?:\.[\w-]+)+$")
_FILE_SUFFIXES = (".html", ".htm", ".txt", ".pdf", ".md")


def _split(url: str):
    """urlsplit that also understands 'host/path' without scheme and relative paths."""
    if "://" in url or url.startswith("//") or ":" in url.split("/", 1)[0]:
        return urlsplit(url)
    first = url.split("/", 1)[0].split("#", 1)[0]
    if _HOST_RE.match(first) and not first.lower().endswith(_FILE_SUFFIXES):
        return urlsplit(f"//{url}")
    return urlsplit(url)


def _is_site_url(url: str) -> bool:
    parts = _split(url)
    if parts.scheme and parts.scheme not in ("http", "https"):
        return False
    if parts.netloc:
        return _SITE_KEY in parts.netloc.lower()
    # Relative link: the chat page would resolve it against /CV/, so treat it as a site path.
    return bool(parts.path)


def canonical_url(url: str, kb: KnowledgeBase | None = None) -> str | None:
    """Canonical site URL for `url`, dropping an unknown anchor; None if the page does not exist."""
    kb = kb or get_knowledge_base()
    parts = _split(url.strip())
    raw_path = parts.path or "/"
    path = normalize_route_path(raw_path)
    candidates = [path]
    if not parts.netloc and not raw_path.startswith("/"):
        candidates.append(normalize_route_path(f"/CV/{raw_path}"))  # relative to the chat page
    for base in list(candidates):
        if not base.endswith("/") and "." not in base.rsplit("/", 1)[-1]:
            candidates += [f"{base}.html", f"{base}/"]
    targets = kb.link_targets
    for candidate in candidates:
        if candidate in targets:
            page_url, anchors = targets[candidate]
            fragment = unquote(parts.fragment).strip().lower()
            return f"{page_url}#{fragment}" if fragment in anchors else page_url
    return None


def sanitize_links(text: str, kb: KnowledgeBase | None = None) -> str:
    """Rewrite every link to the site to a canonical URL; drop links to pages that do not exist."""
    if not text:
        return text
    kb = kb or get_knowledge_base()

    def fix_markdown(match: re.Match) -> str:
        url, label = match.group("url"), match.group("text")
        if url.startswith("#") or (url and not _is_site_url(url)):
            if url.startswith("#"):
                return f"{match.group('lead')}{label}" if not label.startswith(CITATION_MARK) else ""
            return match.group(0)
        fixed = canonical_url(url, kb) if url else None
        if fixed:
            return f"{match.group('lead')}{match.group('bang')}[{label}]({fixed})"
        # Unknown page: a citation chip disappears; a normal link keeps its text.
        return "" if label.strip().startswith(CITATION_MARK) else f"{match.group('lead')}{label}"

    def fix_bare(match: re.Match) -> str:
        url = match.group("url")
        trailing = ""
        while url and url[-1] in _TRAILING_PUNCT:
            url, trailing = url[:-1], url[-1] + trailing
        if not _is_site_url(url):
            return match.group(0)
        fixed = canonical_url(url, kb) or f"{settings.public_site_url}/"
        return f"{match.group('open')}{fixed}{match.group('close')}{trailing}"

    # Markdown links first; bare URLs are then only matched outside them (lookbehind on '(').
    return _BARE_URL_RE.sub(fix_bare, _MD_LINK_RE.sub(fix_markdown, text))


_LINK_DONE_RE = re.compile(r"\[[^\]\n]*\]\([^)\n]*\)")


class StreamingLinkSanitizer:
    """
    Applies sanitize_links to a token stream without ever emitting half a link.

    Text is released as soon as it cannot be part of an unfinished link: the
    trailing word (a URL may still be growing) and any '[' whose link has not
    closed yet are held back until the next token or flush().
    """

    MAX_HOLD = 600

    def __init__(self, kb: KnowledgeBase | None = None, enabled: bool = True):
        self.kb = kb
        self.enabled = enabled
        self.buffer = ""

    def feed(self, text: str) -> str:
        if not self.enabled:
            return text
        self.buffer += text
        cut = self._safe_cut(self.buffer)
        # Keep the blank before a held link with it: a dropped citation takes its space along.
        while cut > 0 and self.buffer[cut - 1] in " \t":
            cut -= 1
        if len(self.buffer) - cut > self.MAX_HOLD:
            cut = len(self.buffer)  # never stall the stream on a '[' that will not close
        ready, self.buffer = self.buffer[:cut], self.buffer[cut:]
        return sanitize_links(ready, self.kb) if ready else ""

    def flush(self) -> str:
        ready, self.buffer = self.buffer, ""
        return sanitize_links(ready, self.kb) if ready else ""

    @staticmethod
    def _safe_cut(buffer: str) -> int:
        trailing = re.search(r"\S+$", buffer)
        cut = trailing.start() if trailing else len(buffer)
        for match in re.finditer(r"\[", buffer):
            start = match.start()
            if start >= cut:
                break
            rest = buffer[start:]
            done = _LINK_DONE_RE.match(rest)
            if done:
                if start + done.end() > cut:
                    return start
                continue
            close, newline = rest.find("]"), rest.find("\n")
            if newline != -1 and (close == -1 or newline < close):
                continue  # '[' never closed on its line: plain text
            if close == -1 or close + 1 == len(rest) or rest[close + 1] == "(":
                return start  # link still open, or ']' just arrived and '(' may follow
        return cut
