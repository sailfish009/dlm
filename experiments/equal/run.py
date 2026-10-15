"""Experiments/equal -- equality / congruence on the real program (v0.0051, D7a).

FALSIFIER FIRST.  The D5 closed world (v0.0048) certified

    absent(net, maxpool2d)

even though the program's forward pass CALLS ``F.max_pool2d``.  The reason is a
vocabulary gap: positive evidence arrives under library ALIASES
(``f_max_pool2d``, ``nn_conv2d``) while the candidate universe uses canonical
layer kinds (``maxpool2d``, ``conv2d``).  A pure Horn theory cannot say the two
symbols denote the SAME thing; that is equality.

D7a supplies it as a *finite congruence* over the given symbol set: the alias
relation ``same_kind`` plus ``uses_layer`` (definition, method-call, or direct
call) feeding the SAME closed-world shape.  The claim is conservative: it adds
only the two new predicates and never changes a positive Horn conclusion.

Checks: the false negative is reproduced then fixed; the congruence is a true
equivalence relation; the extension is conservative; the remaining absences are
still every not-used candidate.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from dlm import KnowledgeBase, closure
from dlm.closedworld import (CANDIDATE_LAYERS, absence_rule, absent_kinds,
                             candidate_facts)
from dlm.equality import (absence_rule_equality, kind, same_kind_facts,
                          same_kind_pairs, symbols_in, uses_layer_rules)

try:
    from ..closedworld.run import _base_closure
    from ..reading.run import CACHE, NORTH_STAR_SRC
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from closedworld.run import _base_closure
    from reading.run import CACHE, NORTH_STAR_SRC

HERE = os.path.dirname(os.path.abspath(__file__))


def _equivalence_holds(pairs) -> bool:
    rel = set(pairs)
    dom = {a for a, _ in pairs} | {b for _, b in pairs}
    reflexive = all((x, x) in rel for x in dom)
    symmetric = all((b, a) in rel for a, b in rel)
    transitive = all((a, c) in rel for a, b in rel for b2, c in rel if b == b2)
    return reflexive and symmetric and transitive


def run(src: str, cache_dir: str = CACHE, offline: bool = True) -> dict:
    closed = _base_closure(src, cache_dir, offline)
    subjects = sorted(a.args[0].name for a in closed if a.pred == "is_module")
    module = subjects[0] if subjects else "net"
    have = sorted(a.args[1].name for a in closed
                  if a.pred == "has_layer" and a.args[0].name == module)
    calls = sorted({a.args[1].name for a in closed
                    if a.pred == "calls" and a.args[0].name == "net_forward"})

    # D5 WITHOUT equality: the raw closed world.
    kb_old = KnowledgeBase(set(closed))
    kb_old.add_rule(absence_rule())
    kb_old.add_facts(candidate_facts())
    absent_old = absent_kinds(closure(kb_old), module)
    reproduced = "maxpool2d" in absent_old and "f_max_pool2d" in calls

    # D7a WITH equality/congruence.
    syms = symbols_in(closed)
    kb_new = KnowledgeBase(set(closed))
    kb_new.add_facts(candidate_facts())
    kb_new.add_facts(same_kind_facts(syms))
    for r in uses_layer_rules():
        kb_new.add_rule(r)
    kb_new.add_rule(absence_rule_equality())
    cw = closure(kb_new)
    absent_new = absent_kinds(cw, module)
    used = sorted(a.args[1].name for a in cw
                  if a.pred == "uses_layer" and a.args[0].name == module)
    fixed = "maxpool2d" not in absent_new and "maxpool2d" in used

    # CONSERVATIVE EXTENSION: restricting the new closure to the old predicates
    # must equal the base (positive) closure exactly.
    new_preds = {"same_kind", "uses_layer", "absent", "candidate_layer"}
    conservative = {a for a in cw if a.pred not in new_preds} == set(closed)
    classes = _classes(syms)
    aliases_recognised = (same_kind(classes, "f_max_pool2d", "maxpool2d")
                          and same_kind(classes, "nn_conv2d", "conv2d"))

    verdict = {
        "false_negative_reproduced": reproduced,
        "false_negative_fixed": fixed,
        "equality_is_congruence": _equivalence_holds(same_kind_pairs(syms)),
        "conservative_extension": conservative,
        "aliases_recognised": aliases_recognised,
        "remaining_absences_are_unused": all(l not in used for l in absent_new),
        "present_layers_kept": all(l not in absent_new for l in have),
    }
    return {
        "program": module,
        "known_layers": have,
        "used_layers": used,
        "absent_without_equality": absent_old,
        "absent_with_equality": absent_new,
        "equality_classes": {k: sorted(v) for k, v in classes.items() if len(v) > 1},
        "calls_forward": calls,
        "verdict": verdict,
    }


def _classes(symbols):
    out: dict = {}
    for s in symbols:
        out.setdefault(kind(s), []).append(s)
    return out


def same_kind(classes: dict, a: str, b: str) -> bool:
    return a in classes.get(b, [])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="equality/congruence over a program")
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "equal"))
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
    print(f"used    : {result['used_layers']}")
    print(f"absent  : {result['absent_without_equality']} (no equality) "
          f"-> {result['absent_with_equality']} (with equality)")
    print(f"classes : {result['equality_classes']}")
    print(f"verdict : {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())