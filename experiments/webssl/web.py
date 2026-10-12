"""Web knowledge extraction for the webssl experiment (NOTE.md §43).

Turns the live web into candidate logic, with no human labels:

* **Wikidata** (`wbsearchentities` / `wbgetentities`) -> function-free binary
  triples ``(pred subj obj)``: instance_of, subclass_of, occupation, birthplace,
  country, country_of, located_in, part_of.  Every label is slugified to a single
  token because the DLM fragment has single-token constants only (NOTE §39.4).
* **Wikipedia REST summary** -> the entity's prose, split into sentences.  Those
  sentences are the natural-language surface used for distant supervision (an
  atom whose object label appears in the sentence is the weak positive).

Everything is cached under ``cache/`` so the experiment is reproducible offline
(``offline=True`` never touches the network).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse as up
import urllib.request as ur
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

UA = {"User-Agent": "dlm-research/0.1 (research; +https://github.com/sailfish009/dlm)"}
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


class WebCache:
    def __init__(self, cache_dir: str, offline: bool = False) -> None:
        self.dir = cache_dir
        self.offline = offline
        os.makedirs(cache_dir, exist_ok=True)
        self._mem: Dict[str, object] = {}

    def _path(self, key: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", key)
        if len(safe) > 120:  # long query strings (batch entity ids) -> stable digest name
            digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
            safe = safe[:80] + "_" + digest
        return os.path.join(self.dir, safe + ".json")

    def get(self, key: str, producer):
        if key in self._mem:
            return self._mem[key]
        path = self._path(key)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self._mem[key] = json.load(fh)
            return self._mem[key]
        if self.offline:
            raise FileNotFoundError(f"offline: cache miss for {key!r} ({path})")
        value = producer()
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(value, fh, ensure_ascii=False)
        self._mem[key] = value
        return value


def _urlopen(url: str, timeout: float = 25.0):
    return ur.urlopen(ur.Request(url, headers=UA), timeout=timeout)


class Wikidata:
    def __init__(self, cache: WebCache, pause: float = 0.1) -> None:
        self.cache = cache
        self.pause = pause

    def _api(self, params: dict) -> dict:
        params = {**params, "format": "json"}

        def produce():
            time.sleep(self.pause)
            with _urlopen(WIKIDATA + "?" + up.urlencode(params)) as r:
                return json.load(r)

        return self.cache.get("wd_" + up.urlencode(sorted(params.items())), produce)

    def search(self, name: str) -> Optional[Tuple[str, str]]:
        d = self._api({"action": "wbsearchentities", "search": name, "language": "en", "limit": 1})
        hits = d.get("search") or []
        if not hits:
            return None
        return hits[0]["id"], hits[0].get("label") or name

    def entities(self, ids: Sequence[str], props: str = "labels|claims|sitelinks") -> Dict[str, dict]:
        out: Dict[str, dict] = {}
        ids = [i for i in dict.fromkeys(ids) if i]
        for i in range(0, len(ids), 40):
            chunk = ids[i:i + 40]
            d = self._api({"action": "wbgetentities", "ids": "|".join(chunk), "props": props,
                           "languages": "en", "sitefilter": "enwiki"})
            out.update(d.get("entities", {}))
        return out

    def labels(self, ids: Sequence[str]) -> Dict[str, str]:
        ent = self.entities(ids, props="labels")
        return {q: (e.get("labels", {}).get("en", {}) or {}).get("value", q) for q, e in ent.items()}

    def summary(self, title: str) -> str:
        def produce():
            with _urlopen(WIKI_SUMMARY + up.quote(title.replace(" ", "_"))) as r:
                return json.load(r)
        d = self.cache.get("wiki_" + title, produce)
        return d.get("extract", "") or ""


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
    """Seed entity names -> (docs, class_hierarchy_facts).  No human labels."""
    cache = WebCache(cache_dir, offline=offline)
    wd = Wikidata(cache)

    # 1. names -> qids
    qid_of: Dict[str, str] = {}
    label_of: Dict[str, str] = {}
    for name in names:
        try:
            found = wd.search(name)
        except FileNotFoundError:
            found = None
        if found:
            qid_of[name], label_of[name] = found[0], found[1]
        else:
            qid_of[name], label_of[name] = slug(name), name

    # 2. entity claims
    ents = wd.entities(list(qid_of.values())) if any(q.startswith("Q") for q in qid_of.values()) else {}
    raw: Dict[str, List[Tuple[str, str]]] = {}
    targets: List[str] = []
    for name, q in qid_of.items():
        raw[name] = _entity_targets(ents.get(q, {}))
        targets += [t for _, t in raw[name]]

    # 3. labels for every target, then slug + human label
    tlab = wd.labels(targets)
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
        cent = wd.entities(ids, props="labels|claims")
        # Resolve labels for BOTH sides of every subclass edge, otherwise the
        # object of a chain stays a raw QID and no transitive rule can fire.
        edge_targets: List[str] = []
        for q in ids:
            for pred, tgt in _entity_targets(cent.get(q, {})):
                if pred == "subclass_of":
                    edge_targets.append(tgt)
        clab = wd.labels(list(dict.fromkeys(ids + edge_targets)))
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
        text = wd.summary(title)[:summary_chars]
        docs.append(Doc(name=name, slug=slug(name), sentences=split_sentences(text),
                        facts=facts, labels=labels))
    return docs, hierarchy