"""DLM v0.0054 -- random web acquisition (experiment glue).

The model owns web access now (:mod:`dlm.web`) and the providers
(:mod:`dlm.search`); this module keeps only the experiment's GIVEN pipeline
choice and the seed-keyed record cache that makes a run replayable::

    EN Wikipedia  list=random    -> random article titles
    EN Wikipedia  prop=pageprops -> title -> Wikidata QID
    Wikidata      wbgetentities  -> labels + claims (+ enwiki sitelink)
    EN Wikipedia  REST summary   -> the entity's prose, split into sentences

The claims become binary Horn facts (``instance_of``, ``subclass_of``, ...); the
P279 chain becomes the class hierarchy.  Raw responses are byte-cached by the
model under ``<cache>/fetch/``; the reduced docs/hierarchy are computed in
memory and never asserted -- the kernel is the only judge.
"""
from __future__ import annotations

import json
import os
from random import Random
from typing import Dict, List, Sequence, Tuple

from dlm.search import (mediawiki_pageprops, mediawiki_random_titles,
                        wikidata_entities, wikidata_labels, wikipedia_summary)
from dlm.web import Web

try:
    from . import web
except ImportError:  # run as a top-level script
    import web

__all__ = ["random_titles", "acquire", "sample_indices"]


def _record_cache(cache_dir: str, key: str, producer):
    """Seed-keyed reduced-record cache, so an offline replay sees the same corpus."""
    path = os.path.join(cache_dir, "records", key + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    value = producer()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(value, fh, ensure_ascii=False)
    return value


def random_titles(n: int, *, seed: int, client: Web, offline: bool = False) -> List[str]:
    """N random mainspace article titles, keyed by ``(n, seed)`` for replay.

    The query is the experiment's GIVEN choice; ``dlm.web.Web`` performs and
    byte-caches the fetch.  ``seed`` selects a stored draw so distinct seeds can
    keep distinct (already-drawn) corpora.
    """
    return _record_cache(
        client.root, "titles_n%d_s%d" % (int(n), int(seed)),
        lambda: mediawiki_random_titles(client, n))


def _entities(client: Web, qids: Sequence[str],
              props: str = "labels|claims|sitelinks") -> Dict[str, dict]:
    return wikidata_entities(client, [q for q in dict.fromkeys(qids)
                                      if q and q.startswith("Q")], props=props)


def acquire(
    n: int,
    *,
    seed: int = 0,
    cache_dir: str,
    offline: bool = False,
    subclass_depth: int = 3,
    summary_chars: int = 1200,
    pause: float = 1.0,     # kept for call compatibility; transport is dlm.web.Web
    retries: int = 4,       # kept for call compatibility
) -> Tuple[List[web.Doc], List[web.Fact]]:
    """Pull ``n`` random articles -> (docs, class_hierarchy_facts). No human labels."""
    client = Web(cache_dir, offline=offline)
    titles = random_titles(n, seed=seed, client=client, offline=offline)
    qmap = mediawiki_pageprops(client, titles)
    title_of: Dict[str, str] = {}
    for t in titles:
        q = qmap.get(t)
        if q:
            title_of.setdefault(q, t)
    qids = sorted(title_of)
    if not qids:
        return [], []

    ents = _entities(client, qids)

    # object labels (everything the seeds point at) + class nodes discovered by BFS
    targets = [t for q in qids for _p, t in web._entity_targets(ents.get(q, {}))]
    tlab = wikidata_labels(client, targets)

    hierarchy: List[web.Fact] = []
    seen: set = set()
    # BFS the class hierarchy from the *objects* (instance_of targets), like web.extract
    frontier: List[Tuple[str, int]] = [(t, 0) for t in dict.fromkeys(targets)]
    while frontier:
        batch, frontier = frontier[:40], frontier[40:]
        ids = [q for q, _ in batch if q not in seen]
        if not ids:
            continue
        cent = _entities(client, ids, props="labels|claims")
        edge_targets = [t for q in ids for p, t in web._entity_targets(cent.get(q, {})) if p == "subclass_of"]
        clab = wikidata_labels(client, list(dict.fromkeys(ids + edge_targets)))
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
        summ = wikipedia_summary(client, title_of[q])
        text = (summ.get("extract", "") if summ else "")[:summary_chars]
        docs.append(web.Doc(name=title_of[q], slug=web.slug(title_of[q]),
                            sentences=web.split_sentences(text), facts=facts, labels=labels))
    return docs, hierarchy


def sample_indices(pool: Sequence, k: int, *, seed: int) -> List[int]:
    """Deterministic index sample (used to grow the corpus across rounds)."""
    idx = list(range(len(pool)))
    Random(seed).shuffle(idx)
    return sorted(idx[: max(0, min(int(k), len(idx)))])