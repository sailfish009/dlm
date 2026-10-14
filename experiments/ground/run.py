"""DLM v0.0038 experiment: the open-universe signal.

A general rule is a promise over all referents.  We start with a tiny universe,
learn an Experience on top of an immutable Ground, then *open* the universe with
new referents and re-test.  The kernel gates every candidate: no negative may be
derived.  The point: the signal is external (new referents), not the theory's own
closure.
"""
from __future__ import annotations

import sys

from dlm import Atom, Const, closure, description_length
from dlm.lisp import parse
from dlm.ground import Ground, learn, Experience


def A(pred, *args):
    return Atom(pred, tuple(Const(a) for a in args))


def family(n):
    facts = {A("parent", f"n{i}", f"n{i+1}") for i in range(n)}
    pos = {A("ancestor", f"n{i}", f"n{j}") for i in range(n) for j in range(i + 2, n + 1)}
    neg = {A("ancestor", f"n{i}", f"n{j}") for i in range(n) for j in range(0, i + 1)}
    return facts, pos, neg


def main() -> int:
    ground = Ground.from_forms(parse("(rule (ancestor ?x ?y) (parent ?x ?y))"))

    print("== ground axioms ==")
    for r in ground.rules:
        print(f"  {r.head} :- {', '.join(map(str, r.body))}")

    # baseline: Ground alone
    facts, pos, neg = family(8)
    base = ground.base(facts)
    base_cov = len([p for p in pos if p in closure(base)])
    print(f"\nground-only coverage on full universe: {base_cov}/{len(pos)}")

    # open the universe round by round
    print("\n== open universe ==")
    print(f"{'round':>5} {'entities':>8} {'pos':>4} {'covered':>7} {'false_assert':>12} {'rules':>5}")
    ok = True
    for round_no, n in enumerate((3, 4, 6, 8), start=0):
        facts, pos, neg = family(n)
        res = learn(ground, facts, pos, neg)
        print(f"{round_no:>5} {n:>8} {len(pos):>4} {len(res.covered):>7} "
              f"{len(res.false_assert):>12} {res.clauses:>5}")
        for step in res.rounds:
            print(f"        + {step.get('added', step)}")
        if res.false_assert:
            ok = False
        if res.covered != frozenset(pos):
            ok = False

    # soundness + ground immutability
    print("\n== invariants ==")
    _, pos, neg = family(8)
    res = learn(ground, family(8)[0], pos, neg)
    print(f"  ground rules unchanged : {len(ground.rules) == 1}")
    print(f"  experience rules       : {res.clauses}")
    print(f"  covered all positives  : {res.covered == frozenset(pos)}")
    print(f"  false_assert           : {len(res.false_assert)}")
    print(f"  description length     : {res.description_length}")
    if not ok:
        print("VERDICT: FAIL")
        return 1
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())