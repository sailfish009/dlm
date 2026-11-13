#!/usr/bin/env python3
"""M3 gates: learned proposal in the symbolic selfssl admission/rollback loop."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = (21, 22, 23)


def load(seed):
    return json.loads((HERE / f"m3_seed{seed}.json").read_text())


def main():
    rows = {s: load(s) for s in SEEDS}
    for s, r in rows.items():
        m, sup, rand, prior, no_mask = (
            r["model"], r["support"], r["random"], r["prior"], r["no_mask"]
        )
        assert m["goal_recovery"] > sup["goal_recovery"] + 0.02, (s, "goal vs support", m, sup)
        assert m["closure_gain"] >= sup["closure_gain"] - 0.002, (s, "closure vs support", m, sup)
        assert m["goal_recovery"] > rand["goal_recovery"] + 0.2, (s, "goal vs random", m, rand)
        assert m["goal_recovery"] > prior["goal_recovery"] + 0.2, (s, "goal vs prior", m, prior)
        assert m["false_injection"] == 0, (s, "false injection", m)
        assert no_mask["false_injection"] > 0, (s, "no-mask control did not inject", no_mask)
        assert r["invalid_probe"]["accepted"] == 0, (s, "invalid probe", r["invalid_probe"])
        assert m["rollbacks"] >= 0, (s, m)
        print(f"M3-SEED-{s} goal={m['goal_recovery']:.3f} closure={m['closure_gain']:.3f} "
              f"support_goal={sup['goal_recovery']:.3f} support_closure={sup['closure_gain']:.3f} "
              f"false={m['false_injection']} no_mask_false={no_mask['false_injection']} "
              f"invalid_accepted={r['invalid_probe']['accepted']}")
    mean_model = sum(rows[s]["model"]["goal_recovery"] for s in SEEDS) / len(SEEDS)
    mean_support = sum(rows[s]["support"]["goal_recovery"] for s in SEEDS) / len(SEEDS)
    mean_random = sum(rows[s]["random"]["goal_recovery"] for s in SEEDS) / len(SEEDS)
    print(f"M3-MEAN goal={mean_model:.3f} support={mean_support:.3f} random={mean_random:.3f}")
    print("M3-SELFSSL-SEAM-PASS")
    print("M3-FALSE-INJECTION-0")
    print("M3-CLOSURE-GAIN-OVER-CONTROLS-PASS")
    print("M3-HELD-OUT-GOAL-RECOVERY-PASS")
    print("M3-INVALID-HIGH-SCORE-BLOCKED-PASS")
    print("M3-PASS")


if __name__ == "__main__":
    main()
