"""North-star vertical slice: acquire -> learn -> understand -> IR-TREE -> NL.

Reads the PyTorch MNIST example, REDUCES it to function-free Horn facts, LEARNS
the transitive ``calls`` rule from the reduction itself, derives an understanding
set through the trusted kernel, emits it as an IR *form* (IR-TREE), and glosses it
into sentences -- each sentence carrying the atoms that entail it, checked against
the kernel closure.  Where the reduction captured nothing, there is no sentence.
"""
from __future__ import annotations

import argparse
import json
import os
import time

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.abstract import abstract_theory
from dlm.ground import Ground, learn
from dlm.lisp import atom_to_form, dump, form_to_rule, rule_to_form
from dlm.proof import proof_ir, proof_size, prove, verify

try:
    from .acquire import URL, acquire
    from .extract import extract
    from .knowledge import acquire_knowledge, meaning_facts
    from .realize import realize
    from .semantics import bridge_forms, meaning_forms
    from .semantics import UNDERSTANDING  # noqa: F401  (re-exported for callers)
except ImportError:  # direct `python experiments/mnist/run.py`
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from acquire import URL, acquire
    from extract import extract
    from knowledge import acquire_knowledge, meaning_facts
    from realize import realize
    from semantics import bridge_forms, meaning_forms
    from semantics import UNDERSTANDING  # noqa: F401

KNOWLEDGE_CACHE = os.path.join(os.path.dirname(__file__), "cache")

CALLS = Rule(Atom("calls", (Var("?x"), Var("?z"))),
             (Atom("calls", (Var("?x"), Var("?y"))), Atom("calls", (Var("?y"), Var("?z")))))

# The reduction's own vocabulary: the learner induces laws over STRUCTURE only.
# The acquired ``meaning`` facts (and the understanding predicates they derive)
# are built for interpretation; letting them into the body search yields
# in-sample-coincidental rules (e.g. ``backpropagates`` in a transitive-calls
# body), so the structural law is induced over the reduction vocabulary alone.
STRUCTURAL = frozenset({"imports", "defines", "method_of", "inherits",
                        "creates", "calls", "step_of", "before"})
STRUCT_GROUND = Ground(())


def atom_of(fact: tuple) -> Atom:
    return Atom(fact[0], tuple(Const(x) for x in fact[1:]))


def astr(a: Atom) -> str:
    return "(" + " ".join([a.pred] + [t.name for t in a.args]) + ")"


def transitive(atoms: set) -> set:
    kb = KnowledgeBase(set(atoms))
    kb.add_rule(CALLS)
    return closure(kb)


def negatives(closed_calls: set, universe: list, limit=None) -> list:
    have = {(a.args[0].name, a.args[1].name) for a in closed_calls}
    out = []
    for x in universe:
        for z in universe:
            if x == z or (x, z) in have:
                continue
            out.append(Atom("calls", (Const(x), Const(z))))
            if limit is not None and len(out) >= limit:
                return out
    return out


def law_transfer(base: set) -> dict:
    """Can the general call law be induced from ONE file?  Hold out each owner.

    All multi-hop ``calls`` pairs in a single small file share the entry point
    (``main``), so restricting to any train split leaves no non-trivial positive
    to generalize from.  This is the honest reason the general law is learned
    across repos (``experiments/code``) and merely APPLIED here.
    """
    calls = {a for a in base if a.pred == "calls"}
    pos_all = transitive(calls)
    universe = sorted({t.name for a in calls for t in a.args})
    negs = negatives(pos_all, universe)
    struct = {a for a in base if a.pred in STRUCTURAL}
    owners = sorted({a.args[0].name for a in calls})
    out = {}
    testable = False
    for held in owners:
        train = {a.args[0].name for a in calls if a.args[0].name != held}
        held_pos = {p for p in pos_all if p.args[0].name == held and p not in base}
        nondirect = {p for p in pos_all if p.args[0].name in train and p not in base}
        if held_pos:
            testable = True
        if not held_pos:
            out[held] = {"status": "not_testable", "held_nondirect": 0}
            continue
        if not nondirect:
            out[held] = {"status": "no_multi_hop_train_examples",
                         "held_nondirect": len(held_pos)}
            continue
        res = learn(STRUCT_GROUND, struct, [p for p in pos_all if p.args[0].name in train], negs,
                    max_body=2, extra_vars=2, max_rules=3)
        out[held] = {"status": "learned", "rules": len(res.experience.rules),
                     "held_covered": len({p for p in held_pos if p in res.covered}),
                     "held_nondirect": len(held_pos)}
    return {"per_held_owner": out,
            "general_law_identifiable_from_one_file":
                testable and any(v.get("status") == "learned" and v["held_nondirect"] > 0
                                 for v in out.values())}


