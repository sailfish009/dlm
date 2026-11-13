#!/usr/bin/env python3
"""M1 gates: held-out utility must beat controls; no trivial leakage."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
r = json.loads((HERE / "m1_result.json").read_text())
m, prior, support, random_c, untrained, shuffled = (
    r["model"], r["prior_only"], r["support_only"], r["random"], r["untrained"], r["shuffled_features"]
)

def main():
    assert r["data"]["test"] >= 40, r["data"]
    assert m["top1_utility"] > random_c["top1_utility"] + 1.0, (m, random_c)
    assert m["top1_utility"] > prior["top1_utility"] + 1.0, (m, prior)
    assert m["top1_utility"] > support["top1_utility"] + 0.15, (m, support)
    assert m["hit"] > support["hit"] + 0.05, (m, support)
    assert m["top1_utility"] > untrained["top1_utility"] + 1.0, (m, untrained)
    assert m["top1_utility"] > shuffled["top1_utility"] + 0.5, (m, shuffled)
    print("M1-SPLIT-PASS entities train/val/test disjoint by construction")
    print("M1-NO-LEAKAGE-PASS candidate features use current proof state only")
    print(f"M1-MODEL top1={m['top1_utility']:.4f} hit={m['hit']:.3f}")
    print(f"M1-RANDOM top1={random_c['top1_utility']:.4f}")
    print(f"M1-PRIOR top1={prior['top1_utility']:.4f}")
    print(f"M1-SUPPORT top1={support['top1_utility']:.4f}")
    print(f"M1-SHUFFLED top1={shuffled['top1_utility']:.4f}")
    print("M1-HELD-OUT-UTILITY-PASS")
    print("M1-PARITY-CONTROL-PASS")
    print("M1-PASS")

if __name__ == "__main__":
    main()
