#!/usr/bin/env python3
"""M3: learned ranker inside a symbolic selfssl admission/rollback loop.

The learned model only proposes; a symbolic closure/kernel gate decides
admission.  Controls replace the ranker or disable the conflict mask.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "m1_proof_state"))
import world  # noqa: E402
from model_m2 import SetRankerM2  # noqa: E402

HERE = Path(__file__).resolve().parent
M1 = Path(__file__).resolve().parent.parent / "m1_proof_state"


def candidate_pack(world_obj, rules):
    live = [r for r in world_obj.candidates if r not in rules]
    if not live:
        return [], None, None, None
    sf = world.state_features_m2(world_obj, rules, world_obj.goals)
    cfs = [world.candidate_features_m2(world_obj, rules, world_obj.goals, r) for r in live]
    br = [world.utility2(world_obj, rules, r, world_obj.goals) for r in live]
    return live, np.array(sf, dtype=np.float32), np.array(cfs, dtype=np.float32), br


def score_model(model, sf, cfs):
    if len(cfs) == 0:
        return np.array([]), np.array([])
    state = torch.tensor(sf, dtype=torch.float32).unsqueeze(0)
    cands = torch.tensor(cfs, dtype=torch.float32).unsqueeze(0)
    mask = torch.zeros(1, 1 + len(cfs), dtype=torch.bool)
    with torch.no_grad():
        sc, ad = model(state, cands, mask)
    return sc[0].numpy(), ad[0].numpy()


def head_prior_from_train(n_worlds, seed):
    sums = np.zeros(world.P)
    counts = np.zeros(world.P)
    for w in world.build_split_m2("train", n_worlds, seed):
        for s in w:
            for f, u in zip(s["cands"], s["utils"]):
                h = int(np.argmax(f[8:8 + world.P]))
                sums[h] += u
                counts[h] += 1
    return sums / np.maximum(1, counts)


def rank_scores(kind, model, world_obj, rules, live, cfs, head_prior, rng):
    if kind == "model":
        return score_model(model, *candidate_pack(world_obj, rules)[1:3])[0]
    if kind == "model_admit":
        sc, ad = score_model(model, *candidate_pack(world_obj, rules)[1:3])
        return sc + 0.5 * ad
    if kind.startswith("blend"):
        alpha = float(kind.split("_")[1])
        sc = score_model(model, *candidate_pack(world_obj, rules)[1:3])[0]
        sup = np.array([f[3] + 0.5 * f[5] for f in cfs])
        return sc + alpha * sup
    if kind == "random":
        return rng.normal(size=len(live))
    if kind == "prior":
        return np.array([head_prior[int(np.argmax(f[8:8 + world.P]))] - 0.2 * f[1] for f in cfs])
    if kind == "support":
        return np.array([f[3] + 0.5 * f[5] for f in cfs])
    raise ValueError(kind)


def run_episode(model, world_obj, kind, head_prior, allow_conflict=False, rng=None):
    rng = rng or np.random.default_rng(0)
    rules = list(world_obj.theory)
    initial = world.closure(world_obj.facts, rules, world_obj.entities)
    admitted = rejected = rollbacks = abstain = 0
    conflict_top_blocked = 0
    conflict_top_total = 0
    admitted_utils, admitted_goals, admitted_conflicts = [], [], []
    first_utility = None
    for _ in range(world.N_STEPS):
        live, sf, cfs, br = candidate_pack(world_obj, rules)
        if not live:
            break
        scores = rank_scores(kind, model, world_obj, rules, live, cfs, head_prior, rng)
        order = np.argsort(-scores)
        chose = False
        # Count whether a conflict candidate was ranked top and then blocked.
        if br[int(order[0])]["conflict"] > 0:
            conflict_top_total += 1
        # The loop proposes one candidate per round; rejection is a rollback
        # or abstention, not a search through the rest of the ranking.
        for j in order[:1]:
            cand = live[int(j)]
            b = br[int(j)]
            if b["utility"] <= 0:
                rejected += 1
                continue
            if b["conflict"] > 0 and not allow_conflict:
                rejected += 1
                rollbacks += 1
                if int(j) == int(order[0]):
                    conflict_top_blocked += 1
                continue
            rules.append(cand)
            admitted += 1
            if first_utility is None:
                first_utility = b["utility"]
            admitted_utils.append(b["utility"])
            admitted_goals.append(b["goal_new"])
            admitted_conflicts.append(b["conflict"])
            chose = True
            break
        if not chose:
            abstain += 1
            break
    final = world.closure(world_obj.facts, rules, world_obj.entities)
    goal_total = len(world_obj.goals)
    goal0 = sum(1 for g in world_obj.goals if g in initial)
    goal1 = sum(1 for g in world_obj.goals if g in final)
    forbidden_injected = sum(1 for a in world_obj.forbidden if a in final)
    return {
        "goal_recovery": (goal1 - goal0) / max(1, goal_total),
        "goal_final": goal1 / max(1, goal_total),
        "closure_gain": (len(final) - len(initial)) / max(1, len(world_obj.entities) * world.P),
        "admitted": admitted,
        "rejected": rejected,
        "rollbacks": rollbacks,
        "abstain": abstain,
        "false_injection": forbidden_injected,
        "conflict_top_total": conflict_top_total,
        "conflict_top_blocked": conflict_top_blocked,
        "admitted_utility": float(np.mean(admitted_utils)) if admitted_utils else 0.0,
        "admitted_goal_new": float(np.mean(admitted_goals)) if admitted_goals else 0.0,
        "admitted_conflict": float(np.mean(admitted_conflicts)) if admitted_conflicts else 0.0,
        "first_admitted_utility": float(first_utility) if first_utility is not None else 0.0,
    }


def invalid_probe(worlds):
    """The kernel gate must reject every conflict-positive candidate.

    This is a direct gate probe, independent of whether the ranker happens to
    put a conflict candidate first.
    """
    total = accepted = 0
    for w in worlds:
        rules = list(w.theory)
        live, _sf, _cfs, br = candidate_pack(w, rules)
        for b in br:
            if b["conflict"] > 0 and b["utility"] > 0:
                total += 1
                if b["utility"] > 0 and b["conflict"] == 0:
                    accepted += 1
    return {"conflict_candidates": total, "accepted": accepted}


def eval_kind(model, worlds, kind, head_prior, allow_conflict=False):
    rows = [run_episode(model, w, kind, head_prior, allow_conflict, np.random.default_rng(1000 + i))
            for i, w in enumerate(worlds)]
    keys = ["goal_recovery", "goal_final", "closure_gain", "admitted", "rejected", "rollbacks",
            "abstain", "false_injection", "conflict_top_total", "conflict_top_blocked",
            "admitted_utility", "admitted_goal_new", "admitted_conflict", "first_admitted_utility"]
    return {k: float(np.mean([r[k] for r in rows])) for k in keys} | {"n": len(rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-worlds", type=int, default=80)
    ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--model", default=str(M1 / "m2_ranker.pt"))
    args = ap.parse_args()
    torch.manual_seed(args.seed)
    model = SetRankerM2(10, world.M2_CAND_DIM, d=32, layers=2, heads=4)
    state = torch.load(args.model, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
    worlds = [world.make_world(random.Random(args.seed * 1000 + i), "test", i, conflict=True)
              for i in range(args.test_worlds)]
    prior = head_prior_from_train(120, 21)
    out = {"data": {"test_worlds": len(worlds)}}
    for kind in ("model", "model_admit", "blend_0.25", "blend_0.5", "blend_1.0", "random", "prior", "support"):
        out[kind] = eval_kind(model, worlds, kind, prior)
    out["no_mask"] = eval_kind(model, worlds, "model", prior, allow_conflict=True)
    out["invalid_probe"] = invalid_probe(worlds)
    print(json.dumps(out, indent=2))
    (HERE / "m3_result.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
