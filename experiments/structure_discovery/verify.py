#!/usr/bin/env python3
"""Direction-aware verification. Every PASS line is backed by a computed
assertion; the direction table is the scientific result, not a gate —
'differs from baseline' is never required (0229 lesson: difference-only
gates pass on degradation).

Pre-registered effect rule (README): a variant shows a consistent effect iff
all 3 seed deltas share a sign AND |mean delta| >= 0.2 utility. Otherwise:
no consistent effect. A2 (PE) is a null control.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VARIANTS = ("base", "a1_cross", "a2_pe", "a3_tied2", "a3_indep1")
SEEDS = (11, 12, 13)
M1_KEYS = ("model", "prior_only", "support_only", "random", "untrained", "shuffled_features")


def load(v, s):
    return json.loads((HERE / f"sd_{v}_seed{s}.json").read_text())


def main():
    q = json.loads((HERE / "qualify.json").read_text())
    assert q["disjoint_splits"]
    assert q["margin_ceiling_support"] >= 0.5
    assert q["margin_ceiling_prior"] >= 1.0
    assert q["margin_support_random"] >= 0.5
    print(f"P0 ceiling={q['ceiling']:.4f} support={q['support']:.4f} "
          f"prior={q['prior']:.4f} random={q['random']:.4f}")

    rows = {(v, s): load(v, s) for v in VARIANTS for s in SEEDS}

    # 1. base parity with the frozen M1 reference (harness drift control).
    ref = json.loads((HERE / "reference_m1_seed11.json").read_text())
    b11 = rows[("base", 11)]
    assert b11["data"] == ref["data"], (b11["data"], ref["data"])
    for k in M1_KEYS:
        for kk, vv in ref[k].items():
            assert abs(b11[k][kk] - vv) < 1e-6, (k, kk, b11[k][kk], vv)
    print(f"BASE-PARITY seed11 top1={b11['model']['top1_utility']:.4f} == frozen M1 reference (abs<1e-6)")

    # 2. base beats controls per seed (M1 margins) + 3. learning moves metric.
    for s in SEEDS:
        r = rows[("base", s)]
        m = r["model"]
        assert m["top1_utility"] > r["random"]["top1_utility"] + 1.0, (s, "random")
        assert m["top1_utility"] > r["prior_only"]["top1_utility"] + 1.0, (s, "prior")
        assert m["top1_utility"] > r["support_only"]["top1_utility"] + 0.15, (s, "support")
        assert m["hit"] > r["support_only"]["hit"] + 0.05, (s, "support hit")
        assert m["top1_utility"] > r["untrained"]["top1_utility"] + 1.0, (s, "untrained")
        assert m["top1_utility"] > r["shuffled_features"]["top1_utility"] + 0.5, (s, "shuffled")
        c = r["curve"]
        assert c[0]["epoch"] == -1
        assert c[-1]["val_top1"] - c[0]["val_top1"] >= 0.5, (s, c[0], c[-1])
    print("BASE-CONTROLS + LEARNING-MOVES pass (3 seeds, computed margins)")

    # 4. parameter accounting (matched-capacity controls).
    pc = {v: rows[(v, 11)]["config"]["param_count"] for v in VARIANTS}
    assert pc["a1_cross"] == pc["base"]
    assert pc["a2_pe"] == pc["base"] + 65 * 32
    assert pc["a3_tied2"] == pc["a3_indep1"]
    assert pc["a3_tied2"] < pc["base"]
    print("PARAMS", json.dumps(pc))

    # 5. determinism marker from repeat_check.sh.
    assert "DETERMINISTIC yes" in (HERE / "repeat.out").read_text()
    print("DETERMINISM base seed11 retrain byte-identical")

    # 6. direction table — computed result, pre-registered classification.
    print("AXIS DIRECTION TABLE (test top1 utility; delta vs base, same seed)")
    summary = {}
    for v in VARIANTS[1:]:
        deltas = [rows[(v, s)]["model"]["top1_utility"] - rows[("base", s)]["model"]["top1_utility"]
                  for s in SEEDS]
        early = []
        for s in SEEDS:
            cv = next(p["val_top1"] for p in rows[(v, s)]["curve"] if p["epoch"] == 30)
            cb = next(p["val_top1"] for p in rows[("base", s)]["curve"] if p["epoch"] == 30)
            early.append(cv - cb)
        mean = float(np.mean(deltas))
        sd = float(np.std(deltas))
        signs = {1 if d > 0 else (-1 if d < 0 else 0) for d in deltas}
        consistent = len(signs) == 1 and abs(mean) >= 0.2
        cls = ("consistent-positive" if mean > 0 else "consistent-negative") if consistent else "no-consistent-effect"
        summary[v] = {"deltas": deltas, "mean": mean, "sd": sd,
                      "early_ep30_deltas": early, "class": cls}
        print(f"{v}: deltas={[round(d, 4) for d in deltas]} mean={mean:.4f} sd={sd:.4f} "
              f"ep30={[round(e, 4) for e in early]} -> {cls}")
    (HERE / "direction_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("V0239-STRUCTURE-DISCOVERY-PASS")


if __name__ == "__main__":
    main()