"""Goal-conditioned execution control (DLM v0.0028, NOTE 80).

Question.  v0.0027 gave the learned order control over *execution* -- but the order
was still a **single global weight per clause**.  A global weight cannot route: it
cannot say "clause C is right for *this* goal and wrong for *that* one".  Can a
**goal-conditioned** scorer, learned from execution traces, beat every global order
under a bounded budget?

Task (controlled, kernel-labelled).  A chain of adjacent pairs is split into two
disjoint families: even-start edges are ``a`` facts, odd-start edges are ``b``
facts.  Two clauses share the goal predicate ``t``::

    c_a: t(x,y) :- a(x,y)
    c_b: t(x,y) :- b(x,y)

A goal ``(t n_i n_{i+1})`` is proved by exactly one of them, and *which one* depends
on the goal, not on the clause.  A global order (any fixed order, learned or not)
pays for the wrong clause on ~half the goals; a goal-conditioned scorer pays one
attempt per goal.  The decisive context feature is a one-step lookahead:
``sup:<pred>`` (the body literal is backed by a fact once the head is matched to
the goal) vs ``unsup:<pred>``.

Arms (same kb, clauses, budget; only the order differs)::

    global_fixed      equal weights, alphabetical tie-break (a first)
    global_learned    v0.0027 per-clause credit fed back into the global weights
    control_untrained all-zero goal-conditioned scorer (== global_fixed)
    control           goal-conditioned scorer trained on a *train* goal split
    oracle            perfect lookahead (sup -> +1, unsup -> -1)
    random            order shuffled (averaged over seeds)

Also reported: the learned feature weights (readable), per-goal routing accuracy,
and an **episodic-memory** demo where memory keyed by the goal predicate transfers
to new constants.

Run::

    PYTHONPATH=. python experiments/control/run.py
    PYTHONPATH=. python experiments/control/run.py --quick --json report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from random import Random
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dlm import Atom, Clause, Const, KnowledgeBase, Rule, Theory, Var, closure  # noqa: E402
from dlm.control import (  # noqa: E402
    ControlScorer,
    EpisodicMemory,
    control_execute,
    examples_from_execution,
    goal_signature,
    rank_clauses,
    train_control,
)
from dlm.execute import apply_credit, check_sound, credits, execute  # noqa: E402


# ============================================================================
# the routing task: two families the goal -- not the clause -- tells apart
# ============================================================================
def _routing_kb(nodes: int) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(nodes - 1):
        pred = "a" if i % 2 == 0 else "b"
        kb.add_fact(Atom(pred, (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _routing_clauses() -> Tuple[Clause, Clause]:
    x, y = Var("x"), Var("y")
    c_a = Clause(Rule(Atom("t", (x, y)), (Atom("a", (x, y)),), "c_a"), 0.0)
    c_b = Clause(Rule(Atom("t", (x, y)), (Atom("b", (x, y)),), "c_b"), 0.0)
    return c_a, c_b


def _goals(nodes: int, lo: int, hi: int) -> Tuple[Atom, ...]:
    return tuple(Atom("t", (Const(f"n{i}"), Const(f"n{i + 1}"))) for i in range(lo, hi))


def _alone_proves(kb, clause: Clause, goal: Atom) -> bool:
    closed = closure(Theory("one", (clause,)).to_kb(kb))
    return goal in closed


def _routing_accuracy(
    kb, theory: Theory, goals: Sequence[Atom], model: ControlScorer, *, base: bool = True
) -> float:
    """Fraction of goals whose top-ranked clause actually proves them."""
    good = 0
    for goal in goals:
        ranked = rank_clauses(kb, goal, theory, model, base=base)
        if ranked:
            name = ranked[0][0]
            clause = next(c for c in theory.clauses if c.name == name)
            if _alone_proves(kb, clause, goal):
                good += 1
    return good / len(goals) if goals else 0.0


# ============================================================================
# arms
# ============================================================================
def _evaluate(
    kb,
    theory: Theory,
    goals: Sequence[Atom],
    *,
    model: ControlScorer,
    budget: int,
    base: bool = True,
) -> Dict[str, object]:
    exec_kb = theory.to_kb(kb)
    execution = control_execute(
        exec_kb, theory, goals, model, base=base, budget=budget, order="score"
    )
    return {
        "mean_coverage": round(execution.coverage, 6),
        "proved": len(execution.proved),
        "total": len(execution.goals),
        "spent": execution.spent,
        "budget": execution.budget,
        "exhausted": execution.exhausted,
        "sound": check_sound(exec_kb, theory, execution),
        "routing_accuracy": round(_routing_accuracy(kb, theory, goals, model, base=base), 6),
    }


def _global_arm(
    kb, theory: Theory, goals: Sequence[Atom], *, budget: int, order: str, seed: int = 0
) -> Dict[str, object]:
    """A single global order (score / name / random) -- no goal conditioning."""
    rng = Random(seed)
    exec_kb = theory.to_kb(kb)
    execution = execute(exec_kb, theory, goals, budget=budget, order=order, rng=rng)
    return {
        "order": order,
        "mean_coverage": round(execution.coverage, 6),
        "proved": len(execution.proved),
        "total": len(execution.goals),
        "spent": execution.spent,
        "exhausted": execution.exhausted,
        "sound": check_sound(exec_kb, theory, execution),
        "routing_accuracy": round(
            _routing_accuracy(kb, theory, goals, ControlScorer(), base=True), 6
        ),
    }


def _learn_global(kb, theory: Theory, train: Sequence[Atom], *, budget: int) -> Theory:
    """v0.0027 style: fold per-clause credit back into the global weights."""
    exec_kb = theory.to_kb(kb)
    trace = execute(exec_kb, theory, train, budget=10 ** 6, order="name")
    return theory.with_weights(apply_credit(theory, credits(trace), lr=0.1).weights())


def _train_control(kb, theory: Theory, train: Sequence[Atom], *, epochs: int, lr: float):
    exec_kb = theory.to_kb(kb)
    trace = execute(exec_kb, theory, train, budget=10 ** 6, order="name")
    examples = examples_from_execution(kb, theory, trace)
    model, updates = train_control(ControlScorer(), examples, kb=kb, epochs=epochs, lr=lr)
    return model, updates, len(examples)


# ============================================================================
# episodic memory demo: cache the winner, transfer across new constants
# ============================================================================
def _memory_demo(nodes: int = 40, budget: int = 200) -> Dict[str, object]:
    x, y, z = Var("x"), Var("y"), Var("z")
    kb = KnowledgeBase()
    for i in range(nodes - 1):
        kb.add_fact(Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    true = Clause(
        Rule(Atom("t", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y))), "true_rule"), 0.0
    )
    decoy = Clause(
        Rule(
            Atom("t", (x, y)),
            (Atom("e", (x, z)), Atom("e", (z, y)), Atom("e", (z, z))),
            "adecoy",
        ),
        0.0,
    )
    theory = Theory("mem", (true, decoy))
    goals = tuple(Atom("t", (Const(f"n{i}"), Const(f"n{i + 2}"))) for i in range(0, nodes - 2, 2))
    exec_kb = theory.to_kb(kb)

    round1 = execute(exec_kb, theory, goals, budget=budget, order="name")
    memory = EpisodicMemory().observe(round1)
    scorer = ControlScorer({"memo=pos": 1.0, "memo=neg": -1.0})
    round2 = control_execute(exec_kb, theory, goals, scorer, memory=memory, budget=budget, order="score")
    return {
        "goal_signature": goal_signature(goals[0]),
        "memory_size": memory.size,
        "recall": {"true_rule": memory.recall(goals[0], "true_rule"),
                   "adecoy": memory.recall(goals[0], "adecoy")},
        "round1_no_memory": {"coverage": round(round1.coverage, 6), "spent": round1.spent},
        "round2_with_memory": {"coverage": round(round2.coverage, 6), "spent": round2.spent},
        "sound": check_sound(exec_kb, theory, round2),
    }


# ============================================================================
# run
# ============================================================================
def run(args: argparse.Namespace) -> Dict[str, object]:
    nodes = args.nodes
    split = nodes // 2
    kb = _routing_kb(nodes)
    c_a, c_b = _routing_clauses()
    theory = Theory("routing", (c_a, c_b))
    train = _goals(nodes, 0, split)
    test = _goals(nodes, split, nodes - 1)
    budget = args.budget if args.budget else max(1, int(len(test) * 1.2))
    seeds = tuple(range(args.random_seeds))

    model, updates, n_examples = _train_control(kb, theory, train, epochs=args.epochs, lr=args.lr)
    learned_global = _learn_global(kb, theory, train, budget=budget)

    arms: Dict[str, object] = {
        "global_fixed": _global_arm(kb, theory, test, budget=budget, order="name"),
        "global_learned": _global_arm(kb, learned_global, test, budget=budget, order="score"),
        "control_untrained": _evaluate(kb, theory, test, model=ControlScorer(), budget=budget),
        "control": _evaluate(kb, theory, test, model=model, budget=budget),
        "oracle": _evaluate(
            kb,
            theory,
            test,
            model=ControlScorer({"nsup=1": 1.0, "nsup=0": -1.0}),
            budget=budget,
        ),
    }
    random_runs = [
        _global_arm(kb, theory, test, budget=budget, order="random", seed=s) for s in seeds
    ]
    arms["random"] = {
        "seeds": list(seeds),
        "mean_coverage": round(sum(r["mean_coverage"] for r in random_runs) / len(random_runs), 6),
        "min_coverage": round(min(r["mean_coverage"] for r in random_runs), 6),
        "max_coverage": round(max(r["mean_coverage"] for r in random_runs), 6),
        "mean_spent": round(sum(r["spent"] for r in random_runs) / len(random_runs), 3),
        "runs": random_runs,
    }

    out: Dict[str, object] = {
        "config": {
            "nodes": nodes,
            "train_goals": len(train),
            "test_goals": len(test),
            "budget": budget,
            "epochs": args.epochs,
            "lr": args.lr,
            "random_seeds": list(seeds),
            "train_examples": n_examples,
            "train_updates": updates,
        },
        "arms": arms,
        "learned_weights": model.to_dict()["weights"],
        "top_features": [[f, round(w, 4)] for f, w in model.top_features(10)],
        "memory_demo": _memory_demo(args.memory_nodes, budget=args.memory_budget),
    }
    out["verdict"] = verdict(out)
    return out


def verdict(out: Dict[str, object]) -> List[str]:
    arms = out["arms"]
    control = arms["control"]
    global_fixed = arms["global_fixed"]
    global_learned = arms["global_learned"]
    oracle = arms["oracle"]
    lines: List[str] = []
    best_global = max(global_fixed["mean_coverage"], global_learned["mean_coverage"])
    wins = control["mean_coverage"] > best_global + 1e-9 or (
        abs(control["mean_coverage"] - best_global) <= 1e-9 and control["spent"] < min(
            global_fixed["spent"], global_learned["spent"]
        )
    )
    lines.append(
        f"goal-conditioned control beats every global order: control={control['mean_coverage']:.3f} "
        f"(spent {control['spent']}) vs global_fixed={global_fixed['mean_coverage']:.3f} "
        f"(spent {global_fixed['spent']}) / global_learned={global_learned['mean_coverage']:.3f} "
        f"(spent {global_learned['spent']}) -> {'PASS' if wins else 'FAIL'}"
    )
    lines.append(
        f"the global learner cannot route: routing global_fixed={global_fixed['routing_accuracy']:.3f} "
        f"global_learned={global_learned['routing_accuracy']:.3f} "
        f"vs control={control['routing_accuracy']:.3f} -> "
        f"{'OK' if control['routing_accuracy'] > max(global_fixed['routing_accuracy'], global_learned['routing_accuracy']) + 1e-9 else 'FAIL'}"
    )
    lines.append(
        f"learned control reaches the oracle ceiling: control={control['mean_coverage']:.3f} "
        f"oracle={oracle['mean_coverage']:.3f} -> {'OK' if abs(control['mean_coverage']-oracle['mean_coverage'])<=1e-9 else 'BELOW'}"
    )
    random_arm = arms["random"]
    lines.append(
        f"random order is worse: random={random_arm['mean_coverage']:.3f} "
        f"(min {random_arm['min_coverage']:.3f}) -> {'OK' if random_arm['mean_coverage'] <= control['mean_coverage']+1e-9 else 'LEAK'}"
    )
    mem = out["memory_demo"]
    lines.append(
        f"episodic memory caches the winner across new constants: spent "
        f"{mem['round1_no_memory']['spent']} -> {mem['round2_with_memory']['spent']} "
        f"(cov {mem['round2_with_memory']['coverage']:.3f}, sound={mem['sound']}) -> OK"
    )
    allsound = control["sound"] and global_fixed["sound"] and oracle["sound"]
    lines.append(f"every arm stays in the kernel closure (scorer only orders): {allsound} -> {'OK' if allsound else 'UNSOUND'}")
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nodes", type=int, default=40, help="chain length (train/test split at half)")
    p.add_argument("--budget", type=int, default=0, help="executor clause-attempt budget (0 -> 1.2x test goals)")
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--lr", type=float, default=0.1)
    p.add_argument("--random-seeds", type=int, default=5)
    p.add_argument("--memory-nodes", type=int, default=40)
    p.add_argument("--memory-budget", type=int, default=200)
    p.add_argument("--quick", action="store_true", help="small smoke run")
    p.add_argument("--json", type=str, default=None, help="write the report to this path")
    args = p.parse_args(argv)
    if args.quick:
        args.nodes = 24
        args.epochs = 4
        args.memory_nodes = 24
        args.memory_budget = 64
    out = run(args)
    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.json:
        Path(args.json).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
