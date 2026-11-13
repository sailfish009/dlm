#!/usr/bin/env python3
"""M2: kernel-utility ranking + admission BCE with conflict hard negatives."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

import world
from model_m2 import SetRankerM2

HERE = Path(__file__).resolve().parent
DEVICE = torch.device("cpu")


def collate(steps):
    max_n = max(len(s["cands"]) for s in steps)
    B = len(steps)
    state = torch.zeros(B, len(steps[0]["state"]))
    cands = torch.zeros(B, max_n, world.M2_CAND_DIM)
    mask = torch.ones(B, 1 + max_n, dtype=torch.bool)
    utils = torch.zeros(B, max_n)
    admit = torch.zeros(B, max_n)
    conflict = torch.zeros(B, max_n)
    hard = torch.zeros(B, max_n)
    best = torch.zeros(B, dtype=torch.long)
    lens = []
    for i, s in enumerate(steps):
        n = len(s["cands"]); lens.append(n)
        state[i] = torch.tensor(s["state"], dtype=torch.float32)
        cands[i, :n] = torch.tensor(s["cands"], dtype=torch.float32)
        mask[i, :1 + n] = False
        utils[i, :n] = torch.tensor(s["utils"], dtype=torch.float32)
        admit[i, :n] = torch.tensor(s["admit"], dtype=torch.float32)
        conflict[i, :n] = torch.tensor(s["conflict"], dtype=torch.float32)
        hard[i, :n] = torch.tensor(s["hard_neg"], dtype=torch.float32)
        best[i] = int(s["best"])
    return state, cands, mask, utils, admit, conflict, hard, best, lens


def score_model(model, steps):
    model.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(steps), 64):
            chunk = steps[i:i + 64]
            st, ca, ma, _u, _a, _c, _h, _b, lens = collate(chunk)
            sc, ad = model(st, ca, ma)
            for j, n in enumerate(lens):
                out.append((sc[j, :n].cpu().numpy(), ad[j, :n].cpu().numpy()))
    return out


def top1_metrics(steps, scores):
    util, hit, regret = [], [], []
    for s, sc in zip(steps, scores):
        i = int(np.argmax(sc)); u = s["utils"]; b = int(s["best"])
        util.append(u[i]); hit.append(1.0 if i == b else 0.0); regret.append(max(u) - u[i])
    return {"top1_utility": float(np.mean(util)), "hit": float(np.mean(hit)),
            "regret": float(np.mean(regret)), "max_regret": float(np.max(regret))}


def conflict_metrics(steps, probs):
    hard_total = hard_reject = conflict_total = conflict_reject = 0
    tp = fp = fn = 0
    for s, p in zip(steps, probs):
        pred = (p >= 0.5).astype(float)
        for i, h in enumerate(s["hard_neg"]):
            if h:
                hard_total += 1; hard_reject += int(pred[i] == 0)
        for i, c in enumerate(s["conflict"]):
            if c > 0:
                conflict_total += 1; conflict_reject += int(pred[i] == 0)
        for i, a in enumerate(s["admit"]):
            if pred[i] == 1 and a == 1: tp += 1
            elif pred[i] == 1 and a == 0: fp += 1
            elif pred[i] == 0 and a == 1: fn += 1
    prec = tp / max(1, tp + fp); rec = tp / max(1, tp + fn)
    f1 = 2 * prec * rec / max(1e-9, prec + rec)
    return {
        "hard_neg_reject_rate": hard_reject / max(1, hard_total),
        "conflict_reject_rate": conflict_reject / max(1, conflict_total),
        "admission_precision": prec,
        "admission_recall": rec,
        "admission_f1": f1,
        "hard_neg_count": hard_total,
        "conflict_count": conflict_total,
    }


def score_prior(steps, head_prior):
    out = []
    for s in steps:
        sc = []
        for f in s["cands"]:
            h = int(np.argmax(f[8:8 + world.P]))
            sc.append(head_prior[h] - 0.2 * f[1])
        out.append(np.array(sc))
    return out


def score_support(steps):
    return [np.array([f[3] + 0.5 * f[5] for f in s["cands"]]) for s in steps]


def score_shuffled(model, steps, seed=99):
    rng = np.random.default_rng(seed); out = []
    for s in steps:
        n = len(s["cands"]); perm = rng.permutation(n)
        fake = dict(s); fake["cands"] = [s["cands"][int(perm[i])] for i in range(n)]
        sc, ad = score_model(model, [fake])[0]
        out.append((sc, ad))
    return out


def train(args):
    torch.manual_seed(args.seed); np.random.seed(args.seed); random.seed(args.seed)
    train_steps = [s for w in world.build_split_m2("train", args.train_worlds, args.seed) for s in w]
    val_steps = [s for w in world.build_split_m2("val", args.val_worlds, args.seed + 1) for s in w]
    test_steps = [s for w in world.build_split_m2("test", args.test_worlds, args.seed + 2) for s in w]
    print(f"DATA train={len(train_steps)} val={len(val_steps)} test={len(test_steps)}")

    sums = np.zeros(world.P); counts = np.zeros(world.P)
    for s in train_steps:
        for f, u in zip(s["cands"], s["utils"]):
            h = int(np.argmax(f[8:8 + world.P])); sums[h] += u; counts[h] += 1
    head_prior = sums / np.maximum(1, counts)

    model = SetRankerM2(len(train_steps[0]["state"]), world.M2_CAND_DIM, d=args.d, layers=args.layers, heads=args.heads)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    def batch_loss(batch):
        st, ca, ma, utils, admit, conflict, hard, best, lens = collate(batch)
        score, admit_logit = model(st, ca, ma)
        tgt = torch.softmax(utils.masked_fill(ma[:, 1:], -1e9) / args.temp, dim=1)
        rank_loss = -(tgt * F.log_softmax(score, dim=1)).sum(dim=1).mean()
        pair = 0.0
        for i, n in enumerate(lens):
            b = int(best[i])
            if n <= 1: continue
            others = torch.cat([score[i, :b], score[i, b + 1:n]])
            pair = pair + F.softplus(others - score[i, b]).mean()
        pair = pair / max(1, len(batch))
        bce = F.binary_cross_entropy_with_logits(admit_logit, admit)
        return rank_loss + args.pair_weight * pair + args.admit_weight * bce

    best_val = -1e9; best_state = None
    for ep in range(args.epochs):
        model.train(); idx = list(range(len(train_steps))); random.shuffle(idx); total = 0.0
        for i in range(0, len(idx), args.batch):
            batch = [train_steps[j] for j in idx[i:i + args.batch]]
            loss = batch_loss(batch)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
            total += loss.item() * len(batch)
        if ep % 10 == 0 or ep == args.epochs - 1:
            vals = score_model(model, val_steps)
            vm = top1_metrics(val_steps, [x[0] for x in vals])
            cm = conflict_metrics(val_steps, [1 / (1 + np.exp(-x[1])) for x in vals])
            print(f"EP {ep:03d} loss={total / len(train_steps):.4f} val_top1={vm['top1_utility']:.4f} "
                  f"val_hit={vm['hit']:.3f} conf_rej={cm['conflict_reject_rate']:.3f} adm_f1={cm['admission_f1']:.3f}")
            metric = vm["top1_utility"] + 0.5 * cm["conflict_reject_rate"] + 0.5 * cm["admission_f1"]
            if metric > best_val:
                best_val = metric
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)

    test_vals = score_model(model, test_steps)
    test_scores = [x[0] for x in test_vals]
    test_probs = [1 / (1 + np.exp(-x[1])) for x in test_vals]
    prior_scores = score_prior(test_steps, head_prior)
    support_scores = score_support(test_steps)
    rng = np.random.default_rng(7)
    rand_scores = [rng.random(len(s["cands"])) for s in test_steps]
    shuffled = score_shuffled(model, test_steps)
    untrained = SetRankerM2(len(test_steps[0]["state"]), world.M2_CAND_DIM, d=args.d, layers=args.layers, heads=args.heads)
    untrained_vals = score_model(untrained, test_steps)

    result = {
        "data": {"train": len(train_steps), "val": len(val_steps), "test": len(test_steps)},
        "model": top1_metrics(test_steps, test_scores),
        "model_conflict": conflict_metrics(test_steps, test_probs),
        "prior_only": top1_metrics(test_steps, prior_scores),
        "support_only": top1_metrics(test_steps, support_scores),
        "random": top1_metrics(test_steps, rand_scores),
        "untrained": top1_metrics(test_steps, [x[0] for x in untrained_vals]),
        "shuffled_features": top1_metrics(test_steps, [x[0] for x in shuffled]),
    }
    print(json.dumps(result, indent=2))
    (HERE / "m2_result.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(model.state_dict(), HERE / "m2_ranker.pt")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-worlds", type=int, default=180)
    ap.add_argument("--val-worlds", type=int, default=40)
    ap.add_argument("--test-worlds", type=int, default=40)
    ap.add_argument("--epochs", type=int, default=120)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--d", type=int, default=32)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--temp", type=float, default=0.8)
    ap.add_argument("--pair-weight", type=float, default=0.5)
    ap.add_argument("--admit-weight", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=21)
    train(ap.parse_args())
