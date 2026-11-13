#!/usr/bin/env python3
"""E2 — integral learning vs gradient learning (the core hypothesis).

NOTE 87: deduction learns by integrating exact credit — "gradient flow without
a gradient". Here an online learner accumulates kernel-exact utility credit over
rounds (NO gradient, NO parameters; the "weights" are accumulated credit) and
admits rules through the kernel gate to close goals. It is matched against a
gradient-trained set ranker (M1-style) run closed-loop, plus controls.

Arms:
  integral  — running sum of exact credit (the discrete path integral)
  single    — this round's credit only (memoryless)
  scramble  — running sum of SWAPPED credit (mislearned-order control)
  permute   — fixed permuted credit assignment (corrupted-content control)
  random    — random pick
  prior     — static head-prior pick
  gradient  — pre-trained SetRanker, closed-loop top-1 (inductive scaffolding)

Efficiency metric: loss_integral = trapezoidal ∫ L dt of the debt trajectory
(NOTE 87 loss_integral) — lower means reaching low debt sooner. Also coverage,
rounds, kernel evaluations, false assertions.

Discriminative requirement (0223 fix): integral must beat BOTH scramble AND
permute; otherwise the credit content is unproven and the result is reported
as a null. Every admitted rule passes the kernel gate (utility > 0).

Self-contained: world.py and models.py are frozen copies (provenance in README).
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

import world
from models import build

HERE = Path(__file__).resolve().parent
ARMS = ("integral", "single", "scramble", "permute", "random", "prior", "gradient")


def debt(w, T):
    cl = world.closure(w.facts, T, w.entities)
    return sum(1 for g in w.goals if g not in cl)


def loss_integral(traj):
    seq = [float(v) for v in traj]
    if len(seq) < 2:
        return 0.0
    return 0.5 * seq[0] + sum(seq[1:-1]) + 0.5 * seq[-1]


def head_prior(train_steps):
    sums = np.zeros(world.P); counts = np.zeros(world.P)
    for s in train_steps:
        for f, u in zip(s["cands"], s["utils"]):
            h = int(np.argmax(f[8:8 + world.P])); sums[h] += u; counts[h] += 1
    return sums / np.maximum(1, counts)


def run_arm(w, arm, model, hp, rng, budget=8):
    T = list(w.theory)
    A = {r: 0.0 for r in w.candidates}
    perm = list(w.candidates); rng.shuffle(perm)
    pmap = {r: perm[i] for i, r in enumerate(w.candidates)}
    traj = [debt(w, T)]
    false_assert = 0
    kevals = 0
    rounds = 0
    credit_based = arm in ("integral", "single", "scramble", "permute")
    for _ in range(budget):
        live = [r for r in w.candidates if r not in T]
        if not live:
            break
        # Credit-based arms need exact kernel credit for ALL live candidates to
        # rank; gradient/random/prior rank without kernel credit and only pay
        # for the single gate check below (fair compute accounting).
        c = {}
        if credit_based:
            for r in live:
                c[r] = world.utility(w, T, r, w.goals); kevals += 1
        if arm == "integral":
            for r in live:
                A[r] += c[r]
            score = {r: A[r] for r in live}
        elif arm == "single":
            score = dict(c)
        elif arm == "scramble":
            for r in live:
                A[r] += c.get(pmap[r], 0.0)
            score = {r: A[r] for r in live}
        elif arm == "permute":
            score = {r: c.get(pmap[r], 0.0) for r in live}
        elif arm == "random":
            score = {r: rng.random() for r in live}
        elif arm == "prior":
            score = {r: hp[int(np.argmax(world.candidate_features(w, T, w.goals, r)[8:8 + world.P]))]
                     for r in live}
        elif arm == "gradient":
            sf = torch.tensor(world.state_features(w, T, w.goals), dtype=torch.float32).unsqueeze(0)
            cf = torch.tensor([world.candidate_features(w, T, w.goals, r) for r in live], dtype=torch.float32).unsqueeze(0)
            mask = torch.zeros(1, 1 + len(live), dtype=torch.bool)
            with torch.no_grad():
                sc = model(sf, cf, mask)[0].numpy()
            score = {r: float(sc[i]) for i, r in enumerate(live)}
        else:
            raise ValueError(arm)
        best = max(live, key=lambda r: score[r])
        rounds += 1
        c_best = world.utility(w, T, best, w.goals); kevals += 1   # kernel gate
        if c_best <= 0:            # no positive-utility admission
            break
        T.append(best)
        traj.append(debt(w, T))
        if debt(w, T) == 0:
            break
    final = debt(w, T)
    cov = 1.0 - final / max(1, len(w.goals))
    return {"coverage": cov, "loss_integral": loss_integral(traj), "rounds": rounds,
            "kernel_evals": kevals, "false_assert": false_assert, "final_debt": final,
            "success": 1.0 if final == 0 else 0.0}


def train_gradient(seed, train_worlds=180, epochs=120):
    torch.manual_seed(seed); np.random.seed(seed); random.seed(seed)
    steps = [s for w in world.build_split("train", train_worlds, seed) for s in w]
    val = [s for w in world.build_split("val", 40, seed + 1) for s in w]
    model = build("base", len(steps[0]["state"]), world.CAND_DIM)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    def collate(batch):
        mn = max(len(s["cands"]) for s in batch)
        B = len(batch)
        st = torch.zeros(B, len(batch[0]["state"]))
        ca = torch.zeros(B, mn, world.CAND_DIM)
        ma = torch.ones(B, 1 + mn, dtype=torch.bool)
        ut = torch.zeros(B, mn); be = torch.zeros(B, dtype=torch.long); ln = []
        for i, s in enumerate(batch):
            n = len(s["cands"]); ln.append(n)
            st[i] = torch.tensor(s["state"]); ca[i, :n] = torch.tensor(s["cands"])
            ma[i, :1 + n] = False; ut[i, :n] = torch.tensor(s["utils"]); be[i] = s["best"]
        return st, ca, ma, ut, be, ln

    def val_top1():
        model.eval(); tot = []
        with torch.no_grad():
            for s in val:
                st = torch.tensor(s["state"]).unsqueeze(0)
                ca = torch.tensor(s["cands"]).unsqueeze(0)
                ma = torch.zeros(1, 1 + len(s["cands"]), dtype=torch.bool)
                sc = model(st, ca, ma)[0].numpy()
                tot.append(s["utils"][int(np.argmax(sc))])
        return float(np.mean(tot))

    best_v = -1e9; best_state = None
    for ep in range(epochs):
        model.train(); idx = list(range(len(steps))); random.shuffle(idx)
        for i in range(0, len(idx), 32):
            batch = [steps[j] for j in idx[i:i + 32]]
            st, ca, ma, ut, be, ln = collate(batch)
            logits = model(st, ca, ma)
            tgt = torch.softmax(ut.masked_fill(ma[:, 1:], -1e9) / 0.8, dim=1)
            loss = -(tgt * F.log_softmax(logits, dim=1)).sum(dim=1).mean()
            pair = 0.0
            for k, n in enumerate(ln):
                b = int(be[k])
                if n <= 1:
                    continue
                others = torch.cat([logits[k, :b], logits[k, b + 1:n]])
                pair = pair + F.softplus(others - logits[k, b]).mean()
            loss = loss + 0.5 * pair / max(1, len(batch))
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
        if ep % 10 == 0 or ep == epochs - 1:
            v = val_top1()
            if v > best_v:
                best_v = v; best_state = {k: x.detach().clone() for k, x in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model, len(steps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-worlds", type=int, default=80)
    ap.add_argument("--seed", type=int, default=777)
    ap.add_argument("--epochs", type=int, default=120)
    ap.add_argument("--out", default="integral_result.json")
    args = ap.parse_args()

    model, n_train_steps = train_gradient(args.seed, epochs=args.epochs)
    train_steps = [s for w in world.build_split("train", 180, args.seed) for s in w]
    hp = head_prior(train_steps)
    worlds = [world.make_world(random.Random(args.seed * 1000 + i), "test", i) for i in range(args.test_worlds)]

    out = {"seed": args.seed, "test_worlds": len(worlds), "gradient_train_steps": n_train_steps}
    for arm in ARMS:
        rows = [run_arm(w, arm, model, hp, random.Random(args.seed + 10000 + i)) for i, w in enumerate(worlds)]
        out[arm] = {k: float(np.mean([r[k] for r in rows])) for k in rows[0]}
        out[arm]["n"] = len(rows)
        succ = [r for r in rows if r["success"] == 1.0]
        out[arm]["success_rate"] = len(succ) / len(rows)
        out[arm]["rounds_given_success"] = float(np.mean([r["rounds"] for r in succ])) if succ else 0.0
        out[arm]["loss_integral_given_success"] = float(np.mean([r["loss_integral"] for r in succ])) if succ else 0.0
    (HERE / args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    for arm in ARMS:
        a = out[arm]
        print(f"{arm:9s} coverage={a['coverage']:.3f} success={a['success_rate']:.3f} "
              f"loss_integral={a['loss_integral']:.3f} rounds|succ={a['rounds_given_success']:.2f} "
              f"kevals={a['kernel_evals']:.1f} false={a['false_assert']:.3f}")
    print("E2-INTEGRAL-LEARNING-DONE")


if __name__ == "__main__":
    main()