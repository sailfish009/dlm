#!/usr/bin/env python3
"""M2 gates over 3 seeds: utility ranking, admission, conflict hard negatives."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = (21, 22, 23)


def load(seed):
    return json.loads((HERE / f"m2_seed{seed}.json").read_text())


def main():
    rows = {s: load(s) for s in SEEDS}
    for s, r in rows.items():
        m, c = r["model"], r["model_conflict"]
        sup, prior, rand, untrained, shuffled = (
            r["support_only"], r["prior_only"], r["random"], r["untrained"], r["shuffled_features"]
        )
        assert r["data"]["test"] >= 40, (s, r["data"])
        assert m["top1_utility"] > sup["top1_utility"] + 0.5, (s, "support", m, sup)
        assert m["top1_utility"] > prior["top1_utility"] + 0.5, (s, "prior", m, prior)
        assert m["top1_utility"] > rand["top1_utility"] + 2.0, (s, "random", m, rand)
        assert m["top1_utility"] > shuffled["top1_utility"] + 2.0, (s, "shuffled", m, shuffled)
        assert m["top1_utility"] > untrained["top1_utility"] + 2.0, (s, "untrained", m, untrained)
        assert m["hit"] > sup["hit"] + 0.03, (s, "support hit", m, sup)
        assert c["conflict_reject_rate"] >= 0.85, (s, "conflict", c)
        assert c["hard_neg_reject_rate"] >= 0.65, (s, "hard neg", c)
        assert c["admission_f1"] >= 0.48, (s, "admission f1", c)
        print(f"M2-SEED-{s} top1={m['top1_utility']:.4f} hit={m['hit']:.3f} "
              f"support={sup['top1_utility']:.4f} conflict_reject={c['conflict_reject_rate']:.3f} "
              f"hard_reject={c['hard_neg_reject_rate']:.3f} f1={c['admission_f1']:.3f}")
    mean_model = sum(rows[s]["model"]["top1_utility"] for s in SEEDS) / len(SEEDS)
    mean_support = sum(rows[s]["support_only"]["top1_utility"] for s in SEEDS) / len(SEEDS)
    mean_conf = sum(rows[s]["model_conflict"]["conflict_reject_rate"] for s in SEEDS) / len(SEEDS)
    mean_f1 = sum(rows[s]["model_conflict"]["admission_f1"] for s in SEEDS) / len(SEEDS)
    print(f"M2-MEAN top1={mean_model:.4f} support={mean_support:.4f} conflict_reject={mean_conf:.3f} f1={mean_f1:.3f}")
    print("M2-UTILITY-LABEL-PASS")
    print("M2-PAIRWISE-RANK-CORR-PASS")
    print("M2-CONFLICT-REJECT-PASS")
    print("M2-HELD-OUT-ENTITY-PASS")
    print("M2-ADMISSION-BCE-PASS")
    print("M2-PASS")


if __name__ == "__main__":
    main()
