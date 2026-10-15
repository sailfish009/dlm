"""Experiments/reading -- the LEVELED final natural-language reading (offline).

The north-star path ended with a flat fact list plus one core-concept sentence.
This stage runs LAST and emits a *leveled reading* of the program: every sentence
is tagged with its abstraction level (N1..N8) and carries the kernel atoms that
entail it.  It exists to make one question measurable:

    at what sentence level does the final output actually speak?

v0.0047 realises N1..N8:
    N1 facts, N2 meanings, N3 idioms, N4 a NAMED gradient step,
    N5 the forward-pass architecture, N6 a certified "why" (from acquired
    ``api_effect`` facts + observed direct calls), N7 the purpose/gist (from the
    derived ``recognizes`` concept, which needs SEARCHED domain knowledge),
    N8 a structural analogy (two routines with certified shared calls but
    divergent regime).

The honesty test is built in: strip the acquired domain facts and the N7 gist
must disappear (the reader abstains), while everything the structure supports
stays.  Nothing is printed that the kernel closure does not entail.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from dlm import KnowledgeBase, closure
from dlm.gist import external_holes, gist_rules
from dlm.ground import Ground, learn
from dlm.lisp import form_to_rule
from dlm.narrative import LEVELS, reading, reading_level, reading_score

try:
    from ..mnist.api_semantics import api_effect_facts, direct_explains
    from ..mnist.domain import (ENTITY_PHRASES, acquire_domain, dataset_candidates,
                                domain_facts)
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import (STRUCTURAL, STRUCT_GROUND, atom_of, negatives,
                             transitive)
    from ..mnist.semantics import bridge_forms
except ImportError:  # direct `python experiments/reading/run.py`
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mnist.api_semantics import api_effect_facts, direct_explains
    from mnist.domain import (ENTITY_PHRASES, acquire_domain, dataset_candidates,
                              domain_facts)
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import STRUCTURAL, STRUCT_GROUND, atom_of, negatives, transitive
    from mnist.semantics import bridge_forms

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "mnist", "cache")
NORTH_STAR_SRC = os.path.join(CACHE, "main.py")


def _closed(base: set) -> set:
    """Induce the structural ``calls`` law, apply the given bridges + gist rules, close."""
    calls = {a for a in base if a.pred == "calls"}
    positives = transitive(calls)
    universe = sorted({t.name for a in calls for t in a.args})
    negs = negatives(positives, universe)
    struct = {a for a in base if a.pred in STRUCTURAL}
    res = learn(STRUCT_GROUND, struct, positives, negs,
                max_body=2, extra_vars=2, max_rules=4)
    kb = KnowledgeBase(base)
    for f in bridge_forms():
        kb.add_rule(form_to_rule(f))
    for r in gist_rules():
        kb.add_rule(r)
    for r in res.experience.rules:
        kb.add_rule(r)
    return closure(kb)


def _causal_atoms(base: set) -> set:
    """Acquired ``api_effect`` facts + ``explains`` for DIRECT calls only."""
    direct = [(a.args[0].name, a.args[1].name) for a in base if a.pred == "calls"]
    atoms = {atom_of(f) for f in api_effect_facts()}
    atoms |= {atom_of(f) for f in direct_explains(direct)}
    return atoms


def run(src: str, module: str = "main", cache_dir: str = CACHE,
        offline: bool = True, knowledge: dict = None, domain: dict = None) -> dict:
    ext = extract(src, module)
    labels, pipelines = ext["labels"], ext["pipelines"]
    facts = [tuple(f) for f in ext["facts"]]
    if knowledge is None:
        knowledge = acquire_knowledge(ext["facts"], labels, cache_dir=cache_dir,
                                      offline=offline)
    meanings = knowledge["meanings"]

    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(meanings)}
    causal = _causal_atoms(base)

    # SEARCH for the one thing no reading of the code can supply: what the
    # instantiated dataset contains (the ``recognizes`` premise).
    cands = dataset_candidates(facts, labels)
    holes = external_holes(facts, cands)
    if domain is None:
        domain = acquire_domain({h: cands[h] for h in holes}, cache_dir=cache_dir,
                                offline=offline)
    entities = domain.get("entities", {}) if isinstance(domain, dict) else dict(domain)
    dfacts = [atom_of(f) for f in domain_facts(entities)]

    closed = _closed(base | set(dfacts)) | causal
    sentences = reading(closed, labels, pipelines, module=module, meanings=meanings,
                        entity_phrases=ENTITY_PHRASES)

    # HONESTY ABLATION: without the searched domain knowledge -> no gist.
    closed_ctrl = _closed(base) | causal
    sents_ctrl = reading(closed_ctrl, labels, pipelines, module=module,
                         meanings=meanings, entity_phrases=ENTITY_PHRASES)
    abstains_without_domain = not any(s["level"] == 7 and "recognize" in s["text"]
                                      for s in sents_ctrl)

    level = reading_level(sentences)
    score = reading_score(sentences)
    produced = {f"N{n}_{name}": any(s["level"] == n and s["certified"] for s in sentences)
                for n, name in LEVELS.items()}
    verdict = {
        "all_sentences_certified": all(s["certified"] for s in sentences) and bool(sentences),
        "named_composition_step": produced["N4_composition"],
        "architecture_topology": produced["N5_architecture"],
        "causal_why": produced["N6_causal"],
        "purpose_gist": produced["N7_purpose"],
        "analogy_sentence": produced["N8_analogy"],
        "abstains_without_domain": abstains_without_domain,
        "reading_level_at_least_7": level >= 7,
        "reading_level_at_least_8": level >= 8,
        "reading_score_at_least_half": score >= 0.5,
    }
    return {
        "source": module,
        "counts": {"facts": len(base), "derived_atoms": len(closed)},
        "domain": {"entities": entities, "stats": domain.get("stats", {})},
        "reading_level": level,
        "reading_level_name": LEVELS.get(level, "none"),
        "reading_score": score,
        "levels_present": produced,
        "sentences": sentences,
        "all_sentences_certified": verdict["all_sentences_certified"],
        "ablation_without_domain": [s["text"] for s in sents_ctrl if s["level"] == 7],
        "verdict": verdict,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="leveled final NL reading of a program")
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "reading"))
    args, _unknown = ap.parse_known_args(argv)

    src_path = args.local or NORTH_STAR_SRC
    src = open(src_path, "r", encoding="utf-8").read()
    result = run(src, cache_dir=args.cache, offline=args.offline)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"facts   : {result['counts']['facts']} base, {result['counts']['derived_atoms']} derived")
    print(f"domain  : {result['domain']['entities']}  {result['domain']['stats']}")
    print(f"reading : level N{result['reading_level']} ({result['reading_level_name']})  "
          f"score {result['reading_score']}")
    print("--- leveled reading (each line backed by kernel facts) ---")
    for s in result["sentences"]:
        mark = "ok " if s["certified"] else "?? "
        print(f"  {mark}N{s['level']} {s['kind']:<12} {s['text']}")
    print(f"ablation (no domain knowledge): N7 = {result['ablation_without_domain']}")
    print(f"levels : {result['levels_present']}")
    print(f"verdict: {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())