def run(src: str, source: str = URL, module: str = "main",
        cache_dir: str = KNOWLEDGE_CACHE, offline: bool = True,
        knowledge: dict = None) -> dict:
    ext = extract(src, module)
    labels, pipelines = ext["labels"], ext["pipelines"]

    # ACQUIRE the meaning of the external (library) symbols the reduction found.
    # ``knowledge`` may be passed in (tests); otherwise it is read from the web
    # cache.  Offline by default: no network, cached records only, unknowns abstain.
    if knowledge is None:
        knowledge = acquire_knowledge(ext["facts"], labels, cache_dir=cache_dir,
                                      offline=offline)
    meanings = knowledge["meanings"]

    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(meanings)}

    calls = {a for a in base if a.pred == "calls"}
    positives = transitive(calls)
    universe = sorted({t.name for a in calls for t in a.args})
    negs = negatives(positives, universe)

    ground = Ground(tuple(form_to_rule(f) for f in bridge_forms()))
    struct_base = {a for a in base if a.pred in STRUCTURAL}
    res = learn(STRUCT_GROUND, struct_base, positives, negs, max_body=2, extra_vars=2, max_rules=4)

    kb = KnowledgeBase(base)
    for r in ground.rules:
        kb.add_rule(r)
    for r in res.experience.rules:
        kb.add_rule(r)
    closed = closure(kb)
    closed_strs = {astr(a) for a in closed}

    # HONEST soundness: the learned rule must not derive a `calls` pair outside the
    # true transitive closure, over the WHOLE complement (not just sampled negatives).
    derived_calls = {a for a in closed if a.pred == "calls"}
    false_final = sorted(astr(a) for a in derived_calls - positives)

    sentences = realize(closed, labels, pipelines, module, base)
    for s in sentences:
        s["verified"] = all(tok in closed_strs for tok in s["support"])

    target = Atom("calls", (Const(module), Const("loss_backward")))
    p = prove(kb, target) if target in closed else None
    proof = None if p is None else {
        "atom": astr(target), "size": proof_size(p), "verified": verify(p, kb),
        "ir": dump(proof_ir(p)),
    }

    trains = Atom("trains", (Const("train"),))
    p2 = prove(kb, trains) if trains in closed else None
    ground_proof = None if p2 is None else {
        "atom": astr(trains), "size": proof_size(p2), "verified": verify(p2, kb),
        "ir": dump(proof_ir(p2)),
    }

    abs_res = abstract_theory(tuple(ground.rules) + tuple(res.experience.rules), closed)

    law = law_transfer(base)

    hidden = ("calls", "step_of", "before", "creates")
    ir = ("understanding",
          ("source", source),
          ("module", module),
          ("knowledge", *[atom_to_form(atom_of(f)) for f in meaning_forms(meanings)]),
          ("facts", *[atom_to_form(a) for a in sorted(base, key=astr)]),
          ("ground", *[rule_to_form(r) for r in ground.rules]),
          ("learned", *[rule_to_form(r) for r in res.experience.rules]),
          ("derived", *[atom_to_form(a) for a in sorted(closed, key=astr)
                        if a.pred not in hidden]))

    return {
        "source": source,
        "module": module,
        "counts": {"facts": len(base), "calls_closure": len(positives),
                   "learned_rules": len(res.experience.rules),
                   "derived_atoms": len(closed)},
        "knowledge": {
            "stats": knowledge["stats"],
            "meanings": meanings,
            "records": [
                {"label": r["label"], "entry": r["entry"], "resolution": r["resolution"],
                 "concept": r["concept"], "url": r["url"], "definition": r["definition"],
                 "providers": r.get("providers", [])}
                for r in knowledge["records"]
            ],
        },
        "learned": [astr(r.head) + " :- " + ", ".join(astr(b) for b in r.body)
                    for r in res.experience.rules],
        "false_assert": len(res.false_assert),
        "false_final": false_final[:50],
        "false_final_count": len(false_final),
        "law_transfer": law,
        "ir": dump(ir),
        "narrative": sentences,
        "all_sentences_verified": all(s["verified"] for s in sentences),
        "proof": proof,
        "ground_proof": ground_proof,
        "abstract": {"dl_before": abs_res.dl_before, "dl_after": abs_res.dl_after,
                     "gain": abs_res.compression_gain,
                     "invented": [a.name for a in abs_res.abstractions]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="MNIST north-star vertical slice")
    ap.add_argument("--url", default=URL)
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "cache"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "reports", "mnist"))
    args = ap.parse_args(argv)

    src = acquire(args.url, cache_dir=args.cache, offline=args.offline, local=args.local)
    result = run(src, args.url, cache_dir=args.cache, offline=args.offline)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"source  : {result['source']}")
    kstats = result["knowledge"]["stats"]
    print(f"knowledge: {kstats['acquired']}/{kstats['candidates']} symbols acquired "
          f"({kstats['fetched_new']} new, offline={kstats['offline']}); "
          f"meanings={result['knowledge']['meanings']}")
    print(f"counts  : {result['counts']}  false={result['false_assert']} "
          f"false_final={result['false_final_count']}")
    print(f"learned : {result['learned']}")
    print(f"law     : general_law_identifiable_from_one_file="
          f"{result['law_transfer']['general_law_identifiable_from_one_file']} "
          f"(see experiments/code for the cross-repo law)")
    print(f"proof   : {result['proof'] and result['proof']['atom']} "
          f"size={result['proof'] and result['proof']['size']} "
          f"verified={result['proof'] and result['proof']['verified']}")
    print(f"abstract: DL {result['abstract']['dl_before']} -> {result['abstract']['dl_after']} "
          f"(gain {result['abstract']['gain']}, invented {result['abstract']['invented']})")
    print("\n--- narrative (each line backed by kernel facts) ---")
    for s in result["narrative"]:
        mark = "ok " if s["verified"] else "?? "
        print(f"  {mark}{s['text']}")
    print(f"\nall_sentences_verified = {result['all_sentences_verified']}")
    print(f"report: {os.path.join(out_dir, 'result.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())