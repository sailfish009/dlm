#!/usr/bin/env python3
"""M5 gates: constrained proposal, kernel reward, false-rule rate, held-out rules."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = (31, 32, 33)


def main():
    rows = {s: json.loads((HERE / f"m5_seed{s}.json").read_text()) for s in SEEDS}
    for s, r in rows.items():
        c, k, p, rv, ru = (r["constrained"], r["kernel"], r["prior"], r["random_valid"], r["random_unconstrained"])
        assert r["split"]["heldout_rules"] == 20, (s, r["split"])
        assert c["false_rule_rate"] == 0.0, (s, c)
        assert ru["false_rule_rate"] > 0.0, (s, ru)
        assert c["recovery_rate"] > p["recovery_rate"] + 0.3, (s, "prior", c, p)
        assert c["recovery_rate"] > rv["recovery_rate"] + 0.2, (s, "random valid", c, rv)
        assert k["recovery_rate"] > p["recovery_rate"], (s, "kernel", k, p)
        print(f"M5-SEED-{s} constrained={c['recovery_rate']:.3f} kernel={k['recovery_rate']:.3f} "
              f"prior={p['recovery_rate']:.3f} random_valid={rv['recovery_rate']:.3f} "
              f"false_constrained={c['false_rule_rate']:.3f} false_unconstrained={ru['false_rule_rate']:.3f}")
    mean_c = sum(rows[s]["constrained"]["recovery_rate"] for s in SEEDS) / len(SEEDS)
    mean_p = sum(rows[s]["prior"]["recovery_rate"] for s in SEEDS) / len(SEEDS)
    print(f"M5-MEAN constrained={mean_c:.3f} prior={mean_p:.3f}")
    print("M5-CONSTRAINED-DECODE-PASS")
    print("M5-KERNEL-REWARD-PASS")
    print("M5-FALSE-RULE-RATE-PASS")
    print("M5-HELD-OUT-RULE-PASS")
    print("M5-PASS")


if __name__ == "__main__":
    main()
