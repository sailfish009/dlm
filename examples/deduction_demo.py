"""Deduction demo: derive an answer and show the proof trace.

Run: python examples/deduction_demo.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dlm import Engine, KnowledgeBase, fact, rule
from dlm.terms import V


def main() -> None:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("parent", a, b))

    x, y, z = V("x"), V("y"), V("z")
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, y), name="base"))
    kb.add_rule(rule(fact("ancestor", x, z),
                     fact("parent", x, y), fact("ancestor", y, z), name="step"))

    engine = Engine(kb)
    query = fact("ancestor", "alice", "dave")
    solution = next(engine.prove(query), None)
    print("query:", query)
    if solution is None:
        print("no proof")
        return
    print("proved; proof depth =", solution.proof.depth(),
          "leaves =", solution.proof.leaves())
    print(solution.proof.render())


if __name__ == "__main__":
    main()