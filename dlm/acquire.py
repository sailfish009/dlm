"""DLM v0.0054 -- the acquisition subject (untrusted).

A deductive model cannot derive what is not in its facts: the meaning of a
library symbol, what a dataset contains, what an API call does.  The model fills
that gap by SEARCHING, reducing the evidence it finds to a fact with provenance,
and re-running -- the search-driven half of the learning loop.  This module is
that subject, and it is part of the MODEL.

It is generic: it names no library and no dataset.  A caller supplies a
:class:`SymbolVocabulary` / :class:`EntityVocabulary` (the cue lexicons and the
reduction hints -- the *given* vocabulary), and the subject does the rest:

    candidates -> web search -> reduce evidence -> fact(+provenance) -> cache

Nothing here is trusted: the kernel consumes ``meaning`` / ``dataset_of`` like
any other fact and re-checks everything it concludes.  A candidate whose evidence
yields no cue produces NO fact -- the subject abstains, so replay stays
deterministic and no meaning is invented.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from .search import (Cues, extract_definition, reduce_text, resolve_object,
                     sphinx_inventory, stackexchange_question,
                     stackexchange_titles, wikipedia_search_titles,
                     wikipedia_summary)
from .web import Web

__all__ = [
    "SymbolVocabulary", "EntityVocabulary",
    "symbol_candidates", "dataset_candidates",
    "acquire_symbol_meanings", "acquire_domain_entities",
    "meaning_facts", "domain_facts",
]


@dataclass(frozen=True)
class SymbolVocabulary:
    """The GIVEN cues that reduce a symbol's documentation to a concept."""
    concept_cues: Cues = ()
    search_cues: Cues = ()
    receiver_hints: Mapping[str, str] = field(default_factory=dict)
    inventory_url: str = ""
    docs_base: str = ""
    inventory_prefixes: Tuple[str, ...] = ("torch.",)
    search_site: str = "stackoverflow"
    search_prefix: str = ""
    record_name: str = "symbol_knowledge.json"


@dataclass(frozen=True)
class EntityVocabulary:
    """The GIVEN cues that reduce a dataset's prose to the entity it records."""
    entity_cues: Cues = ()
    dataset_hints: Tuple[str, ...] = ()
    dataset_word: str = "dataset"
    entity_phrases: Mapping[str, str] = field(default_factory=dict)
    search_site: str = "stackoverflow"
    search_prefix: str = "pytorch"
    record_name: str = "domain_knowledge.json"


# ---------------------------------------------------------------------------
# candidate selection: what to ASK (a reduction, never knowledge)
# ---------------------------------------------------------------------------
def symbol_candidates(facts: List[tuple], labels: Dict[str, str]) -> Dict[str, str]:
    """External, library-looking slugs the reduction uses, mapped to their label.

    "Library-looking" = a dotted name (``nn.Linear``) or a capitalised class
    (``DataLoader``).  Purely local names and names defined in the file are
    dropped; synthetic step slugs (``a__b``) are dropped.  This only says *what
    to ask*.
    """
    defined = {f[2] for f in facts if f[0] in ("defines", "method_of")}
    out: Dict[str, str] = {}
    for f in facts:
        if f[0] in ("creates", "calls", "inherits"):
            args = (f[2],)
        else:
            continue
        for s in args:
            if s in defined or "__" in s:
                continue
            label = labels.get(s)
            if not label:
                continue
            if "." not in label and not label[:1].isupper():
                continue
            out.setdefault(s, label)
    return out


def dataset_candidates(facts: List[tuple], labels: Dict[str, str],
                       hints: Sequence[str] = (),
                       word: str = "dataset") -> Dict[str, str]:
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
        if word in low or any(h in low for h in hints):
            out.setdefault(slug, label)
    return out


