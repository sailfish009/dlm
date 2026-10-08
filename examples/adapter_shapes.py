"""Adapter shapes: what replaces the 4096-d LLM embedding in a CLM/SD pipeline.

Run: python examples/adapter_shapes.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dlm import DecisionEngine, DlmTorso, FEATURE_NAMES, KnowledgeBase, fact, rule
from dlm.terms import V


def main() -> None:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("edge", a, b))
    x, y, z = V("x"), V("y"), V("z")
    kb.add_rule(rule(fact("reach", x, y), fact("edge", x, y), name="base"))
    kb.add_rule(rule(fact("reach", x, z), fact("edge", x, y), fact("reach", y, z), name="step"))

    torso = DlmTorso(DecisionEngine(kb))
    options = ["reach(alice,carol)", "reach(carol,alice)", "edge(bob,carol)"]
    rows = torso.batch_features("", options)

    print("reference CLM torso width: 4096 (learned)")
    print(f"DLM adapter width:         {torso.num_features} (exact proof evidence)")
    print("features:", FEATURE_NAMES)
    print()
    for opt, row in zip(options, rows):
        print(f"  {opt:22} -> {[round(float(v), 3) for v in row]}")
    print("\nstate features (slot-head shape):", torso.state_features().tolist())


if __name__ == "__main__":
    main()