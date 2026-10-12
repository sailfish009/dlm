"""Execution control + experience-fed proof credit (DLM v0.0027, NOTE 79).

Question.  v0.0024 taught the loop to *learn rules* from kernel verdicts -- but a
clause's weight never reaches the kernel, and :func:`dlm.closure` is complete.  So
the learned order was **epiphenomenal**: it could reorder a candidate list but
could never change what is proved.  Can the loop instead learn to *run* what it
learned -- to spend a bounded search budget on the clauses that actually close
proofs?

Method.  ``dlm.execute`` adds a bounded backward-chaining interpreter.  At every
goal it tries the clauses the theory ranks highest first and spends a fixed number
of clause attempts.  The run leaves a readable trace; ``credits`` reads which
clause closed a proof (a hit) and which only spent budget (waste); the loop feeds
that per-clause credit back so the next round's order improves.

Task (controlled, kernel-labelled).  The v0.0024 composition chain: round ``r``
asks ``t_r`` = pairs at distance exactly ``2**r``; the loop must compose
``t_r(x,y):-t_{r-1}(x,z),t_{r-1}(z,y)`` from the previous round.  On top of the
induced clauses we inject one **over-specific decoy** per predicate: the correct
body plus the unsatisfiable literal ``e(z,z)``.  The decoy is sound (it derives
nothing false) but can never fire, so it is pure wasted budget.  Decoys carry the
same weight as the induced clause and sort first by name, so the *frozen* order
tries every decoy before the real clause.

Arms (same data, proposer, gate and budget; only the order / feedback differs)::

    frozen     induced weights, no feedback -- alphabetical tie-break (decoys first)
    feedback   per-step credit fed back into the weights (the method)
    scramble   hits and waste swapped -- mislearned order control
    random     order shuffled -- reward-blind control (averaged over seeds)

Also reported: a **clean** run without decoys (feedback must not hurt), a **budget
sweep** (the gap is a bounded-resource effect; at a large budget it closes), and a
readable execution trace with a kernel soundness check.

Run::

    PYTHONPATH=. python experiments/execution/run.py
    PYTHONPATH=. python experiments/execution/run.py --quick --json report.json
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

from dlm import Atom, Clause, Rule, Theory, Var  # noqa: E402
from dlm.execute import (  # noqa: E402
    check_sound,
    credits,
    execute,
    run_control_loop,
)
from experiments.selfsup.run import _tasks  # noqa: E402


# ============================================================================
# the decoys: sound but unsatisfiable clauses that only waste budget
# ============================================================================
def decoy_clauses(rounds: int) -> Tuple[Clause, ...]:
    """Per predicate ``t_r``: the correct body plus the impossible ``e(z,z)``.

    Sound (it implies the two real body atoms) but it can never fire, so it is
    the cleanest possible stress on *execution order*: a clause the scorer must
    learn to rank last.  Weight 1.0 ties the induced clause's coverage weight and
    the ``adecoy`` name sorts before ``lgg``, so the frozen order hits it first.
    """
    x, y, z = Var("x"), Var("y"), Var("z")
    out: List[Clause] = []
    for r in range(1, rounds + 1):
        prev = "e" if r == 1 else f"t{r - 1}"
        body = (
            Atom(prev, (x, z)),
            Atom(prev, (z, y)),
            Atom("e", (z, z)),  # impossible on a path: no self-loops
        )
        out.append(Clause(Rule(Atom(f"t{r}", (x, y)), body, f"adecoy_r{r}"), 1.0))
    return tuple(out)


# ============================================================================
# arms
# ============================================================================
def _arm(
    tasks,
    *,
    decoys: Sequence[Clause],
    feedback: bool,
    scramble: bool,
    order: str,
    budget: int,
    seed: int,
) -> Dict[str, object]:
    result = run_control_loop(
        tasks,
        feedback=feedback,
        scramble=scramble,
        order=order,
        executor_budget=budget,
        max_body=2,
        name="exec",
        seed=seed,
        decoys=tuple(decoys),
    )
    return {
        "feedback": feedback,
        "scramble": scramble,
        "order": order,
        "seed": seed,
        "budget": budget,
        "params": result.theory.params,
        "mean_coverage": round(result.mean_coverage, 6),
        "total_proved": result.total_proved,
        "total_goals": result.total_goals,
        "total_spent": sum(s.spent for s in result.stats),
        "false_assert": result.false_assert,
        "sound": result.sound,
        "total_updates": result.total_updates,
        "weights": {k: round(v, 4) for k, v in sorted(result.theory.weights().items())},
        "trace": [s.to_dict() for s in result.stats],
    }


def _random_arm(tasks, decoys, *, budget: int, seeds: Sequence[int]) -> Dict[str, object]:
    runs = [
        _arm(tasks, decoys=decoys, feedback=False, scramble=False, order="random", budget=budget, seed=s)
        for s in seeds
    ]
    covs = [r["mean_coverage"] for r in runs]
    spents = [r["total_spent"] for r in runs]
    return {
        "order": "random",
        "seeds": list(seeds),
        "mean_coverage": round(sum(covs) / len(covs), 6),
        "min_coverage": round(min(covs), 6),
        "max_coverage": round(max(covs), 6),
        "mean_spent": round(sum(spents) / len(spents), 3),
        "runs": runs,
    }


# ============================================================================
# the readable trace (the "understanding" claim, made inspectable)
# ============================================================================
def trace_demo(nodes: int = 20) -> Dict[str, object]:
    x, y, z = Var("x"), Var("y"), Var("z")
    kb, tasks, _, _ = _tasks(nodes)
    theory = Theory(
        "demo",
        (
            Clause(Rule(Atom("t1", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y))), "z_t1"), 1.0),
        ),
    )
    decoys = decoy_clauses(1)
    goals = tuple(sorted((tasks[0].held_pos), key=str))[:3]
    exec_theory = Theory("demo", theory.clauses + decoys)
    ex = execute(exec_theory.to_kb(kb), exec_theory, goals, budget=64, order="score")
    return {
        "goals": [str(g) for g in goals],
        "proved": len(ex.proved),
        "spent": ex.spent,
        "sound": check_sound(exec_theory.to_kb(kb), exec_theory, ex),
        "net_credit": credits(ex).net(),
        "trace": list(ex.explain()),
    }


# ============================================================================
# run
# ============================================================================
def run(args: argparse.Namespace) -> Dict[str, object]:
    nodes = args.nodes
    kb, tasks, train, test = _tasks(nodes)
    rounds = len(tasks)
    decoys = decoy_clauses(rounds)
    seeds = tuple(range(args.random_seeds))

    arms = {
        "frozen": _arm(tasks, decoys=decoys, feedback=False, scramble=False, order="score", budget=args.budget, seed=args.seed),
        "feedback": _arm(tasks, decoys=decoys, feedback=True, scramble=False, order="score", budget=args.budget, seed=args.seed),
        "scramble": _arm(tasks, decoys=decoys, feedback=True, scramble=True, order="score", budget=args.budget, seed=args.seed),
        "random": _random_arm(tasks, decoys, budget=args.budget, seeds=seeds),
    }
    # clean control: no decoys -> nothing to rank, feedback must not hurt
    clean = {
        "frozen": _arm(tasks, decoys=(), feedback=False, scramble=False, order="score", budget=args.budget, seed=args.seed),
        "feedback": _arm(tasks, decoys=(), feedback=True, scramble=False, order="score", budget=args.budget, seed=args.seed),
    }
    # budget sweep: the gap is a bounded-resource effect, not a correctness one
    sweep = []
    for budget in args.sweep:
        f = _arm(tasks, decoys=decoys, feedback=False, scramble=False, order="score", budget=budget, seed=args.seed)
        g = _arm(tasks, decoys=decoys, feedback=True, scramble=False, order="score", budget=budget, seed=args.seed)
        sweep.append(
            {
                "budget": budget,
                "frozen_coverage": f["mean_coverage"],
                "feedback_coverage": g["mean_coverage"],
                "frozen_spent": f["total_spent"],
                "feedback_spent": g["total_spent"],
            }
        )

    out: Dict[str, object] = {
        "config": {
            "nodes": nodes,
            "train_nodes": len(train),
            "test_nodes": len(test),
            "rounds": rounds,
            "distances": [2 ** r for r in range(1, rounds + 1)],
            "executor_budget": args.budget,
            "seed": args.seed,
            "random_seeds": list(seeds),
            "decoys": [c.name for c in decoys],
        },
        "arms": arms,
        "clean": clean,
        "budget_sweep": sweep,
        "trace_demo": trace_demo(args.trace_nodes),
    }
    out["verdict"] = verdict(out)
    return out


def verdict(out: Dict[str, object]) -> List[str]:
    arms = out["arms"]
    frozen = arms["frozen"]
    feedback = arms["feedback"]
    scramble = arms["scramble"]
    lines: List[str] = []
    better = (feedback["mean_coverage"] >= frozen["mean_coverage"] - 1e-9) and (
        feedback["mean_coverage"] > frozen["mean_coverage"] + 1e-9
        or feedback["total_spent"] < frozen["total_spent"]
    )
    lines.append(
        f"experience feedback improves bounded execution: frozen={frozen['mean_coverage']:.3f} "
        f"feedback={feedback['mean_coverage']:.3f} (spent {frozen['total_spent']} -> {feedback['total_spent']}) "
        f"-> {'PASS' if better else 'FAIL'}"
    )
    noharm = out["clean"]["feedback"]["mean_coverage"] >= out["clean"]["frozen"]["mean_coverage"] - 1e-9
    lines.append(
        f"feedback does not hurt the clean (no-decoy) run: "
        f"{out['clean']['frozen']['mean_coverage']:.3f} -> {out['clean']['feedback']['mean_coverage']:.3f} "
        f"-> {'OK' if noharm else 'HURT'}"
    )
    lines.append(
        f"scrambled credit does not help: scramble={scramble['mean_coverage']:.3f} "
        f"-> {'OK' if scramble['mean_coverage'] <= frozen['mean_coverage'] + 1e-9 else 'LEAK'}"
    )
    last = out["budget_sweep"][-1]
    lines.append(
        f"the gap is bounded-resource: at budget={last['budget']} "
        f"frozen={last['frozen_coverage']:.3f} feedback={last['feedback_coverage']:.3f}"
    )
    trace = out["trace_demo"]
    lines.append(
        f"traces are readable and kernel-sound: {trace['proved']}/{len(trace['goals'])} proved, "
        f"sound={trace['sound']}, spent={trace['spent']}"
    )
    allsound = all(a.get("sound", True) for a in (arms["frozen"], arms["feedback"], arms["scramble"]))
    lines.append(f"every execution is a subset of the kernel closure: {allsound} -> {'OK' if allsound else 'UNSOUND'}")
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nodes", type=int, default=64, help="chain length (train/test split at half)")
    p.add_argument("--budget", type=int, default=400, help="executor clause-attempt budget per round")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--random-seeds", type=int, default=5, help="number of random-order seeds to average")
    p.add_argument("--sweep", type=int, nargs="*", default=[200, 400, 800, 2000], help="budget sweep")
    p.add_argument("--trace-nodes", type=int, default=20)
    p.add_argument("--quick", action="store_true", help="small smoke run")
    p.add_argument("--json", type=str, default=None, help="write the report to this path")
    args = p.parse_args(argv)
    if args.quick:
        args.nodes = 32
        args.sweep = [100, 200, 400]
    out = run(args)
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
