#!/usr/bin/env python3
"""E1 — credit-field integrability (the foundational precondition).

NOTE 87 (integrate.py) claims deduction learns by integration: accumulate exact
per-clause credit over rounds ("gradient flow without a gradient"). For that
picture to define a SINGLE objective, the credit field must be integrable: there
must exist a scalar potential F(theory) with credit(T, r) = F(T+r) - F(T). On a
discrete theory space the obstruction is the plaquette curl (discrete curvature
/ holonomy):

    curl_c(T, r1, r2) = [c(T,r1) + c(T+r1,r2)] - [c(T,r2) + c(T+r2,r1)]

If curl != 0 the credit is path-dependent (order matters) and no single potential
exists. We measure curl for four exact-credit signals and split:

  STRUCTURE (potential expected): goal gain, closure gain, MDL utility.
  ORDER     (path dependence expected): depth-weighted proof credit, because
            alternative proof paths of different length give different credit
            for the same final closure.

Scalar-objective control: goal/atom/util credit MUST have curl == 0 and MUST
equal an explicit potential difference; this validates the apparatus. The
depth-credit curl is the finding, not a gate.

Self-contained; world.py is a frozen copy of structure_discovery/world.py
(M1 propositional Horn worlds). Credit definitions follow NOTE 87.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np

import world

HERE = Path(__file__).resolve().parent


def closure_with_depth(facts, rules, entities):
    """Forward integral with shortest-proof depth. Facts depth 0; a derived
    atom gets 1 + max(body depths) at its first (shortest) derivation."""
    depth = {a: 0 for a, v in facts.items() if v}
    changed = True
    while changed:
        changed = False
        for r in rules:
            if not r.body:
                continue
            for e in entities:
                if all((p, e) in depth for p in r.body):
                    a = (r.head, e)
                    d = 1 + max(depth[(p, e)] for p in r.body)
                    if a not in depth:
                        depth[a] = d
                        changed = True
    return depth


def credit(kind, w, T, r):
    """Exact credit for adding rule r to theory T (kernel-decided)."""
    ents = w.entities
    before = closure_with_depth(w.facts, T, ents)
    after = closure_with_depth(w.facts, list(T) + [r], ents)
    new_goals = [g for g in w.goals if g in after and g not in before]
    if kind == "goal":
        return float(len(new_goals))
    if kind == "atom":
        return float(len(after) - len(before))
    if kind == "util":
        return float(len(new_goals)) - r.cost
    if kind == "depth":
        return float(sum(1.0 / (1.0 + after[g]) for g in new_goals))
    raise ValueError(kind)


def potential(kind, w, T):
    """Explicit scalar potential F(T) for the integrable credits."""
    ents = w.entities
    cl = closure_with_depth(w.facts, T, ents)
    if kind == "goal":
        return float(sum(1 for g in w.goals if g in cl))
    if kind == "atom":
        return float(len(cl))
    if kind == "util":
        return float(sum(1 for g in w.goals if g in cl)) - sum(r.cost for r in T)
    raise ValueError(kind)


def plaquette_curl(kind, w, T, r1, r2):
    a = credit(kind, w, T, r1) + credit(kind, w, list(T) + [r1], r2)
    b = credit(kind, w, T, r2) + credit(kind, w, list(T) + [r2], r1)
    return a - b


def main():
    rng = random.Random(20241)
    kinds = ("goal", "atom", "util", "depth")
    curls = {k: [] for k in kinds}
    pot_err = {k: 0.0 for k in ("goal", "atom", "util")}
    pot_n = 0
    depth_example = None
    n_plaq = 0

    for wi in range(60):
        w = world.make_world(rng, "test", wi)
        pool = w.candidates
        for _ in range(40):
            T = list(w.theory)
            # random base theory: seed + a few admitted candidates
            extra = rng.sample(pool, rng.randint(0, 3))
            T = T + extra
            avail = [r for r in pool if r not in T]
            if len(avail) < 2:
                continue
            r1, r2 = rng.sample(avail, 2)
            n_plaq += 1
            for k in kinds:
                c = plaquette_curl(k, w, T, r1, r2)
                curls[k].append(c)
                if k == "depth" and abs(c) > 1e-9 and depth_example is None:
                    depth_example = {
                        "world": wi, "curl": c,
                        "r1": [r1.head, list(r1.body)], "r2": [r2.head, list(r2.body)],
                        "c_T_r1": credit("depth", w, T, r1),
                        "c_T_r2": credit("depth", w, T, r2),
                    }
            # scalar-potential identity check on the marginals
            for k in ("goal", "atom", "util"):
                for r in (r1, r2):
                    lhs = credit(k, w, T, r)
                    rhs = potential(k, w, list(T) + [r]) - potential(k, w, T)
                    pot_err[k] = max(pot_err[k], abs(lhs - rhs))
                    pot_n += 1

    stats = {}
    for k in kinds:
        arr = np.array(curls[k])
        nz = int(np.sum(np.abs(arr) > 1e-9))
        stats[k] = {
            "n": len(arr),
            "nonzero_curl": nz,
            "frac_nonzero": nz / max(1, len(arr)),
            "max_abs_curl": float(np.max(np.abs(arr))) if len(arr) else 0.0,
            "mean_abs_curl": float(np.mean(np.abs(arr))) if len(arr) else 0.0,
            "integrable": nz == 0,
        }

    apparatus_ok = (stats["goal"]["integrable"] and stats["atom"]["integrable"]
                    and stats["util"]["integrable"]
                    and max(pot_err.values()) < 1e-9)
    out = {
        "n_plaquettes": n_plaq,
        "potential_identity_checks": pot_n,
        "max_potential_identity_error": max(pot_err.values()),
        "apparatus_control_pass": bool(apparatus_ok),
        "credits": stats,
        "depth_curl_example": depth_example,
        "structure_integrable": stats["goal"]["integrable"] and stats["util"]["integrable"],
        "order_integrable": stats["depth"]["integrable"],
    }
    assert apparatus_ok, ("apparatus control failed", pot_err, stats)
    (HERE / "integrability.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    print(f"E1-APPARATUS-CONTROL pass (goal/atom/util curl==0, potential identity err<1e-9, {pot_n} checks)")
    print(f"E1-STRUCTURE integrable: goal/util/atom credit admit a scalar potential (curl==0)")
    if stats["depth"]["integrable"]:
        print("E1-ORDER depth credit integrable (no path dependence detected)")
    else:
        print(f"E1-ORDER depth credit NON-integrable: {stats['depth']['nonzero_curl']}/{n_plaq} plaquettes curl!=0 "
              f"(max {stats['depth']['max_abs_curl']:.4f}) — proof-order carries curvature")
    print("E1-INTEGRABILITY-DONE")


if __name__ == "__main__":
    main()