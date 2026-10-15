"""DLM v0.0054 -- webssl experiment glue (wiki entity -> Horn facts).

The web *access* and the *providers* now live in the model (:mod:`dlm.web`,
:mod:`dlm.search`); the subject that reaches the web is the model, not this
experiment.  What remains here is experiment-specific SHAPING only:

* the GIVEN property map (``P31`` -> ``instance_of`` ...) and seed-name list;
* slug/sentence reduction for the single-token DLM fragment;
* turning Wikidata claims into the experiment's ``Fact``/``Doc`` records.

No transport, no cache, no provider logic lives here any more.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from dlm.search import (wikidata_entities, wikidata_labels, wikidata_search,
                        wikipedia_summary)
from dlm.web import Web

# Re-exported so ``experiments/web/acquire.py`` can keep using the same names.
__all__ = ["UA", "Web", "WIKIDATA", "WIKI_SUMMARY", "PROP_PRED", "DEFAULT_SEEDS",
           "slug", "split_sentences", "Fact", "Doc", "_entity_targets", "extract"]

UA = {"User-Agent": "dlm-research/0.1 (+https://github.com/sailfish009/dlm)"}
WIKIDATA = "https://www.wikidata.org/w/api.php"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"

PROP_PRED: Dict[str, str] = {
    "P31": "instance_of",
    "P279": "subclass_of",
    "P106": "occupation",
    "P19": "birthplace",
    "P27": "country",
    "P17": "country_of",
    "P159": "located_in",
    "P361": "part_of",
}

# Real entities across a few domains so the hierarchy is not one trivial chain.
DEFAULT_SEEDS: Tuple[str, ...] = (
    "Alan Turing", "Marie Curie", "Albert Einstein", "Ada Lovelace", "Isaac Newton",
    "Leonardo da Vinci", "Vincent van Gogh", "Wolfgang Amadeus Mozart", "Charles Darwin",
    "Nikola Tesla", "Galileo Galilei", "Stephen Hawking", "Rosalind Franklin",
    "Pablo Picasso", "Frida Kahlo", "Jane Austen", "William Shakespeare", "Isaac Asimov",
    "Paris", "Tokyo", "Berlin", "London", "Rome", "Vienna",
)


def slug(text: str) -> str:
    """Single-token canonical constant (spaces/punctuation -> underscore)."""
    out = re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower())
    return out.strip("_") or "unknown"


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [p.strip() for p in parts if len(p.strip()) >= 12]


@dataclass(frozen=True)
class Fact:
    pred: str
    subj: str
    obj: str

    def sexp(self) -> str:
        return f"({self.pred} {self.subj} {self.obj})"

    def key(self) -> str:
        return self.sexp()


@dataclass
class Doc:
    name: str
    slug: str
    sentences: List[str] = field(default_factory=list)
    facts: List[Fact] = field(default_factory=list)     # about this entity
    labels: Dict[str, str] = field(default_factory=dict)  # slug -> surface label


def _entity_targets(ent: dict) -> List[Tuple[str, str]]:
    """-> [(pred, target_qid)] for the supported properties of one entity."""
    out: List[Tuple[str, str]] = []
    for pid, pred in PROP_PRED.items():
        for claim in (ent.get("claims", {}) or {}).get(pid, []) or []:
            dv = (claim.get("mainsnak", {}) or {}).get("datavalue", {}) or {}
            if dv.get("type") == "wikibase-entityid":
                out.append((pred, dv["value"]["id"]))
    return out


def extract(names: Sequence[str] = DEFAULT_SEEDS, *, cache_dir: str, offline: bool = False,
            subclass_depth: int = 3, summary_chars: int = 900) -> Tuple[List[Doc], List[Fact]]:
    """Seed entity names -> (docs, class_hierarchy_facts).  No human labels.

    All network/caching is delegated to the model: ``dlm.web.Web`` fetches and
    caches, ``dlm.search.wikidata_*`` reduce the responses.  ``offline`` replays
    the byte cache; an unreachable source abstains (no fact, no invention).
    """
    web = Web(cache_dir, offline=offline)

    # 1. names -> qids
    qid_of: Dict[str, str] = {}
    label_of: Dict[str, str] = {}
    for name in names:
        found = wikidata_search(web, name)
        if found:
            qid_of[name], label_of[name] = found
        else:
            qid_of[name], label_of[name] = slug(name), name

    # 2. entity claims
    ents = wikidata_entities(web, list(qid_of.values())) if any(
        q.startswith("Q") for q in qid_of.values()) else {}
    raw: Dict[str, List[Tuple[str, str]]] = {}
    targets: List[str] = []
    for name, q in qid_of.items():
        raw[name] = _entity_targets(ents.get(q, {}))
        targets += [t for _, t in raw[name]]

    # 3. labels for every target, then slug + human label
    tlab = wikidata_labels(web, targets)

    def obj_of(q: str) -> Tuple[str, str]:
        human = tlab.get(q, q) or q
        return slug(human), human

    # 4. class hierarchy: BFS over P279 from target classes
    hierarchy: List[Fact] = []
    seen: set = set()
    frontier = [(t, 0) for t in dict.fromkeys(targets)]
    while frontier:
        batch = frontier[:40]
        frontier = frontier[40:]
        ids = [q for q, _ in batch if q not in seen]
        if not ids:
            continue
        cent = wikidata_entities(web, ids, props="labels|claims")
        # Resolve labels for BOTH sides of every subclass edge, otherwise the
        # object of a chain stays a raw QID and no transitive rule can fire.
        edge_targets: List[str] = []
        for q in ids:
            for pred, tgt in _entity_targets(cent.get(q, {})):
                if pred == "subclass_of":
                    edge_targets.append(tgt)
        clab = wikidata_labels(web, list(dict.fromkeys(ids + edge_targets)))
        deeper: List[Tuple[str, int]] = []
        for q, depth in batch:
            if q in seen:
                continue
            seen.add(q)
            for pred, tgt in _entity_targets(cent.get(q, {})):
                if pred == "subclass_of":
                    hierarchy.append(Fact("subclass_of", slug(clab.get(q, q)), slug(clab.get(tgt, tgt))))
                    if depth < subclass_depth:
                        deeper.append((tgt, depth + 1))
        frontier += deeper

    # 5. per-entity docs
    docs: List[Doc] = []
    for name in names:
        q = qid_of[name]
        ent = ents.get(q, {})
        labels: Dict[str, str] = {}
        facts: List[Fact] = []
        for pred, tgt in raw.get(name, []):
            if pred == "subclass_of":
                continue  # a seed is an instance here; class hierarchy handled above
            oslug, human = obj_of(tgt)
            labels[oslug] = human
            facts.append(Fact(pred, slug(name), oslug))
        title = ((ent.get("sitelinks", {}) or {}).get("enwiki", {}) or {}).get("title") or name
        summ = wikipedia_summary(web, title)
        text = (summ.get("extract", "") if summ else "")[:summary_chars]
        docs.append(Doc(name=name, slug=slug(name), sentences=split_sentences(text),
                        facts=facts, labels=labels))
    return docs, hierarchy