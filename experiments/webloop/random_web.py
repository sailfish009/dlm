"""Random web acquisition -- no human selection, fully cached and reproducible.

Source pipeline (all CC/ODbL public APIs, single-token constants only)::

    EN Wikipedia  list=random (ns0)   -> random article titles
    EN Wikipedia  prop=pageprops      -> title -> Wikidata QID
    Wikidata      wbgetentities       -> labels + claims (+ enwiki sitelink)
    EN Wikipedia  REST summary        -> the entity's prose, split into sentences

The claims become binary Horn facts (instance_of, subclass_of, occupation,
birthplace, country, country_of, located_in, part_of); the P279 chain becomes
the class hierarchy.  Every API response is cached under ``cache/`` keyed by a
seed, so ``offline=True`` reproduces a run byte-for-byte and never touches the
network.  Rate limits are respected with exponential backoff.
"""
from __future__ import annotations

import json
import time
import urllib.parse as up
from random import Random
from typing import Dict, Iterator, List, Sequence, Tuple

from . import webref

web = webref.web

EN_API = "https://en.wikipedia.org/w/api.php"
WD_API = web.WIKIDATA
REST = web.WIKI_SUMMARY


def _url_json(url: str, *, pause: float, retries: int) -> object:
    last: Exception | None = None
    for attempt in range(max(1, int(retries))):
        time.sleep(pause * (2 ** attempt))
        try:
            with web._urlopen(url) as r:
                return json.load(r)
        except Exception as exc:  # noqa: BLE001 -- retry on any transport/HTTP error
            last = exc
    raise last if last else RuntimeError("no response")


def _cached(cache, key: str, producer):
    return cache.get(key, producer)


def random_titles(n: int, *, seed: int, cache, pause: float = 1.0, retries: int = 4) -> List[str]:
    """N random mainspace article titles (cached per seed so it is replayable)."""
    key = "enwiki_random_n%d_s%d" % (int(n), int(seed))

    def produce() -> List[str]:
        url = EN_API + "?" + up.urlencode({
            "action": "query", "list": "random", "rnnamespace": 0,
            "rnlimit": int(n), "rnfilterredir": "nonredirects", "format": "json"})
        d = _url_json(url, pause=pause, retries=retries)
        return [x["title"] for x in d.get("query", {}).get("random", [])]

    return _cached(cache, key, produce)


def _pageprops(titles: Sequence[str], *, cache, pause: float, retries: int) -> Dict[str, str]:
    """title -> wikibase QID (missing/None when the page has no item)."""
    key = "pageprops_" + up.urlencode({"t": sorted(dict.fromkeys(titles))})

    def produce() -> Dict[str, str]:
        out: Dict[str, str] = {}
        titles_ = list(dict.fromkeys(titles))
        for i in range(0, len(titles_), 40):
            chunk = titles_[i:i + 40]
            url = EN_API + "?" + up.urlencode({
                "action": "query", "prop": "pageprops",
                "titles": "|".join(chunk), "format": "json"})
            d = _url_json(url, pause=pause, retries=retries)
            for page in (d.get("query", {}).get("pages", {}) or {}).values():
                q = (page.get("pageprops", {}) or {}).get("wikibase_item")
                if q and page.get("title"):
                    out[page["title"]] = q
        return out

    return _cached(cache, key, produce)


def _entities(qids: Sequence[str], *, cache, pause: float, retries: int,
              props: str = "labels|claims|sitelinks") -> Dict[str, dict]:
    qids = [q for q in dict.fromkeys(qids) if q and q.startswith("Q")]
    key = "wd_entities_%s_%s" % (props.replace("|", "."), ",".join(sorted(qids)))

    def produce() -> Dict[str, dict]:
        out: Dict[str, dict] = {}
        for i in range(0, len(qids), 40):
            chunk = qids[i:i + 40]
            url = WD_API + "?" + up.urlencode({
                "action": "wbgetentities", "ids": "|".join(chunk), "props": props,
                "languages": "en", "sitefilter": "enwiki", "format": "json"})
            d = _url_json(url, pause=pause, retries=retries)
            out.update(d.get("entities", {}))
        return out

    return _cached(cache, key, produce)


