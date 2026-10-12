"""Verifiable-reward self-supervised loop over programs (DLM v0.0024, NOTE 76).

Question.  The fused core already turns kernel verdicts into labels and reweights
clauses, but the *loop* was missing: a proposer emits a program (a set of Horn
clauses = Lisp-like code), the kernel verifies it, false_assert gates it, and only
verified programs are promoted into the theory -- which then becomes the next
round's environment.  Can that loop improve the model over rounds, with **zero
human labels**, and do the controls fail?

Task (controlled, kernel-labelled).  A chain ``e(n0,n1), e(n1,n2), ...`` is the
only base fact.  Round ``r`` asks for the predicate ``t_r`` = pairs at distance
exactly ``2**r`` (2, 4, 8, 16, 32).  A single induction pass may use body length
at most 2, so it can express distance-2 but *not* distance-4..32 directly.  The
loop composes: round 1 learns ``t1(x,y):-e(x,z),e(z,y)``; round 2 promotes it and
learns ``t2(x,y):-t1(x,z),t1(z,y)``; and so on -- a program whose body length
would be 32 in one shot but is 2 clauses deep through reuse.

Arms (identical data/learner/budget; only the reward/promotion differs)::

    learn          propose -> kernel-verify -> promote verified (the method)
    no_promote     no feedback: proposals are never promoted
    scramble       the label source is shuffled -> the reward is misaligned
    random         a random program is proposed; the gate rejects it
    reward_hacking the hard gate is removed: a plausible-but-wrong program is promoted

Run::

    PYTHONPATH=. python experiments/selfsup/run.py
    PYTHONPATH=. python experiments/selfsup/run.py --quick --json report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dlm import Atom, Clause, Const, KnowledgeBase, Rule, Theory, Var, closure  # noqa: E402
from dlm.selfsup import (  # noqa: E402
    MODES,
    StopPolicy,
    Task,
    program_sexp,
    reweight,
    run_loop,
)

MODES_ORDER = ("learn", "no_promote", "scramble", "random", "reward_hacking")


# ============================================================================
# the controlled composition task
# ============================================================================
def _edge_kb(nodes: int) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(nodes - 1):
        kb.add_fact(Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _exact_pairs(nodes: Sequence[int], distance: int) -> List[Tuple[int, int]]:
    ns = set(nodes)
    return sorted((a, a + distance) for a in nodes if a + distance in ns)


def _atom(pred: str, a: int, b: int) -> Atom:
    return Atom(pred, (Const(f"n{a}"), Const(f"n{b}")))


def _task(kb: KnowledgeBase, round_index: int, distance: int, train: Sequence[int], test: Sequence[int]) -> Task:
    pred = f"t{round_index}"
    pos = sorted((_atom(pred, a, b) for a, b in _exact_pairs(train, distance)), key=str)
    hit = set(_exact_pairs(train, distance))
    all_pairs = [(a, b) for a in train for b in train if a != b]
    neg = sorted((_atom(pred, a, b) for a, b in all_pairs if (a, b) not in hit), key=str)
    held_pos = sorted((_atom(pred, a, b) for a, b in _exact_pairs(test, distance)), key=str)
    held_neg = sorted(
        (_atom(pred, a, b) for a, b in [(a, b) for a in test for b in test if a != b] if abs(a - b) != distance),
        key=str,
    )
    return Task(pred, kb, tuple(pos), tuple(neg), tuple(held_pos), tuple(held_neg))


def _tasks(nodes: int) -> Tuple[Task, List[Task], List[int], List[int]]:
    kb = _edge_kb(nodes)
    half = nodes // 2
    train = list(range(0, half))
    test = list(range(half, nodes))
    rounds = 0
    while 2 ** (rounds + 1) <= half - 1:
        rounds += 1
    tasks = [_task(kb, r, 2 ** r, train, test) for r in range(1, rounds + 1)]
    return kb, tasks, train, test


# ============================================================================
# the oracle ceiling -- the true composition, given as a reference
# ============================================================================
def _oracle_theory(rounds: int) -> Theory:
    x, y, z = Var("x"), Var("y"), Var("z")
    clauses = [Clause(Rule(Atom("t1", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y))), "oracle_t1"), 1.0)]
    for r in range(2, rounds + 1):
        head = Atom(f"t{r}", (x, y))
        body = (Atom(f"t{r-1}", (x, z)), Atom(f"t{r-1}", (z, y)))
        clauses.append(Clause(Rule(head, body, f"oracle_t{r}"), 1.0))
    return Theory("oracle", tuple(clauses))


def _oracle_coverage(kb: KnowledgeBase, tasks: Sequence[Task], rounds: int) -> Dict[str, float]:
    theory = _oracle_theory(rounds)
    closed = closure(theory.to_kb(kb))
    proved = sum(len([a for a in t.held_pos if a in closed]) for t in tasks)
    total = sum(len(t.held_pos) for t in tasks)
    false = sum(len([a for a in t.held_neg if a in closed]) for t in tasks)
    return {"mean_held_coverage": round(proved / total if total else 0.0, 6), "false_assert": false}


# ============================================================================
# run one arm
# ============================================================================
def _arm(mode: str, tasks: Sequence[Task], rounds: int, *, budget: int, seed: int) -> Dict[str, object]:
    policy = StopPolicy(max_rounds=rounds, stop_on_no_proposal=False)
    result = run_loop(tasks, mode=mode, policy=policy, name="selfsup", budget=budget, seed=seed)
    # order the grown clauses (weights only: never structure/truth)
    grown, updates = reweight(result.theory, []) if result.theory.params else (result.theory, 0)
    return {
        "mode": mode,
        "rounds": result.rounds,
        "params": result.theory.params,
        "mean_held_coverage": round(result.mean_held_coverage, 6),
        "false_assert": result.false_assert,
        "promoted": list(result.promoted),
        "updates": updates,
        "trace": [s.to_dict() for s in result.stats],
        "theory_sexp": program_sexp(grown),
    }


def verdict(out: Dict[str, object]) -> List[str]:
    arms = out["arms"]
    learn = arms["learn"]
    lines = []
    improved = learn["mean_held_coverage"] >= 0.99 and learn["false_assert"] == 0
    lines.append(
        f"loop composes verified programs: learn held-coverage={learn['mean_held_coverage']:.3f} "
        f"false={learn['false_assert']} params={learn['params']} -> {'PASS' if improved else 'FAIL'}"
    )
    for name in ("no_promote", "scramble", "random"):
        a = arms[name]
        ok = a["mean_held_coverage"] <= 0.05
        lines.append(f"control {name} stays at floor: held={a['mean_held_coverage']:.3f} -> {'OK' if ok else 'LEAK'}")
    hack = arms["reward_hacking"]
    lines.append(
        f"gate-off arm fabricates: reward_hacking false={hack['false_assert']} "
        f"(gate is the anchor) -> {'OK' if hack['false_assert'] > 0 else 'NO SIGNAL'}"
    )
    oracle = out["oracle"]
    lines.append(
        f"oracle ceiling held={oracle['mean_held_coverage']:.3f} false={oracle['false_assert']} "
        f"(learn matches the true composition)"
    )
    return lines


def run(args: argparse.Namespace) -> Dict[str, object]:
    kb, tasks, train, test = _tasks(args.nodes)
    rounds = len(tasks)
    arms = {m: _arm(m, tasks, rounds, budget=args.budget, seed=args.seed) for m in MODES_ORDER}
    out: Dict[str, object] = {
        "config": {
            "nodes": args.nodes,
            "train_nodes": len(train),
            "test_nodes": len(test),
            "rounds": rounds,
            "distances": [2 ** r for r in range(1, rounds + 1)],
            "budget": args.budget,
            "seed": args.seed,
            "modes": list(MODES),
        },
        "arms": arms,
        "oracle": _oracle_coverage(kb, tasks, rounds),
    }
    out["verdict"] = verdict(out)
    return out


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nodes", type=int, default=80, help="chain length (train/test split at half)")
    p.add_argument("--budget", type=int, default=20000, help="induction candidate budget per round")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--quick", action="store_true", help="small smoke run (nodes=40)")
    p.add_argument("--json", type=str, default=None, help="write the report to this path")
    args = p.parse_args(argv)
    if args.quick:
        args.nodes = 40
    out = run(args)
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
