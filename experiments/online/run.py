"""DLM v0.0039 online experiment: referents stream in; the theory keeps up.

Diagnostic instrument (not a kernel layer).  Train entities arrive one batch at
a time (an *online* open universe).  After each batch the arm learns -- and for
``abstract`` folds recurring subgoals -- then the theory is scored on **unseen
test entities**.  One rich JSONL row per round is logged so many aspects of
learning can be analysed afterwards: coverage, soundness, generalisation gap,
theory growth (DL), rule bodies, derivation depth, within-round diminishing
returns, and cost.  ``--analyze`` reads the logs back as a report.

Arms: ``frozen`` (no learning) | ``plain`` (learn) | ``abstract`` (learn +
abstract_theory) | ``random`` (control: random positives).

Nothing here asserts: every number is read from the kernel closure.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from random import Random
from statistics import mean
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dlm import Atom, Const, KnowledgeBase, closure  # noqa: E402
from dlm.abstract import abstract_theory, theory_dl  # noqa: E402
from dlm.ground import Experience, Ground, learn  # noqa: E402
from dlm.proof import prove, proof_size  # noqa: E402
from experiments.stream.run import (TRANSITIVE, gen_synthetic,  # noqa: E402
                                     negatives, truth)

ARMS = ("frozen", "plain", "abstract", "random")
INDUCING = ("plain", "abstract", "random")
CURVE_FIELDS = ("held_recovery", "held_gain", "train_recovery", "train_false",
                "false_assert", "clauses", "new_clauses", "dl", "avg_body_len",
                "max_depth", "mean_depth", "learn_seconds", "negatives",
                "revealed_facts")
RECORD_FIELDS = (
    "arm", "seed", "round", "revealed_facts", "revealed_entities", "revealed_pairs",
    "negatives", "clauses", "new_clauses", "dl", "dl_delta", "invented", "heads",
    "train_recovery", "train_false", "generalization_gap", "held_recovery",
    "held_gain", "held_new", "false_assert", "avg_body_len", "retention", "churn",
    "rules_admitted", "intra_curve", "max_depth", "mean_depth", "proof_nodes",
    "depth_sampled", "learn_seconds")


def _batches(items: Sequence[Atom], rounds: int) -> List[set]:
    ordered = sorted(items, key=str)
    return [set(ordered[: round(len(ordered) * (r + 1) / rounds)]) for r in range(rounds)]


def _kb(rules: Sequence, facts: set) -> KnowledgeBase:
    kb = KnowledgeBase(set(facts))
    for r in rules:
        kb.add_rule(r)
    return kb


def _pct(hit: int, total: int) -> float:
    return round(hit / total, 4) if total else 1.0


def _random_positives(revealed: set, revealed_truth: set, cap: int, rng: Random) -> set:
    ents = sorted({c.name for a in revealed for c in a.args})
    preds = sorted({a.pred for a in revealed} | set(TRANSITIVE))
    pool = [Atom(p, (Const(x), Const(y))) for p in preds for x in ents for y in ents
            if Atom(p, (Const(x), Const(y))) not in revealed_truth]
    rng.shuffle(pool)
    return set(pool[:cap])


def _depth(p) -> int:
    return 0 if not p.premises else 1 + max(_depth(x) for x in p.premises)


def _derivation_stats(covered: set, kb: KnowledgeBase, rng: Random, cap: int) -> dict:
    """Proof-tree depth/nodes over a bounded, deterministic sample of covered atoms."""
    pool = sorted(covered, key=str)
    sample = pool if len(pool) <= cap else [pool[i] for i in sorted(rng.sample(range(len(pool)), cap))]
    depths, nodes = [], []
    for a in sample:
        p = prove(kb, a)
        if p is not None:
            depths.append(_depth(p))
            nodes.append(proof_size(p))
    if not depths:
        return {"max_depth": 0, "mean_depth": 0.0, "proof_nodes": 0, "sampled": 0}
    return {"max_depth": max(depths), "mean_depth": round(mean(depths), 3),
            "proof_nodes": sum(nodes), "sampled": len(depths)}


def online_run(arm: str, seed: int, *, n_train: int, n_test: int, chains: int,
               chain_len: int, rounds: int, max_body: int, extra_vars: int,
               max_rules: int, max_neg: int, depth_cap: int = 8) -> List[dict]:
    """Stream trainer, one rich log record per round.  Deterministic per (arm, seed)."""
    train, test = gen_synthetic(seed, n_train, n_test, chains, chain_len)
    test_pos = truth(test)
    ground = Ground(())
    exp = Experience()
    rng = Random(seed * 1000 + 7)
    rows: List[dict] = []
    prev_dl = prev_held = 0.0
    prev_clauses = 0
    prev_covered: set = set()
    prev_rules: set = set()

    for r, revealed in enumerate(_batches(train, rounds), start=1):
        revealed_truth = truth(revealed)
        neg = negatives(revealed, revealed_truth, max_neg)
        dl_before = theory_dl(ground.rules + exp.rules)
        intra: List[float] = []
        learn_s = 0.0
        if arm in INDUCING:
            pos = (revealed_truth if arm != "random"
                   else _random_positives(revealed, revealed_truth,
                                          min(len(revealed_truth), 300), rng))

            def cb(e, rule, _tf=test, _tp=test_pos):
                # held-out recovery after each admitted rule: score on the UNSEEN facts
                intra.append(round(_pct(len(closure(e.to_kb(ground.base(_tf))) & _tp),
                                        len(_tp)), 4))

            t0 = time.time()
            exp = learn(ground, revealed, pos, neg, max_body=max_body,
                        extra_vars=extra_vars, max_rules=max_rules,
                        callback=cb).experience
            learn_s = time.time() - t0

        rules = ground.rules + exp.rules
        invented = 0
        dl = theory_dl(rules)
        if arm == "abstract":
            ab = abstract_theory(rules, revealed)
            rules, invented, dl = ab.theory, len(ab.abstractions), ab.dl_after

        kb_train = _kb(rules, revealed)
        closed_train = closure(kb_train)
        train_rec = _pct(len(closed_train & revealed_truth), len(revealed_truth))
        train_false = len(closed_train - revealed_truth)

        kb_test = _kb(rules, test)
        closed_test = closure(kb_test)
        covered = closed_test & test_pos
        held = _pct(len(covered), len(test_pos))
        false_assert = len(closed_test - test_pos)

        cur_rules = {str(x) for x in exp.rules}
        bodies = [len(x.body) for x in exp.rules]
        d = _derivation_stats(covered, kb_test, rng, depth_cap)

        rows.append({
            "arm": arm, "seed": seed, "round": r,
            "revealed_facts": len(revealed),
            "revealed_entities": len({c.name for a in revealed for c in a.args}),
            "revealed_pairs": len(revealed_truth), "negatives": len(neg),
            "clauses": len(exp.rules), "new_clauses": len(exp.rules) - prev_clauses,
            "dl": dl, "dl_delta": dl - prev_dl, "invented": invented,
            "heads": len({x.head.pred for x in rules}),
            "train_recovery": train_rec, "train_false": train_false,
            "generalization_gap": round(train_rec - held, 4),
            "held_recovery": held, "held_gain": round(held - prev_held, 4),
            "held_new": len(covered - prev_covered), "false_assert": false_assert,
            "avg_body_len": round(mean(bodies), 3) if bodies else 0.0,
            "retention": (round(len(cur_rules & prev_rules) / len(prev_rules), 3)
                          if prev_rules else 1.0),
            "churn": len(prev_rules - cur_rules),
            "rules_admitted": len(intra), "intra_curve": intra,
            "max_depth": d["max_depth"], "mean_depth": d["mean_depth"],
            "proof_nodes": d["proof_nodes"], "depth_sampled": d["sampled"],
            "learn_seconds": round(learn_s, 3),
        })
        prev_dl, prev_held = dl, held
        prev_clauses, prev_covered, prev_rules = len(exp.rules), covered, cur_rules
    return rows


def _mean(rs: Sequence[dict], key: str) -> float:
    vals = [r[key] for r in rs if isinstance(r.get(key), (int, float))]
    return round(mean(vals), 4) if vals else 0.0


def _curve(rows: Sequence[dict]) -> List[dict]:
    out: List[dict] = []
    for rd in sorted({r["round"] for r in rows}):
        rs = [r for r in rows if r["round"] == rd]
        out.append({"round": rd, **{k: _mean(rs, k) for k in CURVE_FIELDS}})
    return out


def run(arm: str, seeds: Sequence[int], cfg: dict) -> Tuple[List[dict], dict]:
    all_rows: List[dict] = []
    for s in seeds:
        all_rows.extend(online_run(arm, s, **cfg))
    last = max(x["round"] for x in all_rows)
    final = [r for r in all_rows if r["round"] == last]
    agg = {
        "arm": arm, "seeds": list(seeds), "curve": _curve(all_rows),
        "final": {k: _mean(final, k) for k in CURVE_FIELDS + ("max_depth", "proof_nodes")},
        "final_held_recovery": _mean(final, "held_recovery"),
        "final_false": _mean(final, "false_assert"),
        "final_dl": _mean(final, "dl"),
        "final_train_recovery": _mean(final, "train_recovery"),
        "final_seconds": _mean(final, "learn_seconds"),
        "max_invented": max((r["invented"] for r in all_rows), default=0),
        "rose_in_all_seeds": all(
            max(r["held_recovery"] for r in all_rows if r["seed"] == s)
            > min(r["held_recovery"] for r in all_rows if r["seed"] == s) for s in seeds),
    }
    return all_rows, agg


def _table(arm_curves: Dict[str, List[dict]]) -> List[str]:
    rounds = sorted({c["round"] for cur in arm_curves.values() for c in cur})
    lines = ["  held-out recovery by round (mean over seeds)",
             "  arm       " + "".join(f" r{r:<5}" for r in rounds)]
    for arm, cur in arm_curves.items():
        by = {c["round"]: c for c in cur}
        lines.append(f"  {arm:9s} " + "".join(f" {by[r]['held_recovery']:.3f}" for r in rounds))
    return lines


def analyze(outdir: Path) -> Tuple[str, dict]:
    """Read ``*_s*.jsonl`` logs; print a multi-aspect learning report + verdict."""
    by_arm: Dict[str, List[dict]] = {}
    for path in sorted(outdir.glob("*_s*.jsonl")):
        arm = path.name.split("_s")[0]
        rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        if rows:
            by_arm.setdefault(arm, []).extend(rows)
    if not by_arm:
        return "no logs under " + str(outdir), {}
    arm_curves = {a: _curve(rs) for a, rs in by_arm.items()}
    lines = ["== online learning report ==", "", "[coverage] on unseen entities"]
    lines += _table(arm_curves) + [""]

    lines.append("[soundness] false asserts on unseen entities (want 0)")
    for arm, cur in sorted(arm_curves.items()):
        vals = ",".join(f"{c['false_assert']:.0f}" for c in cur)
        lines.append(f"  {arm:9s} by round=[{vals}] final={cur[-1]['false_assert']:.0f}")
    lines.append("")

    lines.append("[generalisation] train fit vs unseen; theory growth")
    for arm, cur in sorted(arm_curves.items()):
        f = cur[-1]
        lines.append(f"  {arm:9s} train={f['train_recovery']:.3f} held={f['held_recovery']:.3f} "
                     f"gap={f['train_recovery'] - f['held_recovery']:+.3f} "
                     f"clauses={f['clauses']:.1f} dl={f['dl']:.0f} body={f['avg_body_len']:.2f} "
                     f"invented={max(c.get('invented', 0) for c in by_arm[arm])}")
    lines.append("")

    lines.append("[dynamics] per-round new coverage, proof depth, cost")
    for arm, cur in sorted(arm_curves.items()):
        gains = ",".join(f"{c['held_gain']:+.3f}" for c in cur)
        lines.append(f"  {arm:9s} held_gain=[{gains}] "
                     f"depth={cur[-1]['max_depth']:.0f} "
                     f"sec={sum(c['learn_seconds'] for c in cur):.2f}")
    lines.append("")

    agg: dict = {}
    for arm, cur in arm_curves.items():
        rs = by_arm[arm]
        agg[arm] = {k: cur[-1][k] for k in CURVE_FIELDS}
        agg[arm]["max_false"] = max(r["false_assert"] for r in rs)
        agg[arm]["invented"] = max(r["invented"] for r in rs)
    lines.append("[intra-round] held-out after each admitted rule (mean of rounds)")
    for arm, rs in sorted(by_arm.items()):
        curves = [r["intra_curve"] for r in rs if r["intra_curve"]]
        if curves:
            n = min(len(c) for c in curves)
            lines.append(f"  {arm:9s} " + " ".join(
                f"{mean(c[i] for c in curves):.3f}" for i in range(n)))
    lines.append("")

    if "plain" in agg and "frozen" in agg:
        gain = agg["plain"]["held_recovery"] - agg["frozen"]["held_recovery"]
        lines.append(f"[verdict] online learning gain over frozen = {gain:+.3f}")
        lines.append(f"[verdict] plain sound at end = {agg['plain']['false_assert'] == 0}")
    return "\n".join(lines), agg


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--arms", default="frozen,plain,abstract,random")
    p.add_argument("--seeds", default="0,1,2")
    p.add_argument("--rounds", type=int, default=5)
    p.add_argument("--n-train", type=int, default=24)
    p.add_argument("--n-test", type=int, default=18)
    p.add_argument("--chains", type=int, default=3)
    p.add_argument("--chain-len", type=int, default=6)
    p.add_argument("--max-body", type=int, default=2)
    p.add_argument("--extra-vars", type=int, default=1)
    p.add_argument("--max-rules", type=int, default=6)
    p.add_argument("--max-neg", type=int, default=6000)
    p.add_argument("--depth-cap", type=int, default=8)
    p.add_argument("--quick", action="store_true", help="tiny smoke config")
    p.add_argument("--big", action="store_true", help="more data (slower)")
    p.add_argument("--outdir", default="reports/online")
    p.add_argument("--analyze", default="")
    args = p.parse_args(argv)

    if args.analyze:
        text, _ = analyze(Path(args.analyze))
        print(text)
        return 0
    if args.quick:
        args.n_train, args.n_test, args.chains, args.chain_len = 10, 8, 1, 4
        args.rounds, args.max_rules, args.max_neg = 3, 4, 2000
    elif args.big:
        args.n_train, args.n_test, args.chains, args.chain_len = 30, 22, 4, 7
        args.rounds, args.max_rules, args.max_neg = 8, 8, 12000

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cfg = dict(n_train=args.n_train, n_test=args.n_test, chains=args.chains,
               chain_len=args.chain_len, rounds=args.rounds, max_body=args.max_body,
               extra_vars=args.extra_vars, max_rules=args.max_rules,
               max_neg=args.max_neg, depth_cap=args.depth_cap)
    arms = [a for a in args.arms.split(",") if a]
    seeds = [int(s) for s in args.seeds.split(",") if s]

    summary: Dict[str, dict] = {}
    for arm in arms:
        rows, agg = run(arm, seeds, cfg)
        summary[arm] = agg
        for s in seeds:
            with open(outdir / f"{arm}_s{s}.jsonl", "w", encoding="utf-8") as fh:
                for row in (r for r in rows if r["seed"] == s):
                    fh.write(json.dumps(row, sort_keys=True) + "\n")
        print(f"  {arm:9s} final_held={agg['final_held_recovery']:.3f} "
              f"final_false={agg['final_false']:.3f} dl={agg['final_dl']:.1f} "
              f"train={agg['final_train_recovery']:.3f} "
              f"sec={agg['final_seconds']:.2f} invented={agg['max_invented']} "
              f"rose={agg['rose_in_all_seeds']}")
    (outdir / "summary.json").write_text(
        json.dumps({"config": cfg, "arms": summary}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())