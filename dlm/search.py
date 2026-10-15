"""DLM v0.0054 -- generic web search providers (untrusted).

The model reaches the web for three kinds of source, and none of them is
domain-specific knowledge -- they are *ways to look things up*:

* a documentation **object inventory** (Sphinx ``objects.inv``) resolves a symbol
  to its canonical definition page; the definition paragraph is read verbatim;
* a **Wikipedia** article/summary gives the encyclopedic opening paragraph;
* a **Stack Exchange** search gives free-text Q&A titles (noisy corroboration).

Each provider returns *evidence* (text + URL + title), never a fact.  Turning
evidence into a ``meaning``/``dataset_of`` fact is the acquisition layer's job
(:mod:`dlm.acquire`), and even that fact is untrusted -- the kernel consumes it
like any other and re-checks whatever it concludes.  A provider that cannot be
reached, or returns nothing, abstains (``None`` / ``[]``).
"""
from __future__ import annotations

import gzip
import html as _html
import json
import re
import urllib.parse as _up
import zlib
from typing import Dict, List, Optional, Sequence, Tuple

from .web import Web

__all__ = [
    "reduce_text", "sphinx_inventory", "resolve_object", "extract_definition",
    "wikipedia_search_titles", "wikipedia_summary",
    "wikidata_search", "wikidata_entities", "wikidata_labels",
    "mediawiki_random_titles", "mediawiki_pageprops",
    "stackexchange_items", "stackexchange_titles", "stackexchange_question",
    "WIKI_API", "WIKI_SUMMARY", "WIKIDATA", "SE_API",
]

_HREF = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")

# -- cue reduction (generic) --------------------------------------------------
Cues = Tuple[Tuple[str, Tuple[str, ...]], ...]


def reduce_text(text: str, cues: Cues) -> Optional[str]:
    """Map ``text`` to the FIRST concept whose cue phrase occurs (or ``None``).

    This is a reduction, not knowledge: it only says *which* given idea a
    verbatim source paragraph mentions.  The cues (and their priority order) are
    a GIVEN vocabulary supplied by the caller -- the provider names no domain.
    """
    low = _WS.sub(" ", (text or "").lower())
    for concept, phrases in cues:
        for p in phrases:
            if p in low:
                return concept
    return None


# -- documentation object inventory (Sphinx ``objects.inv``) -----------------
def sphinx_inventory(web: Web, url: str,
                     prefixes: Sequence[str] = ("torch.",)) -> Dict[str, str]:
    """Fetch + parse a Sphinx object inventory: ``{object name: doc URI}``.

    The inventory is the documentation's own search index; filtering by
    ``prefixes`` is only a reduction ("what the model is willing to ask about").
    """
    raw = web.get_bytes(url)
    if not raw:
        return {}
    i = 0
    for _ in range(4):  # four header lines precede the zlib payload
        j = raw.find(b"\n", i)
        if j < 0:
            break
        i = j + 1
    try:
        data = zlib.decompress(raw[i:]).decode("utf-8", "replace")
    except zlib.error:
        return {}
    out: Dict[str, str] = {}
    for line in data.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        name, uri = parts[0], parts[3]
        if prefixes and not any(name.startswith(p) for p in prefixes):
            continue
        if "/" in name:
            continue
        out[name] = uri.split("#")[0]
    return out


def _norm_label(label: str) -> str:
    return re.sub(r"[^a-z0-9_.]", "", (label or "").lower())


def resolve_object(label: str, inventory: Dict[str, str],
                   receiver_hints: Optional[Dict[str, str]] = None
                   ) -> Tuple[Optional[str], str]:
    """Resolve a human label to an inventory object name (or ``None``).

    Thin dotted names are preferred (``torch.nn.Conv2d`` over
    ``torch.ao.quantization.Conv2d``).  ``receiver_hints`` may disambiguate a
    method label ``head.tail`` (e.g. ``loss.backward``) toward the documented
    class that owns it.  Returns ``(name, how)`` with ``how`` recording the rule
    used, so every resolution is auditable.
    """
    receiver_hints = receiver_hints or {}
    lab = _norm_label(label)
    low = {k.lower(): k for k in inventory}
    if lab in low:
        return low[lab], "exact"
    suffix = [k for k in inventory if k.lower().endswith("." + lab)]
    if suffix:
        return min(suffix, key=lambda k: (k.count("."), len(k))), "suffix"
    head, _, last = lab.rpartition(".")
    segs = [k for k in inventory if k.lower().endswith("." + last)]
    if not segs:
        return None, "miss"
    hint = receiver_hints.get(head)
    if hint:
        h = [k for k in segs if k.startswith(hint)]
        if h:
            return min(h, key=lambda k: (k.count("."), len(k))), "receiver-hint"
    return min(segs, key=lambda k: (k.count("."), len(k))), "last-segment"


def extract_definition(page: str, anchor: str) -> Optional[str]:
    """The first paragraph of documentation after ``anchor`` on an HTML page."""
    i = page.find('id="%s"' % anchor)
    seg = page[i:] if i >= 0 else page
    m = re.search(r"<p>(.*?)</p>", seg, re.S)
    if not m:
        return None
    text = _html.unescape(_HREF.sub(" ", m.group(1)))
    text = _WS.sub(" ", text).strip()
    return text or None


# -- Wikipedia ----------------------------------------------------------------
WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def wikipedia_search_titles(web: Web, query: str, limit: int = 4) -> List[str]:
    """Canonical article titles for a search query (the encyclopedia's index)."""
    url = WIKI_API + "?" + _up.urlencode(
        {"action": "query", "format": "json", "list": "search",
         "srsearch": query, "srlimit": limit})
    data = web.get_json(url)
    if not isinstance(data, dict):
        return []
    return [it.get("title", "") for it in
            (data.get("query", {}).get("search") or []) if it.get("title")]


