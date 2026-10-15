"""Recursive self-supervised learning experiment (v0.0055).

The model is given a directed graph as ``edge`` facts and NOT the relational
transitive rule.  It bootstraps reachability by RECURSION: each round closes its
current relation under the two definitional level rules and reifies the
certified extension, feeding its own output back as the next round's only input
(``dlm.recursive``).  The kernel is the sole judge; there are no labels.

Falsifiers (verdict dict, all must hold):
  sound                  every derived pair is a true reachable pair
  complete               the fixpoint equals the full transitive closure
  recursion_grows        >1 round, a later round still adds pairs
  fixpoint_reached       a round adds nothing and the loop stops
  one_shot_insufficient  a single composition does NOT reach the closure
  sublinear_depth        depth <= ceil(log2 diameter) + 2 (not linear)
  deterministic          two runs are identical

Writes reports/recursive/<stamp>/result.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import deque

from dlm.recursive import one_shot, reachability, recurse


def make_chain(n: int = 24):
    return [(f"n{i}", f"n{i + 1}") for i in range(n)]


def make_dag(n: int = 16, seed: int = 7):
    """Deterministic pseudo-random DAG plus a spanning chain (connected)."""
    edges = []
    x = seed
    for i in range(n):
        for j in range(i + 1, n):
            x = (1103515245 * x + 12345) % (2 ** 31)
            if x % 100 < 25:
                edges.append((f"v{i}", f"v{j}"))
    edges += [(f"v{i}", f"v{i + 1}") for i in range(n - 1)]
    return sorted(set(edges))


def diameter(edges):
    """Longest shortest path over the graph (0 if trivial)."""
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
    nodes = sorted({x for e in edges for x in e})
    best = 0
    for s in nodes:
        dist = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for w in adj.get(u, ()):
                if w not in dist:
                    dist[w] = dist[u] + 1
                    best = max(best, dist[w])
                    q.append(w)
    return best


def run(edges, *, name: str = "graph") -> dict:
    truth = reachability(edges)
    r = recurse(edges)
    one = one_shot(edges)
    diam = diameter(edges)
    bound = (math.ceil(math.log2(diam)) + 2) if diam > 1 else 2
    rel = r.relation
    rounds = [rd.to_dict() for rd in r.rounds]
    later_growth = any(rd["new"] > 0 for rd in rounds[1:])
    verdicts = {
        "sound": rel <= truth,
        "complete": rel == truth,
        "recursion_grows": r.depth > 1 and later_growth,
        "fixpoint_reached": bool(r.fixed),
        "one_shot_insufficient": one != truth,
        "sublinear_depth": r.depth <= bound,
        "deterministic": recurse(edges).to_dict() == r.to_dict(),
    }
    return {
        "name": name,
        "nodes": len({x for e in edges for x in e}),
        "edges": len(edges),
        "diameter": diam,
        "depth_bound": bound,
        "truth_pairs": len(truth),
        "derived_pairs": len(rel),
        "one_shot_pairs": len(one),
        "false_pairs": len(rel - truth),
        "rounds": rounds,
        "verdict": verdicts,
        "verdict_ok": all(verdicts.values()),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="recursive self-supervised learning")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(__file__), "..", "..", "reports", "recursive"))
    ap.add_argument("--json", default="")
    ap.add_argument("--offline", action="store_true", help="accepted for harness parity (no network is used)")
    args = ap.parse_args(argv)

    results = [run(make_chain(24), name="chain24"),
               run(make_dag(16), name="dag16")]
    ok = all(x["verdict_ok"] for x in results)
    out = {"version": "0.0.55", "results": results, "all_ok": ok}

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    path = os.path.abspath(args.json) if args.json else os.path.join(out_dir, "result.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    for x in results:
        print(f"[{x['name']}] nodes={x['nodes']} edges={x['edges']} "
              f"diameter={x['diameter']} -> derived {x['derived_pairs']}/"
              f"{x['truth_pairs']} pairs, false={x['false_pairs']} "
              f"depth={len(x['rounds'])} bound={x['depth_bound']} "
              f"one_shot={x['one_shot_pairs']}")
        for rd in x["rounds"]:
            print(f"    round {rd['level']} {rd['pred']}: size={rd['size']} "
                  f"new={rd['new']}")
        print(f"    verdict: {x['verdict']}")
    print(f"recursive self-supervised learning: {'PASS' if ok else 'FAIL'}")
    print(f"report: {path}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())