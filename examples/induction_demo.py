"""Inductive rule learning demo: recover a rule from examples, not from a human.

Run: python examples/induction_demo.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dlm import Engine, KnowledgeBase, fact, induce_rules


def main() -> None:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave"), ("dave", "erin")]:
        kb.add_fact(fact("parent", a, b))

    positives = [fact("grandparent", "alice", "carol"),
                 fact("grandparent", "bob", "dave"),
                 fact("grandparent", "carol", "erin")]
    negatives = [fact("grandparent", "alice", "bob"),
                 fact("grandparent", "bob", "carol")]

    rules = induce_rules(kb, positives, negatives, max_body=2, n_exist=1)
    print("induced rules:")
    for r in rules:
        print("  ", r)

    trial = KnowledgeBase()
    for f in kb.facts():
        trial.add_fact(f)
    for r in rules:
        trial.add_rule(r)
    closure = Engine(trial).forward_chain()
    print("positives derived:", sum(p in closure for p in positives), "/", len(positives))
    print("negatives covered:", sum(n in closure for n in negatives), "/", len(negatives))


if __name__ == "__main__":
    main()