"""Benchmark: semi-naive kernel closure vs the naive fixpoint.

Run:  PYTHONPATH=. python experiments/train/bench_closure.py [--n N] [--naive-max M]

Reports closure size and wall time on a transitive chain (the shape that made the
naive fixpoint re-derive the whole relation every round).  `--naive-max` caps the
chain length for the naive baseline so the script stays quick.
"""
from __future__ import annotations

import argparse
import time

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure

x, y, z = Var("?x"), Var("?y"), Var("?z")
TRANS = Rule(Atom("e", (x, z)), (Atom("e", (x, y)), Atom("e", (y, z))), "t")


def chain(n: int) -> KnowledgeBase:
    facts = {Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))) for i in range(n)}
    return KnowledgeBase(facts, (TRANS,))


def naive(kb: KnowledgeBase) -> set:
    from dlm import _join, _subst
    facts = set(kb.facts)
    changed = True
    while changed:
        changed = False
        by: dict = {}
        for f in facts:
            by.setdefault(f.pred, []).append(f)
        for r in kb.rules:
            for s in _join(r.body, by):
                h = _subst(r.head, s)
                if h.is_ground() and h not in facts:
                    facts.add(h)
                    changed = True
    return facts


def timed(fn, *a):
    t = time.perf_counter()
    out = fn(*a)
    return out, time.perf_counter() - t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--naive-max", type=int, default=80)
    args = ap.parse_args(argv)

    N = min(args.n, args.naive_max)
    out, dt = timed(naive, chain(N))
    print(f"naive        chain={N:4d}  closure={len(out):7d}  time={dt:8.3f}s")

    out, dt = timed(closure, chain(N))
    print(f"semi-naive   chain={N:4d}  closure={len(out):7d}  time={dt:8.3f}s")

    out, dt = timed(closure, chain(args.n))
    print(f"semi-naive   chain={args.n:4d}  closure={len(out):7d}  time={dt:8.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())