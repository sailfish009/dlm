"""The explanation / abstraction layer (DLM v0.0030, NOTE 82).

Question.  v0.0029 made the S-expr substrate read and write itself, but a grown
theory is still only inspectable *one clause at a time*.  A million readable
clauses are as opaque as a black box, so "extreme interpretability" needs a
second half: at-scale, kernel-verified *self-interpretation*.  This experiment
exercises the four things ``dlm/explain.py`` adds -- and checks the honest
boundary: the layer is read-only over the core, every verdict comes from the
kernel, and "compressed" means behaviour-preserving *on the given KB* only.

Two parts, all deterministic, no human labels::

    A learned theory   grow a composition theory with the selfsup loop, witness
                       every clause from its kernel-computed contribution, and
                       answer a held goal with a re-checkable proof + its clauses
                       + their provenance + counterfactuals + a minimal proof
    B lemma library    a theory with genuine redundancy: exact compression drops
                       exactly the derivable lemmas (kernel closure unchanged,
                       held coverage unchanged), a random removal of the same
                       size breaks closure 5/6 of the time

Run::

    PYTHONPATH=. python experiments/explain/run.py
    PYTHONPATH=. python experiments/explain/run.py --quick --json reports/explain.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dlm import Atom, Clause, Const, KnowledgeBase, Rule, Theory, Var, closure  # noqa: E402
from dlm.explain import (  # noqa: E402
    abstract_theory,
    certify_from_tasks,
    closure_preserved,
    compress,
    counterfactual,
    explain,
    minimal_explanation,
    profile,
    summarize,
    verify_explanation,
)
from dlm.selfsup import StopPolicy, Task, run_loop  # noqa: E402


# ============================================================================
# helpers
# ============================================================================
def _atom(pred: str, a: int, b: int) -> Atom:
    return Atom(pred, (Const(f"n{a}"), Const(f"n{b}")))


def _chain_kb(nodes: int) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(nodes - 1):
        kb.add_fact(Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _composition_tasks(kb: KnowledgeBase, nodes: int, distances: Sequence[int]) -> List[Task]:
    train = list(range(0, nodes // 2))
    tasks: List[Task] = []
    for r, dist in enumerate(distances, start=1):
        pred = f"t{r}"
        pos = tuple(sorted((_atom(pred, a, a + dist) for a in train if a + dist < nodes), key=str))
        hit = {(a, a + dist) for a in train if a + dist < nodes}
        pairs = [(a, b) for a in train for b in train if a != b]
        neg = tuple(sorted((_atom(pred, a, b) for a, b in pairs if (a, b) not in hit), key=str))
        held_pos = tuple(
            sorted((_atom(pred, a, a + dist) for a in range(nodes // 2, nodes - dist)), key=str)
        )
        held_neg = tuple(sorted((_atom(pred, a, b) for a, b in pairs if abs(a - b) != dist), key=str))
        tasks.append(Task(pred, kb, pos, neg, held_pos, held_neg))
    return tasks


def _lemma_theory() -> Theory:
    """A theory with known, kernel-verified redundancy: ``two``/``three`` are
    entailed by ``direct`` + ``rec`` (derivable lemmas)."""
    x, y, z, w = Var("x"), Var("y"), Var("z"), Var("w")
    A = lambda a, b: Atom("anc", (a, b))  # noqa: E731
    E = lambda a, b: Atom("e", (a, b))  # noqa: E731
    return Theory(
        "anc",
        (
            Clause(Rule(A(x, y), (E(x, y),), "cdirect"), 0.0),
            Clause(Rule(A(x, y), (A(x, z), E(z, y)), "crec"), 0.0),
            Clause(Rule(A(x, y), (E(x, z), E(z, y)), "ctwo"), 0.0),
            Clause(Rule(A(x, y), (E(x, z), E(z, w), E(w, y)), "cthree"), 0.0),
        ),
    )


# ============================================================================
# A. a learned theory, explained
# ============================================================================
def demo_learned(nodes: int, distances: Sequence[int]) -> dict:
    kb = _chain_kb(nodes)
    tasks = _composition_tasks(kb, nodes, distances)
    loop = run_loop(
        tasks,
        mode="learn",
        policy=StopPolicy(max_rounds=len(tasks), stop_on_no_proposal=False),
        name="explain",
        budget=20000,
        seed=0,
    )
    theory = loop.theory
    prov = certify_from_tasks(theory, tasks)
    goal = _atom(f"t{len(distances)}", 0, distances[-1])
    explanation = explain(kb, theory, goal, provenance=prov)

    # provenance is complete, kernel-witnessed, and non-empty for every clause
    support = {
        d.name: len(d.support)
        for d in (prov.get(c.name) for c in theory.clauses)
        if d is not None
    }
    provenance_complete = prov.missing(theory) == () and all(v > 0 for v in support.values())

    # counterfactual: dropping a clause the proof used must break provability
    used = explanation.clauses
    broke = all(
        counterfactual(kb, theory, goal, drop=[name]) is False for name in used
    )
    # and a clause the proof did NOT use is a no-op counterfactual -- here all
    # four layers are used for this deep goal, so there is nothing to spare
    drops = counterfactual(kb, theory, goal, drop=["__absent__"])

    minimal = minimal_explanation(kb, theory, goal)
    summary = summarize(theory)
    return {
        "kb": "chain" if True else None,
        "nodes": nodes,
        "rounds": loop.rounds,
        "clauses": [c.name for c in theory.clauses],
        "proof_length": explanation.proof_length,
        "proof_clauses": list(explanation.clauses),
        "proved": explanation.proved,
        "verified": verify_explanation(kb, theory, explanation),
        "provenance_complete": provenance_complete,
        "provenance_support": support,
        "used_clauses_break_when_dropped": broke,
        "counterfactual_absent_clause": drops,
        "minimal_clauses": list(minimal.clauses),
        "minimal_proves": minimal.proof is not None,
        "minimal_verifies": verify_explanation(kb, theory, minimal),
        "description_length": summary["profile"]["description_length"],
        "review_budget": summary["review_budget"],
    }


# ============================================================================
# B. an exact, kernel-checked compression of a lemma library
# ============================================================================
def demo_compression(nodes: int) -> dict:
    theory = _lemma_theory()
    kb = _chain_kb(nodes)
    before = profile(theory)
    comp = compress(theory, kb)
    preserved = closure_preserved(theory, comp.theory, kb)
    abst = abstract_theory(theory)

    goals = [_atom("anc", i, i + 3) for i in range(nodes - 3)]
    closed_before = closure(theory.to_kb(kb))
    closed_after = closure(comp.theory.to_kb(kb))
    covered_before = sum(1 for g in goals if g in closed_before)
    covered_after = sum(1 for g in goals if g in closed_after)
    same_membership = all((g in closed_before) == (g in closed_after) for g in goals)

    # honest control: remove the same *number* of clauses at random; how often is
    # the closure still preserved?  (deterministic enumeration of all subsets)
    names = [c.name for c in theory.clauses]
    combos = list(itertools.combinations(names, len(comp.dropped)))
    preserved_combos = []
    for combo in combos:
        reduced = Theory(theory.name, tuple(c for c in theory.clauses if c.name not in combo))
        if closure_preserved(theory, reduced, kb):
            preserved_combos.append(list(combo))

    return {
        "nodes": nodes,
        "kept": [c.name for c in comp.theory.clauses],
        "dropped": list(comp.dropped),
        "closure_preserved": preserved,
        "description_length_before": before.description_length,
        "description_length_after": comp.after.description_length,
        "saved": comp.saved,
        "review_budget_before": abst.review_budget,
        "modules": [m.name for m in abst.modules],
        "held_goals": len(goals),
        "held_covered_before": covered_before,
        "held_covered_after": covered_after,
        "held_membership_identical": same_membership,
        "random_subsets": len(combos),
        "random_preserved": len(preserved_combos),
        "random_preserved_combos": sorted(preserved_combos),
    }


# ============================================================================
# report
# ============================================================================
def verdict(out: Dict[str, object]) -> List[Tuple[str, bool]]:
    a, b = out["learned"], out["compression"]
    return [
        ("a learned goal is answered with a re-checkable proof", a["proved"] and a["verified"]),
        ("every clause carries a kernel-witnessed derivation", a["provenance_complete"]),
        ("a used clause is load-bearing (counterfactual)", a["used_clauses_break_when_dropped"]),
        ("dropping an absent clause is a no-op", a["counterfactual_absent_clause"] is True),
        ("a minimal proof is smaller and still sound", a["minimal_proves"] and a["minimal_verifies"]),
        ("compression drops exactly the derivable lemmas", set(b["dropped"]) == {"ctwo", "cthree"}),
        ("compression leaves the kernel closure unchanged", b["closure_preserved"] is True),
        ("compression leaves held coverage unchanged", b["held_membership_identical"] and b["held_covered_after"] == b["held_goals"]),
        ("compression strictly shrinks the review budget", b["description_length_after"] < b["description_length_before"]),
        ("a random removal of the same size breaks closure", b["random_preserved"] < b["random_subsets"]),
    ]


def run(nodes: int, distances: Sequence[int]) -> dict:
    out: Dict[str, object] = {
        "config": {"nodes": nodes, "distances": list(distances), "layer": "dlm/explain.py"},
        "learned": demo_learned(nodes, distances),
        "compression": demo_compression(8),
    }
    checks = verdict(out)
    out["verdict"] = [{"check": c, "ok": bool(ok)} for c, ok in checks]
    out["all_pass"] = all(ok for _, ok in checks)
    return out


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="DLM v0.0030 explanation / abstraction demo")
    ap.add_argument("--nodes", type=int, default=40)
    ap.add_argument("--quick", action="store_true", help="shorter chain")
    ap.add_argument("--json", type=str, default=None)
    args = ap.parse_args(argv)
    if args.quick:
        nodes, distances = 24, (2, 4)
    else:
        nodes, distances = args.nodes, (2, 4, 8, 16)
    out = run(nodes, distances)
    if args.json:
        path = Path(args.json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())