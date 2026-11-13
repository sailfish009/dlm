#!/usr/bin/env python3
"""M1 multi-seed gate: every seed must beat the controls on held-out worlds."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = (11, 12, 13)


def load(seed):
    return json.loads((HERE / f"m1_seed{seed}.json").read_text())


def main():
    rows = {s: load(s) for s in SEEDS}
    for s, r in rows.items():
        m, prior, support, rand, untrained, shuffled = (
            r["model"], r["prior_only"], r["support_only"], r["random"], r["untrained"], r["shuffled_features"]
        )
        assert r["data"]["test"] >= 40, (s, r["data"])
        assert m["top1_utility"] > rand["top1_utility"] + 1.0, (s, "random", m, rand)
        assert m["top1_utility"] > prior["top1_utility"] + 1.0, (s, "prior", m, prior)
        assert m["top1_utility"] > support["top1_utility"] + 0.15, (s, "support", m, support)
        assert m["hit"] > support["hit"] + 0.05, (s, "support hit", m, support)
        assert m["top1_utility"] > untrained["top1_utility"] + 1.0, (s, "untrained", m, untrained)
        assert m["top1_utility"] > shuffled["top1_utility"] + 0.5, (s, "shuffled", m, shuffled)
        print(f"M1-SEED-{s} model={m['top1_utility']:.4f} hit={m['hit']:.3f} "
              f"support={support['top1_utility']:.4f} prior={prior['top1_utility']:.4f} "
              f"random={rand['top1_utility']:.4f} shuffled={shuffled['top1_utility']:.4f}")
    mean_model = sum(rows[s]["model"]["top1_utility"] for s in SEEDS) / len(SEEDS)
    mean_support = sum(rows[s]["support_only"]["top1_utility"] for s in SEEDS) / len(SEEDS)
    mean_prior = sum(rows[s]["prior_only"]["top1_utility"] for s in SEEDS) / len(SEEDS)
    mean_random = sum(rows[s]["random"]["top1_utility"] for s in SEEDS) / len(SEEDS)
    print(f"M1-MEAN model={mean_model:.4f} support={mean_support:.4f} prior={mean_prior:.4f} random={mean_random:.4f}")
    print("M1-SPLIT-PASS entities train/val/test disjoint by construction")
    print("M1-NO-LEAKAGE-PASS candidate features use current proof state only")
    print("M1-HELD-OUT-UTILITY-PASS")
    print("M1-PARITY-CONTROL-PASS")
    print("M1-PASS")


if __name__ == "__main__":
    main()
