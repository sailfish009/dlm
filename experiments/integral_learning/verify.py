#!/usr/bin/env python3
"""Direction-aware verification for the integral-learning lab. Every PASS line
is backed by a computed assertion. Scientific findings (integral vs gradient,
integral vs single) are REPORTED with numbers, not gated into a desired answer.

Gates (harness validity):
  E1 apparatus control: goal/atom/util credit integrable + potential identity.
  E2 discriminative: integral success beats scramble AND permute on every seed
     (proves the credit content is doing work — the 0223 PERMUTE confound is
     fixed only if permute degrades).
  E2 soundness: false_assert == 0 (kernel gate invariant).
  Determinism: E2 seed 777 re-run byte-identical.

Findings (reported):
  E1 structure/order integrability split.
  E2 integral vs gradient success; integral vs single (accumulation value).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEEDS = (777, 778, 779)
ARMS = ("integral", "single", "scramble", "permute", "random", "prior", "gradient")


def main():
    # ---- E1 ----
    e1 = json.loads((HERE / "integrability.json").read_text())
    assert e1["apparatus_control_pass"], "E1 apparatus control failed"
    assert e1["structure_integrable"], "structure credit not integrable"
    assert e1["max_potential_identity_error"] < 1e-9
    print(f"E1-APPARATUS pass ({e1['potential_identity_checks']} potential-identity checks, "
          f"err {e1['max_potential_identity_error']:.2e})")
    print(f"E1-STRUCTURE integrable (goal/atom/util curl==0); "
          f"E1-ORDER depth integrable={e1['order_integrable']} "
          f"({e1['credits']['depth']['nonzero_curl']}/{e1['n_plaquettes']} plaquettes curl!=0, "
          f"max {e1['credits']['depth']['max_abs_curl']:.4f})")

    # ---- E2 ----
    rows = {s: json.loads((HERE / f"integral_seed{s}.json").read_text()) for s in SEEDS}
    for s, r in rows.items():
        assert r["integral"]["success_rate"] > r["scramble"]["success_rate"] + 0.3, (s, "scramble")
        assert r["integral"]["success_rate"] > r["permute"]["success_rate"] + 0.3, (s, "permute")
        for arm in ARMS:
            assert r[arm]["false_assert"] == 0.0, (s, arm, "false assertion")
    print("E2-DISCRIMINATIVE pass: integral > scramble+0.3 AND > permute+0.3 on all 3 seeds "
          "(credit content proven; 0223 PERMUTE confound fixed)")
    print("E2-SOUNDNESS pass: false_assert == 0 all arms/seeds (kernel gate)")

    mean = {arm: float(np.mean([rows[s][arm]["success_rate"] for s in SEEDS])) for arm in ARMS}
    cov = {arm: float(np.mean([rows[s][arm]["coverage"] for s in SEEDS])) for arm in ARMS}
    kev = {arm: float(np.mean([rows[s][arm]["kernel_evals"] for s in SEEDS])) for arm in ARMS}
    print("E2 SUCCESS-RATE TABLE (3 seeds)")
    for arm in ARMS:
        per = [round(rows[s][arm]["success_rate"], 3) for s in SEEDS]
        print(f"  {arm:9s} mean={mean[arm]:.3f} seeds={per} coverage={cov[arm]:.3f} kevals={kev[arm]:.1f}")

    # Findings (reported, not gated):
    ig = mean["integral"] - mean["gradient"]
    print(f"E2-FINDING integral vs gradient: success {mean['integral']:.3f} vs {mean['gradient']:.3f} "
          f"(delta {ig:+.3f}); integral needs no training phase, {kev['integral']:.0f} online kernel evals/world "
          f"vs gradient {kev['gradient']:.1f} + {rows[777]['gradient_train_steps']} training steps")
    si = mean["single"] - mean["integral"]
    verdict = "accumulation adds no value (single >= integral)" if si >= -0.02 else "accumulation helps"
    print(f"E2-FINDING integral vs single: success {mean['integral']:.3f} vs {mean['single']:.3f} "
          f"(single-integral {si:+.3f}) -> {verdict}; exact integrable credit is a potential "
          f"difference, so greedy ascent on current credit is already optimal")

    # ---- determinism ----
    assert "DETERMINISTIC yes" in (HERE / "repeat.out").read_text()
    print("DETERMINISM E2 seed777 re-run byte-identical")

    summary = {"e1": {"structure_integrable": e1["structure_integrable"],
                      "order_integrable": e1["order_integrable"],
                      "depth_nonzero_frac": e1["credits"]["depth"]["frac_nonzero"]},
               "e2_mean_success": mean, "e2_mean_coverage": cov, "e2_mean_kernel_evals": kev,
               "integral_minus_gradient": ig, "single_minus_integral": si}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("V0241-INTEGRAL-LEARNING-PASS")


if __name__ == "__main__":
    main()