"""Experiments/closedworld -- closed-world deduction on the real program (v0.0047).

The north-star reading can say what the program HAS.  v0.0047 lets the kernel
deduce what it does NOT have, over an explicitly GIVEN candidate universe:

    absent(?m, ?l) :- is_module(?m), candidate_layer(?l), not has_layer(?m, ?l)

The point is NOT "more sentences" but a NEW kind of conclusion -- a certified
negative -- and the property pure Horn cannot have: NON-MONOTONICITY.  Adding a
single ``has_layer`` fact retracts the matching ``absent`` fact.  Three probes
show the kernel stays sound:

  * retraction    : add has_layer(net,batchnorm2d) -> absent(net,batchnorm2d) gone
  * stratification: a negative self-dependency is REJECTED (ValueError)
  * safety        : a negated literal with an unbound variable asserts nothing
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from dlm import Atom, Const, KnowledgeBase, closure, strata
from dlm.closedworld import (CANDIDATE_LAYERS, absence_rule, absent_kinds,
                             candidate_facts, unsound_self_negation)

try:
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import atom_of
    from ..reading.run import CACHE, NORTH_STAR_SRC, _closed
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import atom_of
    from reading.run import CACHE, NORTH_STAR_SRC, _closed

HERE = os.path.dirname(os.path.abspath(__file__))


def _base_closure(src: str, cache_dir: str, offline: bool):
    ext = extract(src, "main")
    k = acquire_knowledge(ext["facts"], ext["labels"], cache_dir=cache_dir, offline=offline)
    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(k["meanings"])}
    return _closed(base)


def run(src: str, cache_dir: str = CACHE, offline: bool = True) -> dict:
    closed = _base_closure(src, cache_dir, offline)
    subjects = sorted(a.args[0].name for a in closed if a.pred == "is_module")
    module = subjects[0] if subjects else "net"
    have = sorted(a.args[1].name for a in closed
                  if a.pred == "has_layer" and a.args[0].name == module)

    kb = KnowledgeBase(set(closed))
    kb.add_rule(absence_rule())
    kb.add_facts(candidate_facts())
    cw = closure(kb)
    absent = absent_kinds(cw, module)
    st = strata(kb)

    # NON-MONOTONICITY: add one positive fact -> the matching negative retracts.
    target = next(l for l in CANDIDATE_LAYERS if l not in have)
    kb2 = kb.copy()
    kb2.add_fact(Atom("has_layer", (Const(module), Const(target))))
    absent2 = absent_kinds(closure(kb2), module)
    retracted = target in absent and target not in absent2

    # STRATIFICATION: a negative self-cycle is refused, not guessed.
    try:
        closure(KnowledgeBase({Atom("q", (Const("x"),))}, (unsound_self_negation(),)))
        rejected = False
    except ValueError:
        rejected = True

    # SAFETY: an unbound negated literal must assert nothing.
    from dlm import NegAtom, Rule, Var
    x, y = Var("x"), Var("y")
    unsafe = Rule(Atom("bad", (x,)), (Atom("candidate_layer", (y,)),
                                      NegAtom(Atom("has_layer", (x, y)))))
    kb3 = KnowledgeBase(set(closed), (absence_rule(), unsafe))
    kb3.add_facts(candidate_facts())
    safe = not any(a.pred == "bad" for a in closure(kb3))

    verdict = {
        "candidate_universe_given": bool(CANDIDATE_LAYERS),
        "has_facts_present": len(have) >= 3,
        "negatives_derived": len(absent) >= 1,
        "every_absence_is_not_a_has": all(l not in have for l in absent),
        "stratified": max(st.values()) >= 1,
        "monotone_addition_retracts": retracted,
        "negative_only_has_layer": absences_are_has_exceptions(cw, have),
        "non_stratified_rejected": rejected,
        "unsafe_negation_asserts_nothing": safe,
    }
    return {
        "program": module,
        "known_layers": have,
        "candidate_universe": list(CANDIDATE_LAYERS),
        "absent": absent,
        "retraction_probe": {"added": target, "retracted": retracted,
                             "absent_after": absent2},
        "strata": dict(sorted(st.items())),
        "verdict": verdict,
    }


def absences_are_has_exceptions(cw: set, have) -> bool:
    """Every ``absent(m,l)`` atom corresponds to a candidate not in ``have``."""
    for a in cw:
        if a.pred == "absent":
            if a.args[1].name in have:
                return False
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="closed-world deduction over a program")
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "closedworld"))
    args, _ = ap.parse_known_args(argv)

    src = open(args.local or NORTH_STAR_SRC, "r", encoding="utf-8").read()
    result = run(src, cache_dir=args.cache, offline=args.offline)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"program : {result['program']}")
    print(f"has     : {result['known_layers']}")
    print(f"absent  : {result['absent']}  (closed world over {len(result['candidate_universe'])} candidates)")
    print(f"retract : added has_layer({result['program']},{result['retraction_probe']['added']}) "
          f"-> absent retracted: {result['retraction_probe']['retracted']}")
    print(f"verdict : {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())