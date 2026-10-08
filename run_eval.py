"""Matched-arm evaluation for DLM v0.0002 (single variable: the decision source).

All arms see the same KB and the same option set.

  B (DLM)     decides by exact proof (closured reachability).
  A (head)    a learned head on SURFACE features only -- no proof, no
              derivability signal, no encoder. Its ceiling is the base rate here.
  C (prior)   predicts the train-split base rate.

Also measures the registered null (P4): with an instantiable-but-wrong rule added,
B's false positives on the specific derived-but-false atoms.

Writes artifacts/eval.json.
"""
from __future__ import annotations

import json
import math
import os
import random
from itertools import product

import numpy as np

from dlm import Decider, DecisionEngine, Engine, KnowledgeBase, fact, rule
from dlm.terms import V

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artifacts", "eval.json")

NODES = ["n0", "n1", "n2", "n3", "n4", "n5"]


def chain_kb(n: int = 6) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(n - 1):
        kb.add_fact(fact("edge", f"n{i}", f"n{i+1}"))
    x, y, z = V("x"), V("y"), V("z")
    kb.add_rule(rule(fact("reach", x, y), fact("edge", x, y), name="base"))
    kb.add_rule(rule(fact("reach", x, z), fact("edge", x, y), fact("reach", y, z), name="step"))
    return kb


def truth(kb: KnowledgeBase) -> set:
    return Engine(kb).forward_chain()


def surface_features(kb: KnowledgeBase, option: str) -> list[float]:
    """Features that carry NO proof information (a fair, weak control)."""
    facts = list(kb.facts())
    rules = list(kb.rules())
    preds_in_head = {r.head.pred for r in rules}
    pred = option.split("(")[0]
    return [
        1.0,
        float(option.count(",")) + 1.0 if "(" in option else 0.0,
        math.log1p(len(facts)),
        math.log1p(len(rules)),
        1.0 if pred in preds_in_head else 0.0,
        float(len(option)),
    ]


def main() -> None:
    random.seed(0)
    kb = chain_kb(len(NODES))
    closure = truth(kb)
    pairs = [(a, b) for a, b in product(NODES, NODES) if a != b]
    options = [f"reach({a},{b})" for a, b in pairs]
    labels = [1.0 if fact("reach", a, b) in closure else 0.0 for a, b in pairs]

    idx = list(range(len(options)))
    random.shuffle(idx)
    cut = len(idx) // 2
    tr, te = idx[:cut], idx[cut:]

    # Arm B: exact proof.
    eng = DecisionEngine(kb)
    b_full = [1.0 if eng.noul(_noul(o)).noul > 0.5 else 0.0 for o in options]

    # Arm A: learned head on surface features.
    X = np.asarray([surface_features(kb, o) for o in options], dtype=np.float64)
    head = Decider(n_features=len(surface_features(kb, options[0])), seed=0).fit(
        X[tr], np.asarray([labels[i] for i in tr]), epochs=400, lr=0.1)
    a_full = np.zeros(len(options))
    a_full[te] = (head.predict_proba(X[te]) > 0.5).astype(float)

    # Arm C: base rate from train.
    base = float(np.mean([labels[i] for i in tr]))
    c_full = np.full(len(options), 1.0 if base > 0.5 else 0.0)

    def acc(pred, ids):
        return float(np.mean([pred[i] == labels[i] for i in ids]))

    report = {
        "task": "reachability noul over a 6-node chain",
        "n_options": len(options),
        "n_train": len(tr),
        "n_test": len(te),
        "positive_rate": float(np.mean(labels)),
        "accuracy": {
            "B_dlm_proof": acc(b_full, te),
            "A_surface_head": acc(a_full, te),
            "C_base_rate": acc(c_full, te),
        },
        "arm_A_note": "surface features carry no proof signal, so A can only learn the base rate",
    }

    # Registered null P4: instantiable-but-wrong rule.
    kb_rev = chain_kb(len(NODES))
    x, y = V("x"), V("y")
    kb_rev.add_rule(rule(fact("reach", x, y), fact("edge", y, x), name="rev"))
    eng_rev = DecisionEngine(kb_rev)
    fp = [f"reach({b},{a})" for a, b in [("n0", "n1"), ("n3", "n4")]
          if eng_rev.noul(_noul(f"reach({b},{a})")).noul > 0.5]
    report["P4_null_false_positives"] = {
        "rev_derived_but_false": fp,
        "count": len(fp),
        "note": "identical surface features to a good rule; no v0.0002 feature separates them",
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps(report, indent=2))


def _noul(text: str):
    from dlm.schema import NoulQuestion

    return NoulQuestion(instructions=text)


if __name__ == "__main__":
    main()