def _labels(qids: Sequence[str], *, cache, pause: float, retries: int) -> Dict[str, str]:
    ent = _entities(qids, cache=cache, pause=pause, retries=retries, props="labels")
    return {q: (((e.get("labels", {}) or {}).get("en", {}) or {}).get("value") or q)
            for q, e in ent.items()}


def _summary(title: str, *, cache, pause: float, retries: int) -> str:
    key = "wiki_summary_" + title

    def produce() -> str:
        url = REST + up.quote(title.replace(" ", "_"))
        d = _url_json(url, pause=pause, retries=retries)
        return d.get("extract", "") or "" if isinstance(d, dict) else ""

    return _cached(cache, key, produce)


def acquire(
    n: int,
    *,
    seed: int = 0,
    cache_dir: str,
    offline: bool = False,
    subclass_depth: int = 3,
    summary_chars: int = 1200,
    pause: float = 1.0,
    retries: int = 4,
) -> Tuple[List[web.Doc], List[web.Fact]]:
    """Pull ``n`` random articles -> (docs, class_hierarchy_facts). No human labels."""
    cache = web.WebCache(cache_dir, offline=offline)
    titles = random_titles(n, seed=seed, cache=cache, pause=pause, retries=retries)
    qmap = _pageprops(titles, cache=cache, pause=pause, retries=retries)
    title_of: Dict[str, str] = {}
    for t in titles:
        q = qmap.get(t)
        if q:
            title_of.setdefault(q, t)
    qids = sorted(title_of)
    if not qids:
        return [], []

    ents = _entities(qids, cache=cache, pause=pause, retries=retries)

    # object labels (everything the seeds point at) + class nodes discovered by BFS
    targets = [t for q in qids for _p, t in web._entity_targets(ents.get(q, {}))]
    tlab = _labels(targets, cache=cache, pause=pause, retries=retries)

    hierarchy: List[web.Fact] = []
    seen: set = set()
    # BFS the class hierarchy from the *objects* (instance_of targets), like web.extract
    frontier: List[Tuple[str, int]] = [(t, 0) for t in dict.fromkeys(targets)]
    while frontier:
        batch, frontier = frontier[:40], frontier[40:]
        ids = [q for q, _ in batch if q not in seen]
        if not ids:
            continue
        cent = _entities(ids, cache=cache, pause=pause, retries=retries, props="labels|claims")
        edge_targets = [t for q in ids for p, t in web._entity_targets(cent.get(q, {})) if p == "subclass_of"]
        clab = _labels(list(dict.fromkeys(ids + edge_targets)), cache=cache, pause=pause, retries=retries)
        deeper: List[Tuple[str, int]] = []
        for q, depth in batch:
            if q in seen:
                continue
            seen.add(q)
            for pred, tgt in web._entity_targets(cent.get(q, {})):
                if pred == "subclass_of":
                    hierarchy.append(web.Fact("subclass_of", web.slug(clab.get(q, q)), web.slug(clab.get(tgt, tgt))))
                    if depth < subclass_depth:
                        deeper.append((tgt, depth + 1))
        frontier += deeper

    docs: List[web.Doc] = []
    for q in qids:
        ent = ents.get(q, {})
        labels: Dict[str, str] = {}
        facts: List[web.Fact] = []
        for pred, tgt in web._entity_targets(ent):
            if pred == "subclass_of":
                continue
            oslug = web.slug(tlab.get(tgt, tgt))
            labels[oslug] = tlab.get(tgt, tgt)
            facts.append(web.Fact(pred, web.slug(title_of[q]), oslug))
        text = _summary(title_of[q], cache=cache, pause=pause, retries=retries)[:summary_chars]
        docs.append(web.Doc(name=title_of[q], slug=web.slug(title_of[q]),
                            sentences=web.split_sentences(text), facts=facts, labels=labels))
    return docs, hierarchy


def sample_indices(pool: Sequence, k: int, *, seed: int) -> List[int]:
    """Deterministic index sample (used to grow the corpus across rounds)."""
    idx = list(range(len(pool)))
    Random(seed).shuffle(idx)
    return sorted(idx[: max(0, min(int(k), len(idx)))])
