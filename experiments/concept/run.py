"""Experiments/concept -- from concrete facts to a CORE CONCEPT, searching the gaps.

This is the loop the north star was missing.  The v0.0042 pipeline *listed* facts
(imports, has_layer, backpropagates, ...).  It never said **what the program is**.
Here the reader:

  ROUND 1  reduce -> acquire meanings -> learn the call law -> close -> gist attempt
           (the gist layer reports the holes it cannot fill: what does `datasets.MNIST`
            CONTAIN?  it is a question, not a fact)
  SEARCH   look the hole up on a web search service, reduce the hits to
           ``dataset_of(MNIST, handwritten_digit)``, cache it with provenance
  ROUND 2  re-learn + re-close on the ENLARGED knowledge base, and now the kernel
           derives the core concept ``recognizes(main, handwritten_digit)``

Every concept is a kernel atom with a verified proof; with the acquired domain
knowledge stripped the concept is NOT derivable -- the reader abstains.  That
ablation is the honesty test: the concept really came from the searched knowledge,
not from a hard-coded rule.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from dlm import Atom, Const, KnowledgeBase, closure
from dlm.gist import (GIST_GOALS, build_gist_kb, concept_atoms, concept_str,
                      external_holes, strongest_concept)
from dlm.ground import Ground, learn
from dlm.lisp import form_to_rule
from dlm.proof import proof_ir, proof_size, prove, verify

try:
    from ..mnist.domain import (ENTITY_PHRASES, acquire_domain, dataset_candidates,
                                domain_facts)
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import (STRUCTURAL, STRUCT_GROUND, atom_of, negatives,
                             transitive)
    from ..mnist.semantics import bridge_forms
except ImportError:  # direct `python experiments/concept/run.py`
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mnist.domain import (ENTITY_PHRASES, acquire_domain, dataset_candidates,
                              domain_facts)
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import STRUCTURAL, STRUCT_GROUND, atom_of, negatives, transitive
    from mnist.semantics import bridge_forms

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "mnist", "cache")
NORTH_STAR_SRC = os.path.join(CACHE, "main.py")


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _understanding_kb(base_facts):
    kb = build_gist_kb(base_facts)
    for f in bridge_forms():
        kb.add_rule(form_to_rule(f))
    return kb


def _learn_and_close(base):
    """Induce the structural ``calls`` law, then close understanding + gist."""
    calls = {a for a in base if a.pred == "calls"}
    positives = transitive(calls)
    universe = sorted({t.name for a in calls for t in a.args})
    negs = negatives(positives, universe)
    struct = {a for a in base if a.pred in STRUCTURAL}
    res = learn(STRUCT_GROUND, struct, positives, negs,
                max_body=2, extra_vars=2, max_rules=4)
    kb = _understanding_kb(base)
    for r in res.experience.rules:
        kb.add_rule(r)
    closed = closure(kb)
    return res, kb, closed, positives


def _gist_sentences(closed, module: str, entities: dict, labels: dict) -> list:
    """Gloss the derived concepts; each sentence cites the atom that entails it."""
    out = []
    for a in concept_atoms(closed):
        if a.pred == "recognizes":
            entity = a.args[1].name
            ds = sorted(d for d, e in entities.items() if e == entity)
            dlabel = labels.get(ds[0], ds[0]) if ds else "an image dataset"
            phrase = ENTITY_PHRASES.get(entity, entity)
            out.append({
                "pred": "recognizes", "level": "core",
                "text": _cap(f"{module} is a program that trains a neural-network model "
                             f"to recognize {phrase} (from the {dlabel} dataset)."),
                "support": [concept_str(a)]})
        elif a.pred == "trains_model":
            out.append({"pred": "trains_model", "level": "supporting",
                        "text": _cap(f"{module} trains a neural-network model."),
                        "support": [concept_str(a)]})
        elif a.pred == "is_supervised":
            out.append({"pred": "is_supervised", "level": "supporting",
                        "text": _cap(f"{module} is trained with supervised learning "
                                     f"(backpropagation + parameter updates)."),
                        "support": [concept_str(a)]})
    return out


def run(src: str, source: str = "cache/main.py", module: str = "main",
        cache_dir: str = CACHE, offline: bool = True, search: bool = True,
        knowledge: dict = None, domain: dict = None) -> dict:
    ext = extract(src, module)
    labels = ext["labels"]
    facts = [tuple(f) for f in ext["facts"]]
    cands = dataset_candidates(facts, labels)

    if knowledge is None:
        knowledge = acquire_knowledge(ext["facts"], labels, cache_dir=cache_dir,
                                      offline=offline)
    meanings = knowledge["meanings"]

    base = {atom_of(f) for f in facts}
    base |= {atom_of(f) for f in meaning_facts(meanings)}

    # ---- ROUND 1: reduce, learn, close, attempt the concept ----------------
    res1, _kb1, closed1, positives = _learn_and_close(base)
    concepts1 = concept_atoms(closed1)
    holes = external_holes(facts, cands)
    rounds = [{"round": 1, "action": "reduce+acquire-meaning+learn+close",
               "facts": len(base), "learned_rules": len(res1.experience.rules),
               "concepts": [concept_str(a) for a in concepts1],
               "gaps": list(holes)}]

    # ---- SEARCH: fill each hole with acquired domain knowledge -------------
    if domain is None:
        domain = acquire_domain({h: cands[h] for h in holes}, cache_dir=cache_dir,
                                offline=offline, search=search)
    entities = domain.get("entities", {}) if isinstance(domain, dict) else dict(domain)
    dfacts = domain_facts(entities)
    base |= {atom_of(f) for f in dfacts}

    # ---- ROUND 2: RE-LEARN + re-close on the enlarged knowledge base -------
    res2, kb2, closed2, _ = _learn_and_close(base)
    concepts2 = concept_atoms(closed2)
    strongest = strongest_concept(closed2)
    rounds.append({"round": 2, "action": "relearn+reclose (knowledge grew)",
                   "facts": len(base), "learned_rules": len(res2.experience.rules),
                   "acquired": [list(f) for f in dfacts],
                   "concepts": [concept_str(a) for a in concepts2]})

    # ---- ABLATION: strip the acquired domain knowledge -> must abstain -----
    base_ctrl = {a for a in base if a.pred not in ("dataset_of", "task_of")}
    _, _kb_c, closed_ctrl, _ = _learn_and_close(base_ctrl)
    ctrl_concepts = concept_atoms(closed_ctrl)
    abstains_without_knowledge = all(a.pred != "recognizes" for a in ctrl_concepts)

    sentences = _gist_sentences(closed2, module, entities, labels)

    proof = None
    if strongest is not None and strongest.pred == "recognizes":
        p = prove(kb2, strongest)
        if p is not None:
            from dlm.lisp import dump
            proof = {"atom": concept_str(strongest), "size": proof_size(p),
                     "verified": verify(p, kb2), "ir": dump(proof_ir(p))}

    # a few concrete facts, for the "list facts first" phase
    sample = []
    for f in sorted(facts):
        if f[0] in ("defines", "inherits", "creates") or (f[0] == "imports" and f[1] == module):
            sample.append("(" + " ".join(f) + ")")

    produced = {
        "lists_concrete_facts": len(facts) >= 40,
        "detects_unknown_gap": len(holes) > 0,
        "searches_for_knowledge": len(entities) > 0,
        "relearns_after_acquiring": len(rounds) == 2 and len(dfacts) > 0,
        "captures_core_concept": strongest is not None and strongest.pred == "recognizes",
        "core_concept_certified": bool(proof and proof["verified"]),
        "abstains_without_acquired_knowledge": abstains_without_knowledge,
    }
    score = round(sum(1 for v in produced.values() if v) / len(produced), 3)

    verdict = {
        "concrete_facts_reduced": len(facts) >= 40,
        "gap_detected": len(holes) > 0,
        "domain_knowledge_acquired": len(entities) > 0,
        "relearn_after_acquisition": len(rounds) == 2,
        "core_concept_captured": produced["captures_core_concept"],
        "core_concept_certified": produced["core_concept_certified"],
        "abstains_without_knowledge": abstains_without_knowledge,
        "concept_score_above_half": score >= 0.5,
    }

    return {
        "source": source,
        "module": module,
        "facts": {"count": len(facts), "sample": sample[:24]},
        "knowledge": {"stats": knowledge["stats"], "meanings": meanings},
        "domain": {"entities": entities,
                   "records": [{"slug": r["slug"], "label": r["label"],
                                "entity": r["entity"], "evidence": r.get("evidence", [])}
                               for r in domain.get("records", [])],
                   "stats": domain.get("stats", {})},
        "rounds": rounds,
        "concepts": [concept_str(a) for a in concepts2],
        "core_concept": concept_str(strongest) if strongest else None,
        "sentences": sentences,
        "all_sentences_certified": all(
            all(tok in {concept_str(a) for a in closed2} for tok in s["support"])
            for s in sentences),
        "proof": proof,
        "ablation_without_knowledge": [concept_str(a) for a in ctrl_concepts],
        "concept_score": {"produced": produced, "score": score},
        "verdict": verdict,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="core-concept (gist) capture + search loop")
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--no-search", action="store_true",
                    help="do not search for domain knowledge (abstain on the gap)")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "concept"))
    args, _unknown = ap.parse_known_args(argv)

    src_path = args.local or NORTH_STAR_SRC
    src = open(src_path, "r", encoding="utf-8").read()
    result = run(src, source=src_path, cache_dir=args.cache,
                 offline=args.offline, search=not args.no_search)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"facts   : {result['facts']['count']} concrete facts reduced")
    print(f"knowledge: {result['knowledge']['stats']['acquired']}/"
          f"{result['knowledge']['stats']['candidates']} library symbols acquired")
    r1, r2 = result["rounds"]
    print(f"round 1 : concepts={r1['concepts']}  gaps={r1['gaps']}")
    print(f"domain  : {result['domain']['stats']}  entities={result['domain']['entities']}")
    for rec in result["domain"]["records"]:
        if rec["entity"]:
            print(f"   search '{rec['label']}' -> {rec['entity']}  "
                  f"(evidence: {rec['evidence'][:1]})")
    print(f"round 2 : concepts={r2['concepts']}")
    print("\n--- core concept (kernel-certified) ---")
    for s in result["sentences"]:
        tag = "CORE" if s["level"] == "core" else "sup "
        print(f"  [{tag}] {s['text']}   <- {s['support']}")
    print(f"ablation (no domain knowledge): {result['ablation_without_knowledge']}")
    print(f"concept_score: {result['concept_score']['score']} "
          f"{result['concept_score']['produced']}")
    print(f"verdict: {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())