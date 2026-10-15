"""DLM v0.0039 experiment: label-free abstraction.

No labels anywhere.  From a theory + facts alone we (1) fold a recurring body
pattern into an **invented predicate**, (2) verify with the kernel that the
closure is *preserved*, (3) measure that the form-tree description length (DL)
*strictly shrinks*, and (4) measure whether the shorter theory covers more of the
same closure under a **fixed inference budget** -- the falsifiable claim.

The theory is synthetic: ``n_rules`` rules that all share a chain-of-edges core,
so the recurring structure is real and the only lever is abstraction.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Tuple

from dlm import Atom, Const, Rule, Var, closure, KnowledgeBase
from dlm.abstract import (abstract_theory, closure_budget, closure_preserved,
                          common_body_patterns, mined_subforms, theory_dl)
from dlm.lisp import rule_to_form


def _chain(var_names: Tuple[str, ...], pred: str) -> Tuple[Atom, ...]:
    return tuple(Atom(pred, (Var(var_names[i]), Var(var_names[i + 1])))
                 for i in range(len(var_names) - 1))


def build(n_rules: int, core_len: int) -> Tuple[List[Rule], set]:
    """``n_rules`` rules sharing a ``core_len``-edge chain, plus a chain of facts."""
    names = tuple(f"?x{i}" for i in range(core_len + 1))
    core = _chain(names, "edge")
    rules = [Rule(Atom(f"h{i}", (Var(names[0]), Var(names[-1]))), core, name=f"h{i}")
             for i in range(n_rules)]
    facts = {Atom("edge", (Const(f"c{i}"), Const(f"c{i + 1}"))) for i in range(8)}
    return rules, facts


def run(args) -> dict:
    rules, facts = build(args.rules, args.core)
    target = closure(KnowledgeBase(set(facts), tuple(rules)))

    res = abstract_theory(rules, facts, min_support=args.min_support,
                          max_pattern=args.core)
    preserved = closure_preserved(facts, rules, res.theory)

    # fixed-budget coverage of the SAME closure, un-abstracted vs abstracted
    budgets = [args.budget // 2, args.budget, args.budget * 2]
    base_kb = KnowledgeBase(set(facts), tuple(rules))
    abs_kb = KnowledgeBase(set(facts), res.theory)
    budget_curve = []
    for b in budgets:
        got0 = closure_budget(base_kb, b) & target
        got1 = closure_budget(abs_kb, b) & target
        budget_curve.append({
            "budget": b,
            "baseline": round(len(got0) / len(target), 4),
            "abstracted": round(len(got1) / len(target), 4),
            "gain": len(got1) - len(got0),
        })

    forms = [rule_to_form(r) for r in rules]
    report = {
        "config": {"rules": args.rules, "core": args.core, "min_support": args.min_support,
                   "budget": args.budget},
        "target_atoms": len(target),
        "dl_before": res.dl_before,
        "dl_after": res.dl_after,
        "compression_gain": res.compression_gain,
        "compression_ratio": round(1 - res.dl_after / res.dl_before, 4),
        "closure_preserved": preserved,
        "invented": [
            {"name": a.name, "support": a.support, "uses": a.uses,
             "definition": str(a.definition.head) + " :- " +
                           ", ".join(map(str, a.definition.body))}
            for a in res.abstractions
        ],
        "macro_library": [{"pattern": k, "count": n}
                          for k, n in mined_subforms(forms, min_support=args.min_support)],
        "budget_curve": budget_curve,
    }
    report["verdict"] = {
        "pattern_found": len(res.abstractions) > 0,
        "closure_preserved": preserved,
        "dl_strictly_decreases": res.compression_gain > 0,
        "budget_coverage_gain": any(c["gain"] > 0 for c in budget_curve),
    }
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rules", type=int, default=6)
    p.add_argument("--core", type=int, default=4, help="shared core chain length")
    p.add_argument("--min-support", type=int, default=2)
    p.add_argument("--budget", type=int, default=400)
    p.add_argument("--json", default="")
    args = p.parse_args(argv)
    out = run(args)
    text = json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False)
    print(text)
    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0 if all(out["verdict"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())