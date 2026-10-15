"""Domain knowledge acquisition -- what a DATASET contains (untrusted).

The library-semantics acquirer (``knowledge.py``) learns what a *symbol* means
(``DataLoader`` -> data_loading).  That is still not enough to say *what a program
recognizes*: the code instantiates ``datasets.MNIST``, but the meaning of that
dataset -- "a database of handwritten digits" -- is neither in the code nor in a
symbol's own definition.  So the reader SEARCHES for it and reduces the results to
``dataset_of(symbol, entity)`` facts.

Two web providers, both untrusted:

* ``wikipedia`` -- the Wikipedia REST **summary** service.  For a dataset symbol
  it returns the encyclopedic opening paragraph ("The MNIST database is a large
  database of handwritten digits ..."), which the cue lexicon reduces to the
  domain ENTITY the dataset records.  This is the authoritative source.
* ``search`` -- Stack Exchange's API (free-text Q&A).  Noisier than Wikipedia, so
  it is used to *cross-check* and to *fall back* when Wikipedia has no summary.

This is the search-driven half of the loop: the gist layer reports a *hole*
(``dlm.gist.external_holes``), the reader searches for the hole, acquires a fact
carrying provenance, and re-runs.  Offline replay reads only the reduced cache; a
dataset the acquirer cannot reduce simply yields no fact (abstain).

Nothing here is trusted: the kernel consumes ``dataset_of`` like any other fact.
"""
from __future__ import annotations

import gzip
import html as _html
import json
import os
import re
import urllib.parse as _up
import urllib.request
from typing import Dict, List, Optional, Tuple

from .knowledge import UA, SE_API, _Fetcher  # reuse the cached HTTP layer

DOMAIN_VERSION = 2

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# A reduction heuristic ("what to ASK about"), not knowledge: dataset-looking
# constructors.  A symbol is a dataset candidate if its label mentions "dataset"
# or one of the well-known vision dataset names.
DATASET_HINTS: Tuple[str, ...] = (
    "mnist", "fashion", "cifar", "kmnist", "imagenet", "coco", "voc",
    "caltech", "svhn", "stl", "omniglot", "usps", "emnist",
)

# Free-text cues (definitions / Q&A titles) -> the domain ENTITY a dataset
# records.  Order is disambiguation priority: specific before generic.
DATASET_CUES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("handwritten_digit", ("handwritten digit", "hand-written digit", "hand written digit",
                           "digit recognition", "digits 0-9", "digits and",
                           "digits are", "handwritten number")),
    ("clothing_item", ("fashion", "clothing", "garment", "apparel")),
    ("character", ("character recognition", "characters", "letters")),
    ("object_category", ("object categor", "object class", "categories of object",
                         "object recognition", "image classification",
                         "different classes", "classes represent", "100 classes",
                         "10 classes")),
    ("natural_image", ("natural image", "photograph", "color image")),
)

# entity slug -> a readable phrase for the realizer (untrusted gloss vocabulary).
ENTITY_PHRASES: Dict[str, str] = {
    "handwritten_digit": "handwritten digits",
    "clothing_item": "clothing items",
    "character": "characters",
    "object_category": "object categories",
    "natural_image": "natural images",
}


def dataset_candidates(facts: List[tuple], labels: Dict[str, str]) -> Dict[str, str]:
    """Dataset-looking instances the code creates: ``{slug: label}``.

    A reduction for the *question* only -- it never says what the dataset is.
    """
    out: Dict[str, str] = {}
    for f in facts:
        if f[0] != "creates":
            continue
        slug = f[2]
        label = labels.get(slug, slug)
        low = label.lower()
        if "dataset" in low or any(h in low for h in DATASET_HINTS):
            out.setdefault(slug, label)
    return out


def reduce_entity(text: str) -> Optional[str]:
    low = re.sub(r"\s+", " ", (text or "").lower())
    for entity, phrases in DATASET_CUES:
        for p in phrases:
            if p in low:
                return entity
    return None


# ---------------------------------------------------------------------------
# provider 1 (primary): Wikipedia REST summary
# ---------------------------------------------------------------------------
def _wiki_search_titles(fetch: _Fetcher, query: str, limit: int = 4) -> List[str]:
    """Canonical article titles for a search query (the encyclopedia's index)."""
    url = WIKI_API + "?" + _up.urlencode(
        {"action": "query", "format": "json", "list": "search",
         "srsearch": query, "srlimit": limit})
    raw = fetch.get(url)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    return [it.get("title", "") for it in
            (data.get("query", {}).get("search") or []) if it.get("title")]


def _wiki_summary(fetch: _Fetcher, title: str) -> Optional[dict]:
    """The opening paragraph of an article (verbatim, with its URL)."""
    url = WIKI_SUMMARY + _up.quote(title.replace(" ", "_"), safe="")
    raw = fetch.get(url)
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    extract = (data.get("extract") or "").strip()
    if not extract or str(data.get("type", "")).endswith("not_found"):
        return None
    page = ((data.get("content_urls") or {}).get("desktop") or {}).get("page")
    return {"title": data.get("title", title), "extract": extract,
            "url": page or url}


