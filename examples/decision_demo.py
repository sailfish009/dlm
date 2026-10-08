"""Decision demo: answer noul / choice / score by deduction, with a proof.

Run: python examples/decision_demo.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dlm import DecisionEngine, KnowledgeBase, SystemOneService, fact, rule
from dlm.terms import V


def reach_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("edge", a, b))
    x, y, z = V("x"), V("y"), V("z")
    kb.add_rule(rule(fact("reach", x, y), fact("edge", x, y), name="base"))
    kb.add_rule(rule(fact("reach", x, z), fact("edge", x, y), fact("reach", y, z), name="step"))
    kb.add_rule(rule(fact("level", 1), fact("reach", "alice", "carol"), name="l1"))
    return kb


def main() -> None:
    kb = reach_kb()
    engine = DecisionEngine(kb)
    service = SystemOneService(engine)

    payload = {
        "state": "",
        "questions": {
            "entailed": {"type": "noul", "instructions": "reach(alice,carol)"},
            "not_entailed": {"type": "noul", "instructions": "reach(carol,alice)"},
            "unparseable": {"type": "noul", "instructions": "alice knows carol"},
            "choose": {"type": "choice", "instructions": "which holds?",
                       "criteria": {"a": "reach(alice,dave)", "b": "reach(carol,bob)"}},
            "rate": {"type": "score", "instructions": "rate", "criteria": ["low", "mid", "high"]},
        },
    }
    out = service.handle(payload)
    print(json.dumps(out, indent=2))

    # The answer is auditable: show the proof.
    from dlm import Engine

    sol = next(Engine(kb).prove(fact("reach", "alice", "carol")))
    print("\nproof for reach(alice,carol):")
    print(sol.proof.render())


if __name__ == "__main__":
    main()