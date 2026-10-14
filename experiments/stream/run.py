"""DLM v0.0038 stream experiment: does Experience accumulate round by round?

Controlled multi-relation domain (synthetic by default, real web with --web).
Entities are split into a *train* and a disjoint *test* set (open universe):
induction only ever sees train entities; every round is scored on the unseen
test entities.  The question is whether the residual on train forces a NEW
clause each round and whether held-out recovery strictly increases.

Ground is empty here on purpose: everything the model knows must be learned.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from typing import Dict, List, Sequence, Set, Tuple

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.ground import Ground, learn

TRANSITIVE = ("subclass_of", "part_of", "located_in")
INVERSE = ("country", "country_of")


def A(pred: str, x, y) -> Atom:
    return Atom(pred, (Const(x), Const(y)))


def true_rules() -> Tuple[Rule, ...]:
    out: List[Rule] = []
    for p in TRANSITIVE:
        x, y, z = Var("?x"), Var("?y"), Var("?z")
        out.append(Rule(Atom(p, (x, y)), (Atom(p, (x, z)), Atom(p, (z, y))), "true_" + p))
    x, y = Var("?x"), Var("?y")
    out.append(Rule(Atom(INVERSE[1], (x, y)), (Atom(INVERSE[0], (y, x)),), "true_inv"))
    return tuple(out)


def truth(facts) -> Set[Atom]:
    kb = KnowledgeBase(set(facts))
    for r in true_rules():
        kb.add_rule(r)
    return closure(kb)


# --------------------------------------------------------------------------- #
# domain generation
# --------------------------------------------------------------------------- #
def gen_synthetic(seed: int, n_train: int, n_test: int, chains: int, chain_len: int):
    rng = random.Random(seed)
    train_e = [f"t{i}" for i in range(n_train)]
    test_e = [f"e{i}" for i in range(n_test)]
    train, test = set(), set()
    for p in TRANSITIVE:
        for pool, dst in ((train_e, train), (test_e, test)):
            for _ in range(chains):
                nodes = sorted(rng.sample(pool, min(chain_len + 1, len(pool))))  # acyclic path
                for i in range(len(nodes) - 1):
                    dst.add(A(p, nodes[i], nodes[i + 1]))
    # inverse relation: country(subj, obj) facts -> country_of(obj, subj) entailed
    for pool, dst, tag in ((train_e, train, "c"), (test_e, test, "d")):
        for i in range(0, len(pool), 4):
            dst.add(A("country", pool[i], f"{tag}{i}"))
    return train, test


def gen_web(args):
    from experiments.web.acquire import acquire
    docs, hierarchy = acquire(args.docs, seed=args.seed, cache_dir=args.cache,
                              offline=args.offline, subclass_depth=args.subclass_depth,
                              pause=args.pause, retries=args.retries)
    preds = set(TRANSITIVE) | set(INVERSE)
    facts = set()
    for f in hierarchy:
        facts.add(A("subclass_of", f.subj, f.obj))
    for d in docs:
        for f in d.facts:
            if f.pred in preds:
                facts.add(A(f.pred, f.subj, f.obj))
    ents = sorted({c for a in facts for c in (a.args[0].name, a.args[1].name)})
    cut = max(1, int(len(ents) * (1.0 - args.test_frac)))
    train_e, test_e = set(ents[:cut]), set(ents[cut:])
    train = {a for a in facts if a.args[0].name in train_e and a.args[1].name in train_e}
    test = {a for a in facts if a.args[0].name in test_e and a.args[1].name in test_e}
    return train, test


def negatives(train: Set[Atom], truth_train: Set[Atom], cap: int) -> Set[Atom]:
    ents = sorted({c for a in train for c in (a.args[0].name, a.args[1].name)})
    preds = sorted({a.pred for a in train} | set(TRANSITIVE) | set(INVERSE))
    negs = set()
    for p in preds:
        for a in ents:
            for b in ents:
                if Atom(p, (Const(a), Const(b))) not in truth_train:
                    negs.add(Atom(p, (Const(a), Const(b))))
    if cap and len(negs) > cap:
        negs = set(sorted(negs, key=str)[:cap])
    return negs


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def run(args) -> dict:
    if args.web:
        train, test = gen_web(args)
        source = "web"
    else:
        train, test = gen_synthetic(args.seed, args.n_train, args.n_test, args.chains, args.chain_len)
        source = "synthetic"
    train_pos = truth(train)
    test_pos = truth(test)
    negs = negatives(train, train_pos, args.max_neg)

    curve: List[dict] = []

    def callback(exp, rule):
        derived = closure(exp.to_kb(Ground(()).base(test)))
        curve.append({
            "round": len(exp.rules),
            "rule": str(rule.head) + " :- " + ", ".join(str(b) for b in rule.body),
            "held_recovery": round(len(derived & test_pos) / len(test_pos), 4) if test_pos else 1.0,
            "false": len(derived - test_pos),
        })

    base_train = Ground(()).base(train)
    t0 = time.time()
    res = learn(Ground(()), train, train_pos, negs, max_body=2, extra_vars=1,
                max_rules=args.max_rules, callback=callback)
    induce_s = time.time() - t0
    print(f"induce_time={induce_s:.3f}s rounds={len(curve)}", file=sys.stderr)

    identity = len(test & test_pos) / len(test_pos) if test_pos else 1.0
    final = curve[-1]["held_recovery"] if curve else 0.0
    first = curve[0]["held_recovery"] if curve else 0.0
    heads = {r.head.pred for r in res.experience.rules}
    out = {
        "config": {
            "source": source, "seed": args.seed, "n_train": args.n_train,
            "n_test": args.n_test, "chains": args.chains, "chain_len": args.chain_len,
            "web": args.web, "max_rules": args.max_rules,
        },
        "domain": {
            "train_facts": len(train), "train_pairs": len(train_pos),
            "test_facts": len(test), "test_pairs": len(test_pos),
            "negatives": len(negs),
        },
        "curve": curve,
        "identity_recovery": round(identity, 4),
        "learned_rules": [str(r.head) + " :- " + ", ".join(str(b) for b in r.body)
                          for r in res.experience.rules],
        "law_heads_found": sorted(heads),
        "expected_heads": sorted(set(TRANSITIVE) | {INVERSE[1]}),
    }
    out["verdict"] = {
        "multi_round": len(curve) >= 2,
        "strictly_increases": any(c["held_recovery"] > first for c in curve[1:]),
        "sound_every_round": all(c["false"] == 0 for c in curve),
        "accumulation_beats_round1": final > first,
        "beats_identity": final > identity + 0.05,
        "all_laws_found": set(heads) == set(out["expected_heads"]),
    }
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--web", action="store_true")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--n-train", type=int, default=24)
    p.add_argument("--n-test", type=int, default=18)
    p.add_argument("--chains", type=int, default=3)
    p.add_argument("--chain-len", type=int, default=6)
    p.add_argument("--max-rules", type=int, default=8)
    p.add_argument("--max-neg", type=int, default=8000)
    p.add_argument("--test-frac", type=float, default=0.3)
    p.add_argument("--docs", type=int, default=120)
    p.add_argument("--cache", default="experiments/web/cache")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--subclass-depth", type=int, default=3)
    p.add_argument("--pause", type=float, default=0.5)
    p.add_argument("--retries", type=int, default=4)
    p.add_argument("--json", default="")
    args = p.parse_args(argv)

    out = run(args)
    text = json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False)
    print(text)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0 if all(out["verdict"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())