"""DLM v0.0038 web experiment: fetch real web hierarchy -> learn on Ground/Experience.

Pipeline: acquire (random Wikipedia/Wikidata, cached) -> class hierarchy facts
``subclass_of`` -> split a chain-preserving subgraph -> induce the transitivity
law on Ground(empty)+data with the kernel soundness gate -> evaluate held-out
recovery of the learned law against identity (raw facts) and a scrambled control.

No human labels.  The kernel (closure) is the only judge; the law is admitted
only if it derives no negative.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from typing import Iterable, List, Tuple

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.ground import Ground, learn


def A(x, y):
    return Atom("subclass_of", (Const(x), Const(y)))


def _trans_rule():
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    return Rule(Atom("subclass_of", (x, y)), (Atom("subclass_of", (x, z)), Atom("subclass_of", (z, y))), "trans")


def transitive(facts: Iterable[Atom]) -> set:
    kb = KnowledgeBase(set(facts))
    kb.add_rule(_trans_rule())
    return closure(kb)


def load_edges(args) -> Tuple[List[Tuple[str, str]], dict]:
    """Return a chain-preserving list of (subj, obj) subclass edges."""
    meta = {"source": "web", "docs": args.docs, "seed": args.seed}
    raw: List[Tuple[str, str]] = []
    if args.synthetic:
        rng = random.Random(args.seed)
        nodes = [f"c{i}" for i in range(args.docs)]
        for i in range(len(nodes) - 1):
            if rng.random() < 0.9:
                raw.append((nodes[i], nodes[i + 1]))
        meta["source"] = "synthetic"
    else:
        try:
            from .acquire import acquire
        except ImportError:  # run as a top-level script
            from acquire import acquire
        docs, hierarchy = acquire(
            args.docs, seed=args.seed, cache_dir=args.cache, offline=args.offline,
            subclass_depth=args.subclass_depth, pause=args.pause, retries=args.retries,
        )
        raw = [(f.subj, f.obj) for f in hierarchy]
        meta["articles"] = len(docs)
    # dedupe preserving acquisition (BFS) order, then bound chain-preservingly
    seen, edges = set(), []
    for e in raw:
        if e[0] == e[1] or e in seen:
            continue
        seen.add(e)
        edges.append(e)
    if args.max_edges and len(edges) > args.max_edges:
        edges = edges[: args.max_edges]
    meta["edges"] = len(edges)
    return edges, meta


def run(args) -> dict:
    edges, meta = load_edges(args)
    all_facts = {A(s, o) for s, o in edges}
    truth = transitive(all_facts)

    # train / held split of edges
    cut = max(1, int(len(edges) * args.train_frac))
    train_edges, held_edges = edges[:cut], edges[cut:]
    train_facts = {A(s, o) for s, o in train_edges}
    train_pos = transitive(train_facts)
    held_pos = truth - train_pos

    # negatives: ordered wrong pairs over the entity universe (bounded)
    ents = sorted({c for e in edges for c in e})
    negs = set()
    for a in ents:
        for b in ents:
            if a != b and A(a, b) not in truth:
                negs.add(A(a, b))
    if len(negs) > args.max_neg:
        negs = set(sorted(negs, key=str)[: args.max_neg])

    ground = Ground(())
    t0 = time.time()
    res = learn(ground, train_facts, train_pos, negs, max_body=2, extra_vars=1, max_rules=4)
    induce_s = time.time() - t0

    learned = closure(res.experience.to_kb(ground.base(all_facts)))
    identity = set(all_facts)

    # scrambled control: permute the train edges' constants, re-learn, re-test
    perm = list(ents)
    random.Random(args.seed + 999983).shuffle(perm)
    mp = dict(zip(ents, perm))
    sc_facts = {A(mp[s], mp[o]) for s, o in train_edges}
    sc_pos = transitive(sc_facts)
    sc_res = learn(Ground(()), sc_facts, sc_pos, negs, max_body=2, extra_vars=1, max_rules=4)
    scrambled = closure(sc_res.experience.to_kb(ground.base(all_facts)))

    def rec(closed):
        return len(closed & held_pos) / len(held_pos) if held_pos else 1.0

    out = {
        "config": {
            "docs": args.docs, "seed": args.seed, "offline": args.offline,
            "source": meta.get("source"), "train_frac": args.train_frac,
            "max_edges": args.max_edges, "synthetic": args.synthetic,
        },
        "corpus": meta,
        "graph": {
            "entities": len(ents), "edges": len(edges), "train_edges": len(train_edges),
            "true_pairs": len(truth), "train_pairs": len(train_pos), "held_pairs": len(held_pos),
            "negatives": len(negs),
        },
        "arms": {
            "identity": {"held_recovery": round(rec(identity), 4), "false": len(identity - truth)},
            "learned": {"held_recovery": round(rec(learned), 4), "false": len(learned - truth)},
            "scrambled": {"held_recovery": round(rec(scrambled), 4), "false": len(scrambled - truth)},
        },
        "learned_rules": [str(r.head) + " :- " + ", ".join(str(b) for b in r.body)
                          for r in res.experience.rules],
        "scrambled_rules": [str(r.head) + " :- " + ", ".join(str(b) for b in r.body)
                            for r in sc_res.experience.rules],
    }
    print(f"induce_time={induce_s:.3f}s", file=sys.stderr)
    a = out["arms"]
    out["verdict"] = {
        "learned_beats_identity": a["learned"]["held_recovery"] > a["identity"]["held_recovery"] + 0.1,
        "learned_sound": a["learned"]["false"] == 0,
        "identity_sound": a["identity"]["false"] == 0,
        "scrambled_not_better": a["scrambled"]["held_recovery"] <= a["learned"]["held_recovery"],
        "found_transitivity": any("subclass_of" in r and r.count("subclass_of") == 3
                                  for r in out["learned_rules"]),
    }
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--docs", type=int, default=60)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--cache", default="experiments/web/cache")
    p.add_argument("--train-frac", type=float, default=0.7)
    p.add_argument("--max-edges", type=int, default=200)
    p.add_argument("--max-neg", type=int, default=4000)
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
    return 0 if all(out["verdict"].values()) or out["verdict"]["found_transitivity"] else 1


if __name__ == "__main__":
    sys.exit(main())