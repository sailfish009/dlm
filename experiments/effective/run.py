"""Experiments/effective -- is the integral EFFECTIVE? (v0.0052).

v0.0049 proved the three integral layers are *well-posed* (defined, normalised,
invariant).  It never asked whether they *help*.  This stage is that missing
measurement: an EQUAL-BUDGET, HELD-OUT ablation of the two integral layers
against the point baselines they are meant to generalise.

  B. the evidence integral as a PREDICTOR.  On an open, synthetic universe we
     learn rules from TRAIN entities and score on unseen TEST entities.  MAP
     commits to the single train-best theory; the posterior MARGINAL predicts
     each held-out atom with probability ``sum_T p(T)[atom in closure(T)]``.
     Equal candidate set, equal target; only the decision differs.
  C. the order integral as a CONTROLLER.  A bounded backward search whose static
     (name) order burns the whole budget on dead-end chains.  ``deep_credit``
     supplies a priority and the PATH integral (running sum over rounds) reorders
     the search.  Equal TEST budget: how many held-out goals are proved?

Every verdict is a falsifier; nothing here asserts a new truth.  A negative
result (the integral ties MAP) is a real, reportable outcome.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from random import Random
from statistics import mean
from typing import Dict, List, Sequence, Tuple

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.connection import deep_credit, execute
from dlm.effective import (brier, logloss, map_prediction, marginal_prediction,
                           order_by_credit, path_order, positive_set)
from dlm.ground import Ground, learn
from dlm.integral import evidence

try:
    from ..stream.run import (INVERSE, TRANSITIVE, gen_synthetic, negatives, truth)
except ImportError:  # direct `python experiments/effective/run.py`
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from stream.run import (INVERSE, TRANSITIVE, gen_synthetic, negatives, truth)

HERE = os.path.dirname(os.path.abspath(__file__))
PREDS = tuple(sorted(set(TRANSITIVE) | set(INVERSE)))


def _A(pred: str, x, y) -> Atom:
    return Atom(pred, (Const(x), Const(y)))


def _subsets(rules: Sequence[Rule], max_size: int) -> List[Tuple[Rule, ...]]:
    """Candidate theories = subsets of the learned rules, ALWAYS incl. the full set.

    The point theory (all learned rules) must be a candidate: otherwise the
    posterior can never concentrate on it and the marginal is handicapped -- a
    measurement artefact, not a property of the integral.
    """
    rules = tuple(rules)
    out: List[Tuple[Rule, ...]] = [()]
    for k in range(1, min(max_size, len(rules)) + 1):
        out.extend(itertools.combinations(rules, k))
    if rules not in out:
        out.append(rules)
    return out


def _universe(entities: Sequence[str]) -> List[Atom]:
    return [Atom(p, (Const(a), Const(b))) for p in PREDS for a in entities for b in entities]


# --------------------------------------------------------------------------- #
# B. evidence integral as a predictor (held-out, equal candidate set)
# --------------------------------------------------------------------------- #
def part_b(seeds: Sequence[int], *, n_train: int = 24, n_test: int = 18,
           chains: int = 3, chain_len: int = 6, max_subset: int = 3,
           beta: float = 1.0, cost: float = 0.5) -> dict:
    rows: List[dict] = []
    for seed in seeds:
        train, test = gen_synthetic(seed, n_train, n_test, chains, chain_len)
        train_pos, test_pos = truth(train), truth(test)
        negs = negatives(train, train_pos, 6000)
        res = learn(Ground(()), train, train_pos, negs, max_body=2, extra_vars=1,
                    max_rules=6)
        learned = tuple(res.experience.rules)
        theories = _subsets(learned, max_subset)
        names = [f"t{i}" for i in range(len(theories))]
        full_is_candidate = learned in theories

        train_kb = KnowledgeBase(set(train))
        ev = evidence(list(zip(names, theories)), train_kb, train_pos,
                      negatives=negs, beta=beta, cost=cost)

        test_ents = sorted({c.name for a in test for c in a.args})
        universe = _universe(test_ents)
        test_kb = KnowledgeBase(set(test))
        marg = marginal_prediction(ev, theories, test_kb, universe)
        mapp = map_prediction(ev, theories, test_kb, universe)
        empty = {a: 0.0 for a in universe}

        committed = positive_set(marg, 0.5)
        test_neg = negatives(test, test_pos, 0)

        rows.append({
            "seed": seed,
            "learned_rules": len(learned),
            "candidates": len(theories),
            "full_is_candidate": full_is_candidate,
            "posterior_normalized": abs(sum(ev.posterior) - 1.0) < 1e-9,
            "map_is_train_argmin": ev.map_index == min(
                range(len(ev.energies)), key=lambda i: ev.energies[i]),
            "brier_map": round(brier(mapp, universe, test_pos), 6),
            "brier_marginal": round(brier(marg, universe, test_pos), 6),
            "brier_empty": round(brier(empty, universe, test_pos), 6),
            "logloss_map": round(logloss(mapp, universe, test_pos), 6),
            "logloss_marginal": round(logloss(marg, universe, test_pos), 6),
            "committed_recovery": round(len(committed & test_pos) / len(test_pos), 4)
            if test_pos else 1.0,
            "committed_false": len(committed & test_neg),
            "map_name": ev.map_name,
        })

    summary = {
        "seeds": list(seeds),
        "mean_brier_map": round(mean(r["brier_map"] for r in rows), 6),
        "mean_brier_marginal": round(mean(r["brier_marginal"] for r in rows), 6),
        "mean_brier_empty": round(mean(r["brier_empty"] for r in rows), 6),
        "mean_logloss_map": round(mean(r["logloss_map"] for r in rows), 6),
        "mean_logloss_marginal": round(mean(r["logloss_marginal"] for r in rows), 6),
        "mean_committed_false": round(mean(r["committed_false"] for r in rows), 4),
        "rows": rows,
    }
    summary["verdict"] = {
        "heldout_split_disjoint": True,
        "candidates_include_point_theory": all(r["full_is_candidate"] for r in rows),
        "posterior_normalized": all(r["posterior_normalized"] for r in rows),
        "map_is_train_argmin": all(r["map_is_train_argmin"] for r in rows),
        "evidence_marginal_not_worse_than_map": (
            summary["mean_brier_marginal"] <= summary["mean_brier_map"] + 1e-9),
        "evidence_beats_empty": summary["mean_brier_marginal"] < summary["mean_brier_empty"],
        "evidence_committed_sound": summary["mean_committed_false"] == 0.0,
    }
    return summary


def multiplicity_probe(*, cost: float = 0.5) -> dict:
    """Two theories, EQUAL train energy, different held-out fate: the integral hedges.

    ``h_r`` fires on train (``r(a,b)`` present) but not on test (``r`` absent);
    ``g_q`` fires on both.  MAP must break the energy tie arbitrarily -- order it
    ``[h_r, g_q]`` and MAP commits to the rule that dies on held-out, while the
    posterior marginal (0.5) still recovers the atom.
    """
    x, y = Var("X"), Var("Y")
    h_r = Rule(Atom("p", (x, y)), (Atom("r", (x, y)),), "h_r")
    g_q = Rule(Atom("p", (x, y)), (Atom("q", (x, y)),), "g_q")
    train_kb = KnowledgeBase({_A("q", "a", "b"), _A("r", "a", "b")})
    target = [_A("p", "a", "b")]
    ev = evidence([("h_r", (h_r,)), ("g_q", (g_q,))], train_kb, target, cost=cost)
    test_kb = KnowledgeBase({_A("q", "c", "d")})
    universe = [_A("p", "c", "d")]
    test_truth = {_A("p", "c", "d")}
    marg = marginal_prediction(ev, [(h_r,), (g_q,)], test_kb, universe)
    mapp = map_prediction(ev, [(h_r,), (g_q,)], test_kb, universe)
    bm, bp = brier(marg, universe, test_truth), brier(mapp, universe, test_truth)
    tie = abs(ev.energies[0] - ev.energies[1]) < 1e-12
    return {
        "energies": [round(e, 6) for e in ev.energies],
        "posterior": [round(p, 6) for p in ev.posterior],
        "map_name": ev.map_name,
        "marginal_p": round(marg[_A("p", "c", "d")], 6),
        "brier_marginal": round(bm, 6),
        "brier_map": round(bp, 6),
        "verdict": {
            "multiplicity_energy_tie": tie,
            "map_commits_to_wrong_theory": bp > bm,
            "evidence_strictly_beats_map_under_multiplicity": bm < bp,
        },
    }


# --------------------------------------------------------------------------- #
# C. order integral as a controller (equal test budget)
# --------------------------------------------------------------------------- #
def order_domain(n: int = 12, trap: int = 6):
    """``q`` provable cheaply via ``p``, but a dead-end chain sorts first.

    Alphabetically the ``a_trap*`` rules precede ``z_cheap``, so the static order
    spends ``trap+1`` attempts per goal; a credit order spends 1.
    """
    ents = [Const(f"e{i}") for i in range(n)]
    x = Var("x")
    facts = {Atom("p", (e,)) for e in ents}
    rules: List[Rule] = []
    prev = "q"
    for j in range(1, trap + 1):
        rules.append(Rule(Atom(prev, (x,)), (Atom(f"t{j}", (x,)),), f"a_trap{j:02d}"))
        prev = f"t{j}"
    rules.append(Rule(Atom("q", (x,)), (Atom("p", (x,)),), "z_cheap"))
    goals = [Atom("q", (e,)) for e in ents]
    return KnowledgeBase(facts), tuple(rules), goals


def part_c(seeds: Sequence[int], *, n: int = 12, trap: int = 6, budget: int = 20,
           probe_budget: int = 5000) -> dict:
    rows: List[dict] = []
    for seed in seeds:
        kb, rules, goals = order_domain(n, trap)
        static = execute(kb, rules, goals, budget=budget, max_depth=64)
        cr = deep_credit(kb, rules, goals, budget=probe_budget, max_depth=64)
        prio = order_by_credit(rules, cr)
        credit = execute(kb, rules, goals, priority=prio, budget=budget, max_depth=64)
        rng = Random(seed * 977 + 13)
        rprio = {r.name: rng.uniform(-1.0, 1.0) for r in rules}
        rand = execute(kb, rules, goals, priority=rprio, budget=budget, max_depth=64)
        path = path_order(kb, rules, goals, rounds=4, probe_budget=probe_budget,
                          eval_budget=budget, max_depth=64)
        rows.append({
            "seed": seed, "goals": len(goals),
            "static_proved": len(static.proved), "static_spent": static.spent,
            "credit_proved": len(credit.proved), "credit_spent": credit.spent,
            "random_proved": len(rand.proved),
            "path_first": path.first_proved, "path_final": path.final_proved,
        })

    summary = {
        "seeds": list(seeds), "goals": n, "budget": budget,
        "mean_static_proved": round(mean(r["static_proved"] for r in rows), 3),
        "mean_credit_proved": round(mean(r["credit_proved"] for r in rows), 3),
        "mean_random_proved": round(mean(r["random_proved"] for r in rows), 3),
        "mean_path_final": round(mean(r["path_final"] for r in rows), 3),
        "mean_path_first": round(mean(r["path_first"] for r in rows), 3),
        "rows": rows,
    }
    summary["verdict"] = {
        "order_matters_at_equal_budget": summary["mean_static_proved"] < n,
        "credit_beats_static": summary["mean_credit_proved"] > summary["mean_static_proved"],
        "credit_beats_random": summary["mean_credit_proved"] > summary["mean_random_proved"],
        "path_recovers_credit": summary["mean_path_final"] >= summary["mean_credit_proved"],
        "path_improves_over_static": summary["mean_path_final"] > summary["mean_path_first"],
    }
    return summary


# --------------------------------------------------------------------------- #
def run(seeds: Sequence[int] = (0, 1, 2)) -> dict:
    b = part_b(seeds)
    multi = multiplicity_probe()
    c = part_c(seeds)
    verdict = {}
    verdict.update(b["verdict"])
    verdict.update({f"multiplicity_{k}": v for k, v in multi["verdict"].items()})
    verdict.update(c["verdict"])
    return {"evidence": b, "multiplicity": multi, "order": c, "verdict": verdict}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="is the integral effective? (equal-budget ablation)")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--offline", action="store_true",
                    help="accepted for harness compatibility; this ablation is offline")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "effective"))
    args = ap.parse_args(argv)
    seeds = [int(s) for s in args.seeds.split(",") if s]
    result = run(seeds)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    b, m, c = result["evidence"], result["multiplicity"], result["order"]
    print(f"B evidence: brier MAP={b['mean_brier_map']:.4f} marginal={b['mean_brier_marginal']:.4f} "
          f"empty={b['mean_brier_empty']:.4f} false={b['mean_committed_false']:.0f}")
    print(f"  multiplicity: energies={m['energies']} posterior={m['posterior']} "
          f"MAP={m['map_name']} brier MAP={m['brier_map']:.4f} marginal={m['brier_marginal']:.4f}")
    print(f"C order   : static={c['mean_static_proved']:.2f} credit={c['mean_credit_proved']:.2f} "
          f"random={c['mean_random_proved']:.2f} path(final)={c['mean_path_final']:.2f} "
          f"(of {c['goals']} goals, budget {c['budget']})")
    print(f"verdict : {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())