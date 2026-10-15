"""DLM v0.0039 code experiment: learn the dependency law on real GitHub import graphs.

Pipeline: acquire (seeded random small Python repos, cached) -> module import
graph ``(imports M N)`` -> hold out **whole repos** -> induce the transitivity
law on the train repos with the kernel soundness gate -> evaluate held-out
recovery on the unseen repos against identity (raw edges) and a scrambled
control.

No human labels and no weak supervision: the repo itself is the oracle.  The
kernel (``closure``) is the only judge; the law is admitted only if it derives
no negative.  This is the honest cross-distribution test the web experiment
cannot give -- the held-out repos never appear in induction.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from typing import Dict, Iterable, List, Tuple

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.ground import Ground, learn


def A(x, y):
    return Atom("imports", (Const(x), Const(y)))


def _trans_rule():
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    return Rule(Atom("imports", (x, y)),
                (Atom("imports", (x, z)), Atom("imports", (z, y))), "trans")


def transitive(facts: Iterable[Atom]) -> set:
    kb = KnowledgeBase(set(facts))
    kb.add_rule(_trans_rule())
    return closure(kb)


def _synthetic_repos(n_repos: int, per_repo: int, seed: int) -> Dict[str, List[Tuple[str, str]]]:
    """Chain-shaped import graphs so transitivity has real multi-hop pairs."""
    rng = random.Random(seed)
    repos: Dict[str, List[Tuple[str, str]]] = {}
    for r in range(n_repos):
        pre = f"syn{r}"
        mods = [f"{pre}_m{i}" for i in range(per_repo)]
        edges: List[Tuple[str, str]] = []
        for i in range(len(mods) - 1):
            if rng.random() < 0.9:
                edges.append((mods[i], mods[i + 1]))
            if i + 2 < len(mods) and rng.random() < 0.3:
                edges.append((mods[i], mods[i + 2]))
        repos[pre] = edges
    return repos


def load_repos(args) -> Tuple[Dict[str, List[Tuple[str, str]]], dict]:
    meta: dict = {"source": "github"}
    if args.synthetic:
        repos = _synthetic_repos(args.repos, args.per_repo, args.seed)
        meta = {"source": "synthetic", "repos": len(repos), "per_repo": args.per_repo}
        return repos, meta
    try:
        from . import code
        from .acquire import acquire
    except ImportError:  # run as a top-level script
        import code
        from acquire import acquire
    got = acquire(args.repos, seed=args.seed, cache_dir=args.cache, offline=args.offline,
                  pages=args.pages, max_files=args.max_files, max_file_bytes=args.max_file_bytes,
                  pause=args.pause, retries=args.retries)
    repos: Dict[str, List[Tuple[str, str]]] = {}
    per: List[dict] = []
    for repo in got:
        key = code.slug(repo.name)
        edges = [(f.subj, f.obj) for f in repo.facts]
        repos[key] = edges
        per.append({"repo": repo.name, "files": len(repo.files), "edges": len(edges)})
    meta = {"source": "github", "repos": len(repos), "per_repo": per}
    return repos, meta


def run(args) -> dict:
    repos, meta = load_repos(args)
    if not repos:
        return {"config": {"source": meta.get("source")}, "corpus": meta,
                "verdict": {"no_data": True}}

    names = sorted(repos)
    cut = max(1, min(len(names) - 1, int(round(len(names) * args.train_frac)))) if len(names) > 1 else len(names)
    train_names, held_names = names[:cut], names[cut:]

    def facts_of(keys) -> List[Atom]:
        return [A(s, o) for k in keys for s, o in repos[k]]

    train_facts_list = facts_of(train_names)
    all_facts_list = facts_of(names)
    train_facts = set(train_facts_list)
    all_facts = set(all_facts_list)
    train_pos = transitive(train_facts)
    held_pos = set()
    for k in held_names:
        held_pos |= transitive({A(s, o) for s, o in repos[k]})
    truth = transitive(all_facts)

    # negatives: within-repo non-edges among the train universe (bounded)
    negs: set = set()
    for k in train_names:
        ents = sorted({c for e in repos[k] for c in e})
        for a in ents:
            for b in ents:
                if a != b and A(a, b) not in truth:
                    negs.add(A(a, b))
    if len(negs) > args.max_neg:
        negs = set(sorted(negs, key=str)[: args.max_neg])

    t0 = time.time()
    res = learn(Ground(()), train_facts, train_pos, negs,
                max_body=args.max_body, extra_vars=1, max_rules=4)
    induce_s = time.time() - t0

    learned = closure(res.experience.to_kb(Ground(()).base(all_facts)))
    identity = set(all_facts)

    # scrambled control: permute constants per train repo, re-learn, re-test
    rng = random.Random(args.seed + 999983)
    sc_facts: set = set()
    for k in train_names:
        ents = sorted({c for e in repos[k] for c in e})
        perm = ents[:]
        rng.shuffle(perm)
        mp = dict(zip(ents, perm))
        sc_facts |= {A(mp[s], mp[o]) for s, o in repos[k]}
    sc_res = learn(Ground(()), sc_facts, transitive(sc_facts), negs,
                   max_body=args.max_body, extra_vars=1, max_rules=4)
    scrambled = closure(sc_res.experience.to_kb(Ground(()).base(all_facts)))

    def rec(closed) -> float:
        return len(closed & held_pos) / len(held_pos) if held_pos else 1.0

    out = {
        "config": {
            "repos": args.repos, "seed": args.seed, "offline": args.offline,
            "source": meta.get("source"), "synthetic": args.synthetic,
            "train_frac": args.train_frac, "max_neg": args.max_neg,
        },
        "corpus": meta,
        "graph": {
            "train_repos": len(train_names), "held_repos": len(held_names),
            "edges": len(all_facts), "train_edges": len(train_facts),
            "true_pairs": len(truth), "train_pairs": len(train_pos),
            "held_pairs": len(held_pos), "negatives": len(negs),
        },
        "arms": {
            "identity": {"held_recovery": round(rec(identity), 4),
                         "false": len(identity - truth)},
            "learned": {"held_recovery": round(rec(learned), 4),
                        "false": len(learned - truth)},
            "scrambled": {"held_recovery": round(rec(scrambled), 4),
                          "false": len(scrambled - truth)},
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
        "found_transitivity": any(r.count("imports") == 3 for r in out["learned_rules"]),
    }
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repos", type=int, default=4)
    p.add_argument("--per-repo", type=int, default=12, help="synthetic modules per repo")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--cache", default="experiments/code/cache")
    p.add_argument("--query", default=None)
    p.add_argument("--pages", type=int, default=3)
    p.add_argument("--max-files", type=int, default=250)
    p.add_argument("--max-file-bytes", type=int, default=300_000)
    p.add_argument("--train-frac", type=float, default=0.6)
    p.add_argument("--max-body", type=int, default=2)
    p.add_argument("--max-neg", type=int, default=4000)
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
    v = out.get("verdict", {})
    return 0 if v.get("found_transitivity") else 1


if __name__ == "__main__":
    sys.exit(main())