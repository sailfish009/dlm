#!/usr/bin/env python3
"""M5: grammar-constrained rule proposal with a symbolic kernel reward.

This is a generator, not a ranker.  It constructs Horn rules from a finite
grammar, rejects malformed/ill-typed rules, and uses the kernel utility oracle
as a reward.  The held-out split is over whole rules.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "m1_proof_state"))
import world  # noqa: E402


def split_rules(seed=31):
    rules = list(world.ALL_RULES)
    rng = random.Random(seed)
    rng.shuffle(rules)
    return rules[:70], rules[70:]


def grammar_ok(r: world.Rule) -> bool:
    if not (1 <= len(r.body) <= 2):
        return False
    if r.head in r.body:
        return False
    if len(set(r.body)) != len(r.body):
        return False
    return all(0 <= p < world.P for p in (r.head, *r.body))


def prior_table(train_rules, train_worlds):
    head = np.ones(world.P)
    body = np.ones(world.P)
    length = np.ones(3)
    for w in train_worlds:
        rules = list(w.theory)
        for r in train_rules:
            b = world.utility2(w, rules, r, w.goals)
            if b["utility"] > 0 and b["conflict"] == 0:
                head[r.head] += 1
                for p in r.body:
                    body[p] += 1
                length[len(r.body)] += 1
    head /= head.sum(); body /= body.sum(); length /= length.sum()
    return head, body, length


def prior_score(r, table):
    head, body, length = table
    s = np.log(head[r.head]) + np.log(length[len(r.body)])
    for p in r.body:
        s += np.log(body[p])
    return float(s)


def kernel_score(w, rules, r):
    b = world.utility2(w, rules, r, w.goals)
    return b["utility"] if b["conflict"] == 0 else -1e9


def random_triple(rng):
    # unconstrained: may repeat, may put head in body, may use 3 body tokens
    head = rng.randrange(world.P)
    n = rng.choice((1, 2, 3))
    body = tuple(rng.randrange(world.P) for _ in range(n))
    return world.Rule(head, body)


def propose(w, rules, train_rules, table, rng, k=5, mode="constrained"):
    if mode == "random_unconstrained":
        raw = [random_triple(rng) for _ in range(k * 4)]
        props = raw[:k]
        return props, sum(1 for r in props if not grammar_ok(r))
    if mode == "random_valid":
        valid = [r for r in world.ALL_RULES if grammar_ok(r)]
        return rng.sample(valid, k), 0
    pool = [r for r in world.ALL_RULES if grammar_ok(r)]
    if mode == "prior":
        scored = [(prior_score(r, table), r) for r in pool]
    elif mode == "kernel":
        scored = [(kernel_score(w, rules, r), r) for r in pool]
    elif mode == "constrained":
        scored = [(prior_score(r, table) + 2.0 * kernel_score(w, rules, r), r) for r in pool]
    else:
        raise ValueError(mode)
    scored.sort(key=lambda x: -x[0])
    return [r for _s, r in scored[:k]], 0


def eval_worlds(worlds, train_rules, table, seed=31):
    rng = random.Random(seed)
    modes = ["random_unconstrained", "random_valid", "prior", "kernel", "constrained"]
    out = {m: {"recovery": 0, "false": 0, "n": 0, "generated": 0} for m in modes}
    for w in worlds:
        rules = list(w.theory)
        useful = []
        for r in world.ALL_RULES:
            if r in train_rules:
                continue
            b = world.utility2(w, rules, r, w.goals)
            if b["utility"] > 0 and b["conflict"] == 0:
                useful.append((b["utility"], r))
        if not useful:
            continue
        useful.sort(key=lambda x: -x[0])
        targets = {r for u, r in useful if u == useful[0][0]}
        for mode in modes:
            props, false = propose(w, rules, train_rules, table, rng, mode=mode)
            out[mode]["n"] += 1
            out[mode]["generated"] += len(props)
            out[mode]["false"] += false
            out[mode]["recovery"] += int(any(r in targets for r in props))
    for m in modes:
        n = max(1, out[m]["n"])
        out[m]["recovery_rate"] = out[m]["recovery"] / n
        out[m]["false_rule_rate"] = out[m]["false"] / max(1, out[m]["generated"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-worlds", type=int, default=80)
    ap.add_argument("--seed", type=int, default=31)
    args = ap.parse_args()
    train_rules, heldout_rules = split_rules(args.seed)
    # build_split_m2 returns steps, not worlds; regenerate worlds directly.
    rng = random.Random(args.seed)
    train_worlds = [world.make_world(rng, "train", i, conflict=True) for i in range(120)]
    table = prior_table(train_rules, train_worlds)
    rng = random.Random(args.seed)
    test_worlds = [world.make_world(rng, "test", i, conflict=True) for i in range(args.test_worlds)]
    result = eval_worlds(test_worlds, train_rules, table, args.seed)
    result["split"] = {"train_rules": len(train_rules), "heldout_rules": len(heldout_rules),
                       "test_worlds": len(test_worlds)}
    print(json.dumps(result, indent=2))
    (HERE / "m5_result.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
