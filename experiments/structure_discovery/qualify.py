#!/usr/bin/env python3
"""P0 fixture qualification: the task must have headroom above heuristics.

A structure-discovery fixture is qualified only if (computed, not asserted by
fiat): entity splits are disjoint, the oracle ceiling sits well above the
support heuristic and the learned prior, and the heuristic beats random.
On the prior-saturated MNIST fixture these margins collapse — that is why
this lab runs on proof-state worlds instead.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

import world

HERE = Path(__file__).resolve().parent


def main():
    ents = world.ENTITIES
    disjoint = (set(ents["train"]).isdisjoint(ents["val"])
                and set(ents["train"]).isdisjoint(ents["test"])
                and set(ents["val"]).isdisjoint(ents["test"]))

    rng = random.Random(999)
    worlds = [world.make_world(rng, "test", i) for i in range(80)]
    steps = [s for w in worlds for s in world.make_steps(w, rng)]

    ceiling = float(np.mean([max(s["utils"]) for s in steps]))
    sup, rand, pri = [], [], []
    rr = np.random.default_rng(7)
    tr = [s for w in world.build_split("train", 120, 999) for s in w]
    sums = np.zeros(world.P)
    counts = np.zeros(world.P)
    for s in tr:
        for f, u in zip(s["cands"], s["utils"]):
            h = int(np.argmax(f[8:8 + world.P]))
            sums[h] += u
            counts[h] += 1
    hp = sums / np.maximum(1, counts)
    for s in steps:
        f = np.array([c[3] + 0.5 * c[5] for c in s["cands"]])
        sup.append(s["utils"][int(np.argmax(f))])
        rand.append(s["utils"][int(rr.integers(len(s["cands"])))])
        sc = [hp[int(np.argmax(c[8:8 + world.P]))] - 0.2 * c[1] for c in s["cands"]]
        pri.append(s["utils"][int(np.argmax(sc))])

    out = {
        "n_steps": len(steps),
        "disjoint_splits": bool(disjoint),
        "ceiling": ceiling,
        "support": float(np.mean(sup)),
        "prior": float(np.mean(pri)),
        "random": float(np.mean(rand)),
        "margin_ceiling_support": ceiling - float(np.mean(sup)),
        "margin_ceiling_prior": ceiling - float(np.mean(pri)),
        "margin_support_random": float(np.mean(sup)) - float(np.mean(rand)),
    }
    assert disjoint, "entity splits overlap"
    assert out["margin_ceiling_support"] >= 0.5, out
    assert out["margin_ceiling_prior"] >= 1.0, out
    assert out["margin_support_random"] >= 0.5, out
    (HERE / "qualify.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    print("P0-FIXTURE-QUALIFIED (computed margins)")


if __name__ == "__main__":
    main()