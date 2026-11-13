#!/usr/bin/env python3
"""M1: proof-state set ranker on synthetic kernel-utility labels."""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

import world
from model import SetRanker

HERE = Path(__file__).resolve().parent
DEVICE = torch.device("cpu")


def collate(steps, max_n=None):
    if max_n is None:
        max_n = max(len(s["cands"]) for s in steps)
    B = len(steps)
    state = torch.zeros(B, len(steps[0]["state"]))
    cands = torch.zeros(B, max_n, world.CAND_DIM)
    mask = torch.ones(B, 1 + max_n, dtype=torch.bool)
    utils = torch.zeros(B, max_n)
    best = torch.zeros(B, dtype=torch.long)
    lengths = []
    for i, s in enumerate(steps):
        n = len(s["cands"])
        lengths.append(n)
        state[i] = torch.tensor(s["state"], dtype=torch.float32)
        cands[i, :n] = torch.tensor(s["cands"], dtype=torch.float32)
        mask[i, :1 + n] = False
        utils[i, :n] = torch.tensor(s["utils"], dtype=torch.float32)
        best[i] = int(s["best"])
    return state, cands, mask, utils, best, lengths


def top1_metrics(steps, scores):
    util, hit, regret = [], [], []
    for s, sc in zip(steps, scores):
        i = int(np.argmax(sc))
        u = s["utils"]
        b = int(s["best"])
        util.append(u[i])
        hit.append(1.0 if i == b else 0.0)
        regret.append(max(u) - u[i])
    return {
        "top1_utility": float(np.mean(util)),
        "hit": float(np.mean(hit)),
        "regret": float(np.mean(regret)),
        "max_regret": float(np.max(regret)),
    }


def score_model(model, steps):
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(steps), 64):
            chunk = steps[i:i + 64]
            st, ca, ma, _u, _b, lens = collate(chunk)
            logits = model(st, ca, ma)
            for j, n in enumerate(lens):
                out.append(logits[j, :n].cpu().numpy())
    return out


def score_prior(steps, head_prior):
    out = []
    for s in steps:
        sc = []
        for f in s["cands"]:
            head = int(np.argmax(f[8:8 + world.P]))
            sc.append(head_prior[head] - 0.2 * f[1])
        out.append(np.array(sc))
    return out


def score_support(steps):
    # A non-learned heuristic: prefer rules whose bodies are already satisfied.
    return [np.array([f[3] + 0.5 * f[5] for f in s["cands"]]) for s in steps]

def score_shuffled(model, steps, seed=99):
    """Break candidate/feature correspondence; keep the oracle labels."""
    rng = np.random.default_rng(seed)
    out = []
    for s in steps:
        n = len(s["cands"])
        perm = rng.permutation(n)
        fake = dict(s)
        # Keep position i, but replace its features with another candidate's
        # features.  A permutation-equivariant model cannot hide this mismatch.
        fake["cands"] = [s["cands"][int(perm[i])] for i in range(n)]
        out.append(score_model(model, [fake])[0])
    return out


def train(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)

    train_steps = [s for w in world.build_split("train", args.train_worlds, args.seed) for s in w]
    val_steps = [s for w in world.build_split("val", args.val_worlds, args.seed + 1) for s in w]
    test_steps = [s for w in world.build_split("test", args.test_worlds, args.seed + 2) for s in w]
    print(f"DATA train={len(train_steps)} val={len(val_steps)} test={len(test_steps)}")

    # Prior-only control: mean utility by head predicate on TRAIN.
    sums = np.zeros(world.P)
    counts = np.zeros(world.P)
    for s in train_steps:
        for f, u in zip(s["cands"], s["utils"]):
            h = int(np.argmax(f[8:8 + world.P]))
            sums[h] += u
            counts[h] += 1
    head_prior = sums / np.maximum(1, counts)

    model = SetRanker(len(train_steps[0]["state"]), world.CAND_DIM, d=args.d, layers=args.layers, heads=args.heads)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    def batch_loss(batch):
        st, ca, ma, utils, best, lens = collate(batch)
        logits = model(st, ca, ma)
        # listwise utility target (masked)
        tgt = torch.softmax(utils.masked_fill(ma[:, 1:], -1e9) / args.temp, dim=1)
        loss = -(tgt * F.log_softmax(logits, dim=1)).sum(dim=1).mean()
        # top-1 pairwise term
        pair = 0.0
        for i, n in enumerate(lens):
            b = int(best[i])
            if n <= 1:
                continue
            others = torch.cat([logits[i, :b], logits[i, b + 1:n]])
            pair = pair + F.softplus(others - logits[i, b]).mean()
        pair = pair / max(1, len(batch))
        return loss + args.pair_weight * pair

    best_val = -1e9
    best_state = None
    for ep in range(args.epochs):
        model.train()
        idx = list(range(len(train_steps)))
        random.shuffle(idx)
        total = 0.0
        for i in range(0, len(idx), args.batch):
            batch = [train_steps[j] for j in idx[i:i + args.batch]]
            loss = batch_loss(batch)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += loss.item() * len(batch)
        if ep % 10 == 0 or ep == args.epochs - 1:
            val = top1_metrics(val_steps, score_model(model, val_steps))
            print(f"EP {ep:03d} loss={total / len(train_steps):.4f} val_top1={val['top1_utility']:.4f} val_hit={val['hit']:.3f}")
            if val["top1_utility"] > best_val:
                best_val = val["top1_utility"]
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)

    test_scores = score_model(model, test_steps)
    model_m = top1_metrics(test_steps, test_scores)
    prior_m = top1_metrics(test_steps, score_prior(test_steps, head_prior))
    support_m = top1_metrics(test_steps, score_support(test_steps))
    rng = np.random.default_rng(7)
    rand_scores = [rng.random(len(s["cands"])) for s in test_steps]
    rand_m = top1_metrics(test_steps, rand_scores)
    # untrained control
    untrained = SetRanker(len(test_steps[0]["state"]), world.CAND_DIM, d=args.d, layers=args.layers, heads=args.heads)
    untrained_m = top1_metrics(test_steps, score_model(untrained, test_steps))
    shuffled_m = top1_metrics(test_steps, score_shuffled(model, test_steps))

    result = {
        "data": {"train": len(train_steps), "val": len(val_steps), "test": len(test_steps)},
        "model": model_m,
        "prior_only": prior_m,
        "support_only": support_m,
        "random": rand_m,
        "untrained": untrained_m,
        "shuffled_features": shuffled_m,
    }
    print(json.dumps(result, indent=2))
    out = HERE / "m1_result.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    torch.save(model.state_dict(), HERE / "m1_ranker.pt")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-worlds", type=int, default=180)
    ap.add_argument("--val-worlds", type=int, default=40)
    ap.add_argument("--test-worlds", type=int, default=40)
    ap.add_argument("--epochs", type=int, default=150)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--d", type=int, default=32)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--temp", type=float, default=0.8)
    ap.add_argument("--pair-weight", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=11)
    train(ap.parse_args())
