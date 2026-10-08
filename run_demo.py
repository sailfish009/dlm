"""DLM v0.0001 — end-to-end demo (honest two-part evaluation).

Part A (mechanism): distractors that are non-instantiable (body predicates with
no backing facts). The decider should drop them, shrinking the candidate set
with no loss of true answers.

Part B (limitation): a distractor that is instantiable but semantically wrong,
with the same shape as a good rule. The v0.0001 hand features cannot separate
it, so false positives persist in BOTH arms. This is logged as a limitation,
not hidden.

Writes artifacts/demo_metrics.json.
"""
from __future__ import annotations

import json
import os
from itertools import product

from dlm import (
    Decider,
    Engine,
    KnowledgeBase,
    Pipeline,
    collect_training_data,
    fact,
    induce_rules,
    rule,
)
from dlm.terms import V, atom

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "artifacts", "demo_metrics.json")
CHAIN = [("alice", "bob"), ("bob", "carol"), ("carol", "dave"), ("dave", "erin")]
NODES = ["alice", "bob", "carol", "dave", "erin"]


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in CHAIN:
        kb.add_fact(fact("edge", a, b))
        kb.add_fact(fact("node", a))
    kb.add_fact(fact("node", "erin"))
    x, y, z = V("x"), V("y"), V("z")
    kb.add_rule(rule(fact("reach", x, y), fact("edge", x, y), name="reach_base"))
    kb.add_rule(rule(fact("reach", x, z), fact("edge", x, y), fact("reach", y, z), name="reach_step"))
    kb.add_rule(rule(fact("reach", x, y), fact("jump", x, y), name="reach_jump"))  # non-instantiable
    kb.add_rule(rule(fact("reach", x, y), fact("edge", x, z), fact("jump", z, y), name="reach_far"))  # half-backed
    kb.add_rule(rule(fact("reach", x, y), fact("edge", y, x), name="reach_rev"))  # hard: instantiable, wrong
    return kb


def ground_truth(kb: KnowledgeBase) -> set:
    good = KnowledgeBase()
    for f in kb.facts():
        good.add_fact(f)
    for r in kb.rules():
        if r.name in ("reach_base", "reach_step"):
            good.add_rule(r)
    return Engine(good).forward_chain()


def main() -> None:
    kb = build_kb()
    truth = ground_truth(kb)

    # unsafe-rule rejection demonstration
    x, y = V("x"), V("y")
    unsafe_rejected = False
    try:
        kb.add_rule(rule(fact("reach", x, y), fact("node", x), name="reach_unsafe"))
    except ValueError:
        unsafe_rejected = True

    gp_pos = [fact("grandparent", "alice", "carol"), fact("grandparent", "bob", "dave"), fact("grandparent", "carol", "erin")]
    gp_neg = [fact("grandparent", "alice", "bob"), fact("grandparent", "bob", "carol")]
    induced = induce_rules(kb, gp_pos, gp_neg, max_body=2, n_exist=1)
    for r in induced:
        kb.add_rule(r)

    all_pairs = [(a, b) for a, b in product(NODES, NODES) if a != b]
    positives = [atom("reach", a, b) for a, b in all_pairs if fact("reach", a, b) in truth]
    negatives = [atom("reach", a, b) for a, b in all_pairs if fact("reach", a, b) not in truth]

    X, yv = collect_training_data(kb, positives)
    dec = Decider(seed=0).fit(X, yv, epochs=600, lr=0.1)
    dec.calibrate(X, yv)

    pipe = Pipeline(kb, decider=dec, threshold=0.5)

    def evaluate(use_decider: bool) -> dict:
        pos_ok = 0
        neg_bad = 0
        sel = cand = 0
        fallbacks = 0
        dropped_names: set = set()
        for q in positives:
            res = pipe.answer(q, use_decider=use_decider)
            pos_ok += 1 if res.answers else 0
            sel += int(res.trace["n_selected"])
            cand += int(res.trace["n_candidates"])
            fallbacks += int(res.trace["used_fallback"])
            dropped_names.update(getattr(c.item, "name", "") for c in res.dropped if hasattr(c.item, "name"))
        for q in negatives:
            if pipe.answer(q, use_decider=use_decider).answers:
                neg_bad += 1
        return {
            "positives_answered": pos_ok,
            "positives_total": len(positives),
            "negatives_falsely_answered": neg_bad,
            "negatives_total": len(negatives),
            "selected_candidates": sel,
            "total_candidates": cand,
            "fast_path_fallbacks": fallbacks,
            "dropped_rule_names": sorted(n for n in dropped_names if n),
        }

    report = {
        "unsafe_rule_rejected": unsafe_rejected,
        "induced_rules": [str(r) for r in induced],
        "decider_params": dec.num_params(),
        "decider_temperature": dec.temperature,
        "part_A_noninstantiable_distractors": {
            "no_decider": evaluate(False),
            "with_decider": evaluate(True),
        },
        "note": "Part B limitation: reach_rev is instantiable and wrong; not separable by v0.0001 features.",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()