# ---------------------------------------------------------------------------
# record-cache helpers (reduced records, beside the raw fetch cache)
# ---------------------------------------------------------------------------
def _load_records(path: str, version: int, key: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                db = json.load(fh)
        except ValueError:
            db = {}
        if db.get("version") == version:
            return db
    return {"version": version, key: {}}


def _save_records(path: str, db: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(db, fh, indent=1, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------
# acquisition 1: symbol -> meaning concept (documentation + search)
# ---------------------------------------------------------------------------
def acquire_symbol_meanings(candidates: Dict[str, str], labels: Dict[str, str],
                            cache_dir: str, vocab: SymbolVocabulary, *,
                            version: int = 1, offline: bool = False,
                            search: bool = True,
                            max_new: Optional[int] = None) -> dict:
    """Acquire ``meaning(symbol, concept)`` for the library symbols in play.

    Uses the documentation inventory (authoritative) and, optionally, a web
    search for corroboration.  Reads/writes the vocabulary's record file (e.g.
    ``<cache_dir>/pytorch_knowledge.json``) and the raw fetch cache under
    ``<cache_dir>/fetch/``.
    """
    path = os.path.join(cache_dir, vocab.record_name)
    db = _load_records(path, version, "symbols")
    syms: Dict[str, dict] = db.setdefault("symbols", {})
    web = Web(cache_dir, offline=offline)
    inventory: Optional[Dict[str, str]] = None
    fetched_new = 0
    changed = False

    for slug, label in sorted(candidates.items()):
        if syms.get(label) is not None:
            continue
        if offline:
            continue
        if max_new is not None and fetched_new >= max_new:
            continue
        if inventory is None:
            inventory = sphinx_inventory(web, vocab.inventory_url,
                                         vocab.inventory_prefixes)
        entry, how = resolve_object(label, inventory, vocab.receiver_hints)
        rec = {"label": label, "slug": slug, "entry": entry, "resolution": how,
               "definition": None, "concept": None, "url": None, "providers": []}
        if entry:
            url = vocab.docs_base + inventory[entry]
            rec["url"] = url
            page = web.get_text(url)
            if page:
                defn = extract_definition(page, entry)
                rec["definition"] = defn
                rec["concept"] = reduce_text(defn, vocab.concept_cues) if defn else None
            rec["providers"].append("docs")
        if search:
            ev = stackexchange_question(web, label, vocab.search_prefix,
                                        vocab.search_site)
            if ev:
                rec["providers"].append("search")
                rec["search"] = ev
                if rec["concept"] is None:
                    rec["concept"] = reduce_text(ev["title"], vocab.search_cues)
        syms[label] = rec
        fetched_new += 1
        changed = True

    if changed:
        _save_records(path, db)

    meanings = {slug: syms[label]["concept"]
                for slug, label in candidates.items()
                if syms.get(label, {}).get("concept")}
    records = sorted((syms[label] for label in set(candidates.values()) if label in syms),
                     key=lambda r: r["label"])
    return {"meanings": meanings, "records": records,
            "stats": {"candidates": len(candidates), "acquired": len(meanings),
                      "cached_records": len(syms), "fetched_new": fetched_new,
                      "offline": offline, "inventory_url": vocab.inventory_url}}


# ---------------------------------------------------------------------------
# acquisition 2: dataset -> entity (Wikipedia primary, search fallback)
# ---------------------------------------------------------------------------
def acquire_domain_entities(candidates: Dict[str, str], cache_dir: str,
                            vocab: EntityVocabulary, *, version: int = 1,
                            offline: bool = False, search: bool = True) -> dict:
    """Search for what each dataset candidate contains; cache reduced records.

    ``offline`` reads only cached records (no network); a candidate with no
    cached record yields no fact (abstain).
    """
    path = os.path.join(cache_dir, vocab.record_name)
    db = _load_records(path, version, "datasets")
    ds: Dict[str, dict] = db.setdefault("datasets", {})
    web = Web(cache_dir, offline=offline)
    fetched_new = 0
    changed = False

    for slug, label in sorted(candidates.items()):
        if ds.get(slug, {}).get("v") == version:
            continue
        if offline or not search:
            continue
        evidence: List[str] = []
        providers: List[str] = []

        entity, summ, wev = _wikipedia_lookup(web, label, vocab)
        evidence.extend(wev)
        if summ:
            providers.append("wikipedia")

        se_entity, se_titles = _search_lookup(web, label, vocab)
        if se_titles:
            providers.append("search")
            evidence.extend("search: " + t for t in se_titles[:3])

        # Wikipedia decides; web search only corroborates or fills the gap.
        final = entity or se_entity
        ds[slug] = {"slug": slug, "label": label, "v": version, "entity": final,
                    "providers": providers,
                    "wikipedia": ({"title": summ["title"], "url": summ["url"],
                                   "entity": entity} if summ else None),
                    "search": {"titles": se_titles[:5], "entity": se_entity},
                    "evidence": evidence}
        fetched_new += 1
        changed = True

    if changed:
        _save_records(path, db)

    entities = {slug: rec["entity"] for slug, rec in ds.items() if rec.get("entity")}
    records = sorted(ds.values(), key=lambda r: r["slug"])
    return {"entities": entities, "records": records,
            "stats": {"candidates": len(candidates), "acquired": len(entities),
                      "cached_records": len(ds), "fetched_new": fetched_new,
                      "offline": offline}}


def _wikipedia_lookup(web: Web, label: str, vocab: EntityVocabulary
                      ) -> Tuple[Optional[str], Optional[dict], List[str]]:
    evidence: List[str] = []
    titles = [label]
    for t in wikipedia_search_titles(web, f"{label} {vocab.dataset_word}"):
        if t.lower() != label.lower():
            titles.append(t)
    for title in titles:
        summ = wikipedia_summary(web, title)
        if not summ:
            continue
        snippet = " ".join(summ["extract"].split())[:240]
        evidence.append(f"wikipedia:{summ['title']}: {snippet}")
        entity = reduce_text(summ["extract"], vocab.entity_cues)
        if entity:
            return entity, summ, evidence
    return None, None, evidence


def _search_lookup(web: Web, label: str, vocab: EntityVocabulary
                   ) -> Tuple[Optional[str], List[str]]:
    titles = stackexchange_titles(web, f"{vocab.search_prefix} {label} "
                                       f"{vocab.dataset_word}", vocab.search_site)
    for title in titles:
        entity = reduce_text(title, vocab.entity_cues)
        if entity:
            return entity, titles
    return None, titles


# ---------------------------------------------------------------------------
# facts
# ---------------------------------------------------------------------------
def meaning_facts(meanings: Mapping[str, str]) -> List[Tuple[str, str, str]]:
    """``{slug: concept}`` -> ground fact tuples ``("meaning", slug, concept)``."""
    return [("meaning", slug, concept) for slug, concept in sorted(meanings.items())]


def domain_facts(entities: Mapping[str, str]) -> List[Tuple[str, str, str]]:
    """``{slug: entity}`` -> ``dataset_of`` ground fact tuples."""
    return [("dataset_of", slug, entity) for slug, entity in sorted(entities.items())]