def wikipedia_summary(web: Web, title: str) -> Optional[dict]:
    """The opening paragraph of an article (verbatim, with its canonical URL)."""
    url = WIKI_SUMMARY + _up.quote((title or "").replace(" ", "_"), safe="")
    data = web.get_json(url)
    if not isinstance(data, dict):
        return None
    extract = (data.get("extract") or "").strip()
    if not extract or str(data.get("type", "")).endswith("not_found"):
        return None
    page = ((data.get("content_urls") or {}).get("desktop") or {}).get("page")
    return {"title": data.get("title", title), "extract": extract, "url": page or url}


# -- Wikidata (structured claims + labels + English sitelink) -----------------
WIKIDATA = "https://www.wikidata.org/w/api.php"


def wikidata_search(web: Web, name: str, language: str = "en", limit: int = 1
                    ) -> Optional[Tuple[str, str]]:
    """The top Wikidata item for a name, as ``(QID, label)`` (or ``None``)."""
    url = WIKIDATA + "?" + _up.urlencode(
        {"action": "wbsearchentities", "search": name, "language": language,
         "limit": limit, "format": "json"})
    data = web.get_json(url)
    if not isinstance(data, dict):
        return None
    hits = data.get("search") or []
    if not hits:
        return None
    return hits[0].get("id"), (hits[0].get("label") or name)


def wikidata_entities(web: Web, ids: Sequence[str],
                      props: str = "labels|claims|sitelinks",
                      languages: str = "en", sitefilter: str = "enwiki"
                      ) -> Dict[str, dict]:
    """``{QID: entity}`` for the requested ids (batched 40 at a time)."""
    out: Dict[str, dict] = {}
    ids = [i for i in dict.fromkeys(ids) if i]
    for i in range(0, len(ids), 40):
        chunk = ids[i:i + 40]
        url = WIKIDATA + "?" + _up.urlencode(
            {"action": "wbgetentities", "ids": "|".join(chunk), "props": props,
             "languages": languages, "sitefilter": sitefilter, "format": "json"})
        data = web.get_json(url)
        if isinstance(data, dict):
            out.update(data.get("entities", {}) or {})
    return out


def wikidata_labels(web: Web, ids: Sequence[str]) -> Dict[str, str]:
    """``{QID: English label}`` (the QID itself when unlabelled)."""
    ent = wikidata_entities(web, ids, props="labels")
    return {q: (((e.get("labels", {}) or {}).get("en", {}) or {}).get("value") or q)
            for q, e in ent.items()}


def mediawiki_random_titles(web: Web, n: int, api: str = WIKI_API) -> List[str]:
    """``n`` random mainspace article titles from the encyclopedia's own index."""
    url = api + "?" + _up.urlencode(
        {"action": "query", "list": "random", "rnnamespace": 0,
         "rnlimit": int(n), "rnfilterredir": "nonredirects", "format": "json"})
    data = web.get_json(url)
    if not isinstance(data, dict):
        return []
    return [x.get("title", "") for x in data.get("query", {}).get("random", [])]


def mediawiki_pageprops(web: Web, titles: Sequence[str], api: str = WIKI_API
                        ) -> Dict[str, str]:
    """``{title: wikibase QID}`` for the pages that carry one."""
    out: Dict[str, str] = {}
    titles_ = [t for t in dict.fromkeys(titles) if t]
    for i in range(0, len(titles_), 40):
        chunk = titles_[i:i + 40]
        url = api + "?" + _up.urlencode(
            {"action": "query", "prop": "pageprops", "titles": "|".join(chunk),
             "format": "json"})
        data = web.get_json(url)
        if not isinstance(data, dict):
            continue
        for page in (data.get("query", {}).get("pages", {}) or {}).values():
            q = (page.get("pageprops", {}) or {}).get("wikibase_item")
            if q and page.get("title"):
                out[page["title"]] = q
    return out


# -- Stack Exchange -----------------------------------------------------------
SE_API = "https://api.stackexchange.com/2.3/"


def _maybe_gunzip(raw: bytes) -> bytes:
    if raw[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(raw)
        except OSError:
            return raw
    return raw


def stackexchange_items(web: Web, path: str, params: dict) -> List[dict]:
    """Raw Stack Exchange API items for ``path`` + ``params`` (gzip handled)."""
    url = SE_API + path + "?" + _up.urlencode(params)
    raw = web.get_bytes(url)
    if raw is None:
        return []
    try:
        data = json.loads(_maybe_gunzip(raw))
    except ValueError:
        return []
    return list(data.get("items") or [])


def stackexchange_titles(web: Web, query: str, site: str = "stackoverflow",
                         pagesize: int = 5, sort: str = "relevance") -> List[str]:
    items = stackexchange_items(web, "search/advanced", {
        "order": "desc", "sort": sort, "q": query, "site": site,
        "pagesize": pagesize})
    return [_html.unescape(it.get("title", "")) for it in items]


def stackexchange_question(web: Web, label: str, query_prefix: str = "",
                           site: str = "stackoverflow") -> Optional[dict]:
    """The top question for a label: ``{provider,title,link}`` or ``None``."""
    q = (query_prefix + " " + label).strip()
    items = stackexchange_items(web, "search/advanced", {
        "order": "desc", "sort": "relevance", "q": q, "site": site, "pagesize": 3})
    if not items:
        return None
    top = items[0]
    return {"provider": "stackexchange",
            "title": _html.unescape(top.get("title", ""))[:200],
            "link": top.get("link", "")}