def _wiki_lookup(fetch: _Fetcher, label: str) -> Tuple[Optional[str], Optional[dict], List[str]]:
    """Look a dataset up on Wikipedia: direct title first, then search fallback.

    Returns ``(entity, summary, evidence)``.  ``evidence`` is the human-readable
    first sentences consulted, kept for audit even when no cue fired.
    """
    evidence: List[str] = []
    titles = [label]
    for t in _wiki_search_titles(fetch, f"{label} dataset"):
        if t.lower() != label.lower():
            titles.append(t)
    for title in titles:
        summ = _wiki_summary(fetch, title)
        if not summ:
            continue
        snippet = re.sub(r"\s+", " ", summ["extract"])[:240]
        evidence.append(f"wikipedia:{summ['title']}: {snippet}")
        entity = reduce_entity(summ["extract"])
        if entity:
            return entity, summ, evidence
    return None, None, evidence


# ---------------------------------------------------------------------------
# provider 2 (cross-check / fallback): Stack Exchange free-text search
# ---------------------------------------------------------------------------
def _se_titles(fetch: _Fetcher, query: str, pagesize: int = 5) -> List[str]:
    url = SE_API + "search/advanced?" + _up.urlencode(
        {"order": "desc", "sort": "relevance", "q": query,
         "site": "stackoverflow", "pagesize": pagesize})
    raw = fetch.get(url)
    if not raw:
        return []
    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except OSError:
            return []
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    return [_html.unescape(it.get("title", "")) for it in (data.get("items") or [])]


def _se_lookup(fetch: _Fetcher, label: str) -> Tuple[Optional[str], List[str]]:
    """Cross-check a dataset label against Stack Overflow Q&A titles."""
    titles = _se_titles(fetch, f"pytorch {label} dataset")
    for title in titles:
        entity = reduce_entity(title)
        if entity:
            return entity, titles
    return None, titles


# ---------------------------------------------------------------------------
# cache
# ---------------------------------------------------------------------------
def _domain_path(cache_dir: str) -> str:
    return os.path.join(cache_dir, "domain_knowledge.json")


def load_domain(cache_dir: str) -> dict:
    path = _domain_path(cache_dir)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            db = json.load(fh)
        # A version bump invalidates older records: they are re-searched online
        # (and simply dropped under ``--offline``, so replay stays deterministic).
        if db.get("version") == DOMAIN_VERSION:
            return db
    return {"version": DOMAIN_VERSION, "datasets": {}}


def save_domain(cache_dir: str, db: dict) -> None:
    with open(_domain_path(cache_dir), "w", encoding="utf-8") as fh:
        json.dump(db, fh, indent=1, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------
# acquisition
# ---------------------------------------------------------------------------
def acquire_domain(candidates: Dict[str, str], cache_dir: str,
                   offline: bool = False, search: bool = True) -> dict:
    """Search for what each dataset candidate contains; cache reduced records.

    ``offline`` reads only cached records (no network); a candidate with no cached
    record simply yields no fact.  Returns ``{entities, records, stats}``.
    """
    db = load_domain(cache_dir)
    ds: Dict[str, dict] = db.setdefault("datasets", {})
    fetch = _Fetcher(cache_dir, offline=offline)
    fetched_new = 0
    changed = False

    for slug, label in sorted(candidates.items()):
        if ds.get(slug, {}).get("v") == DOMAIN_VERSION:
            continue
        if offline or not search:
            continue
        evidence: List[str] = []
        providers: List[str] = []

        entity, summ, wev = _wiki_lookup(fetch, label)
        evidence.extend(wev)
        if summ:
            providers.append("wikipedia")

        se_entity, se_titles = _se_lookup(fetch, label)
        if se_titles:
            providers.append("search")
            evidence.extend(f"search: {t}" for t in se_titles[:3])

        # Wikipedia decides; Stack Exchange only corroborates or fills the gap.
        final = entity or se_entity
        ds[slug] = {
            "slug": slug, "label": label, "v": DOMAIN_VERSION,
            "entity": final,
            "providers": providers,
            "wikipedia": ({"title": summ["title"], "url": summ["url"],
                           "entity": entity} if summ else None),
            "search": {"titles": se_titles[:5], "entity": se_entity},
            "evidence": evidence,
        }
        fetched_new += 1
        changed = True

    if changed:
        save_domain(cache_dir, db)

    entities = {slug: rec["entity"] for slug, rec in ds.items()
                if rec.get("entity")}
    records = sorted(ds.values(), key=lambda r: r["slug"])
    return {"entities": entities, "records": records,
            "stats": {"candidates": len(candidates), "acquired": len(entities),
                      "cached_records": len(ds), "fetched_new": fetched_new,
                      "offline": offline}}


def domain_facts(entities: Dict[str, str]) -> List[Tuple[str, str, str]]:
    """``{slug: entity}`` -> ``dataset_of`` ground fact tuples."""
    return [("dataset_of", slug, entity) for slug, entity in sorted(entities.items())]