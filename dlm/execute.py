"""DLM v0.0027 -- a bounded, order-sensitive executor + proof credit (untrusted).

The fused core's :func:`dlm.closure` is **complete**, and a clause's weight never
reaches the kernel -- so the learned order is *epiphenomenal*: it can reorder a
candidate list (:func:`dlm.solve`) but cannot change what is proved.  That is why
v0.0024's loop learned *rules* but never learned *how to judge or route them*.

This module gives the order something to control.  :func:`execute` is a bounded
backward-chaining (SLD) interpreter: at each goal it tries the clauses the theory
ranks highest first and spends a fixed budget of clause attempts.  Now a good
order proves more within budget, and the kernel still verifies.

The second half is the feedback that was missing.  A run leaves a readable
:class:`Execution` trace -- which clause closed a proof, which clause only spent
budget -- and :func:`credits` turns that into a per-clause experience signal.
:func:`run_control_loop` feeds that signal back into the fused learner
(:func:`apply_credit`) after every round, so the order the executor uses
next time is shaped by the loop's own experience.

Trust invariant: the executor only *orders* clause attempts.  It never adds a
fact or a rule.  :func:`check_sound` re-checks every proved goal against the
kernel closure, and the same symbols a proof uses are the ones the kernel already
verifies.

v0.0028 adds an optional ``scorer(goal, clause) -> float`` seam: a goal-conditioned
order supplied by :mod:`dlm.control` (one-way -- this module does not import it).
It only replaces *how* attempts are ranked; the budget, the trace and the kernel
gate are unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from dlm import Atom, Clause, Rule, Theory, Var, apply_atom, closure, unify
from dlm.selfsup import evaluate, promote, propose

__all__ = [
    "Step",
    "Execution",
    "execute",
    "check_sound",
    "Credit",
    "credits",
    "experience_pairs",
    "pairs_from_credit",
    "apply_credit",
    "ControlRound",
    "ControlResult",
    "run_control_loop",
]


# ============================================================================
# 1. the observed execution: one readable trace of an attempt
# ============================================================================
@dataclass(frozen=True)
class Step:
    """One clause-application attempt in the executor's search."""

    goal: Atom
    clause: Optional[str]
    ok: bool
    depth: int

    def to_dict(self) -> dict:
        return {
            "goal": str(self.goal),
            "clause": self.clause,
            "ok": self.ok,
            "depth": self.depth,
        }


@dataclass(frozen=True)
class Execution:
    """The result of executing a goal list under a budget -- a full trace.

    ``proved`` is the subset of ``goals`` the executor closed within budget;
    ``steps`` is *how* it got there (the observation the model can read and learn
    from); ``exhausted`` says the budget ran out before the goals were settled.
    """

    goals: Tuple[Atom, ...]
    proved: Tuple[Atom, ...]
    steps: Tuple[Step, ...]
    spent: int
    budget: int
    exhausted: bool

    @property
    def coverage(self) -> float:
        return len(self.proved) / len(self.goals) if self.goals else 0.0

    def explain(self) -> Tuple[str, ...]:
        out: List[str] = []
        for s in self.steps:
            mark = "OK " if s.ok else "-- "
            out.append(f"{mark}{'  ' * s.depth}{s.clause or 'fact'} <- {s.goal}")
        return tuple(out)

    def to_dict(self) -> dict:
        return {
            "goals": len(self.goals),
            "proved": len(self.proved),
            "spent": self.spent,
            "budget": self.budget,
            "exhausted": self.exhausted,
            "coverage": round(self.coverage, 6),
            "steps": [s.to_dict() for s in self.steps],
        }


# ============================================================================
# 2. the executor (untrusted): order the attempts, never assert
# ============================================================================
def _freshen_rule(rule: Rule, prefix: str) -> Rule:
    """Rename every variable of ``rule`` apart, deterministically."""
    mapping: Dict[Var, Var] = {}

    def fresh(atom: Atom) -> Atom:
        args: List = []
        for t in atom.args:
            if isinstance(t, Var):
                if t not in mapping:
                    mapping[t] = Var(f"{prefix}{len(mapping)}")
                args.append(mapping[t])
            else:
                args.append(t)
        return Atom(atom.pred, tuple(args))

    return Rule(fresh(rule.head), tuple(fresh(b) for b in rule.body), rule.name)


def execute(
    kb,
    theory: Theory,
    goals,
    *,
    budget: int = 100000,
    max_depth: int = 64,
    order: str = "score",
    rng: Optional[Random] = None,
    scorer: Optional[Callable[[Atom, Clause], float]] = None,
) -> Execution:
    """Bounded backward chaining: try the theory's best clauses first.

    ``order="score"`` uses the learned clause weights (the model's policy),
    ``"name"`` is the frozen alphabetical baseline, ``"random"`` is the
    reward-blind control.  The budget counts clause-application attempts, so a
    better order settles more goals before the budget runs out.

    ``scorer`` (v0.0028 seam, untrusted) overrides the order with a *goal-conditioned*
    score ``scorer(goal, clause) -> float``: the same clause can be ranked first for
    one goal and last for another.  It still only orders attempts -- it never adds a
    fact or rule, so :func:`check_sound` is unchanged.
    """
    goals = tuple(goals)
    spent = 0
    steps: List[Step] = []
    proved: List[Atom] = []
    exhausted = False
    memo: Dict[Atom, bool] = {}
    by_pred: Dict[str, List] = {}
    for c in theory.clauses:
        by_pred.setdefault(c.rule.head.pred, []).append(c)

    def candidates(goal: Atom) -> List:
        cands = [c for c in by_pred.get(goal.pred, ()) if c.rule.head.arity == goal.arity]
        if scorer is not None:
            return sorted(cands, key=lambda c: (-scorer(goal, c), c.name))
        if order == "name":
            return sorted(cands, key=lambda c: c.name)
        if order == "random":
            out = list(cands)
            if rng is not None:
                rng.shuffle(out)
            return out
        return sorted(cands, key=lambda c: (-c.weight, c.name))

    def solve_body(body, subst, depth: int):
        s = subst
        for atom in body:
            s = solve(atom, s, depth)
            if s is None:
                return None
        return s

    def solve(goal: Atom, subst, depth: int):
        nonlocal spent, exhausted
        g = apply_atom(goal, subst)
        if g.is_ground() and (kb.has_fact(g) or memo.get(g, False)):
            return subst
        if depth >= max_depth:
            return None
        for fact in kb.facts_by_pred(g.pred):
            if fact.arity != g.arity:
                continue
            s2 = unify(g, fact, subst)
            if s2 is not None:
                return s2
        for clause in candidates(g):
            if spent >= budget:
                exhausted = True
                return None
            spent += 1
            fresh = _freshen_rule(clause.rule, f"__x{spent}_")
            s2 = unify(g, fresh.head, subst)
            if s2 is None:
                steps.append(Step(g, clause.name, False, depth))
                continue
            s3 = solve_body(fresh.body, s2, depth + 1)
            if s3 is not None:
                steps.append(Step(g, clause.name, True, depth))
                if g.is_ground():
                    memo[g] = True
                return s3
            steps.append(Step(g, clause.name, False, depth))
        return None

    for goal in goals:
        if goal.is_ground() and (kb.has_fact(goal) or memo.get(goal, False)):
            proved.append(goal)
            continue
        if solve(goal, {}, 0) is not None:
            proved.append(goal)
        if exhausted:
            break
    return Execution(goals, tuple(proved), tuple(steps), spent, budget, exhausted)


def check_sound(kb, theory: Theory, execution: Execution) -> bool:
    """Trust check: every proved goal must lie in the kernel's closure."""
    closed = closure(theory.to_kb(kb))
    return all(g in closed for g in execution.proved)


# ============================================================================
# 3. experience: turn the trace into per-clause credit
# ============================================================================
@dataclass(frozen=True)
class Credit:
    """Per-clause experience: how often each clause closed a proof vs only spent."""

    hits: Dict[str, int]
    waste: Dict[str, int]

    def net(self) -> Dict[str, int]:
        keys = sorted(set(self.hits) | set(self.waste))
        return {k: self.hits.get(k, 0) - self.waste.get(k, 0) for k in keys}

    def to_dict(self) -> dict:
        return {"hits": dict(sorted(self.hits.items())), "waste": dict(sorted(self.waste.items())), "net": self.net()}


def credits(execution: Execution) -> Credit:
    """Read the trace: a successful attempt is a hit, a failed one is waste."""
    hits: Dict[str, int] = {}
    waste: Dict[str, int] = {}
    for step in execution.steps:
        if step.clause is None:
            continue
        table = hits if step.ok else waste
        table[step.clause] = table.get(step.clause, 0) + 1
    return Credit(hits, waste)


def pairs_from_credit(theory: Theory, credit: Credit) -> Tuple[Tuple[Rule, Rule], ...]:
    """Positive/negative rule pairs from per-clause credit (used by the loop)."""
    rules = {c.name: c.rule for c in theory.clauses}
    net = credit.net()
    pos = [rules[n] for n, v in net.items() if v > 0 and n in rules]
    neg = [rules[n] for n, v in net.items() if v < 0 and n in rules]
    return tuple((p, n) for p in pos for n in neg)


def experience_pairs(theory: Theory, execution: Execution) -> Tuple[Tuple[Rule, Rule], ...]:
    """Positive/negative rule pairs for the fused perceptron, from the trace.

    A clause with net positive credit is a positive example, a clause with net
    negative credit a negative example; the hard-negative perceptron then pushes
    the helpful clauses above the wasteful ones.  Clauses with zero net credit are
    left alone.
    """
    return pairs_from_credit(theory, credits(execution))


def apply_credit(theory: Theory, credit: Credit, *, lr: float = 0.1) -> Theory:
    """Direct credit update: ``weight += lr * (hits - waste)`` per clause."""
    weights = theory.weights()
    for name, delta in credit.net().items():
        if name in weights:
            weights[name] = weights[name] + lr * delta
    return theory.with_weights(weights)


# ============================================================================
# 4. the experience-fed loop: propose -> gate -> execute -> credit
# ============================================================================
@dataclass(frozen=True)
class ControlRound:
    """One round of the control loop: what was learned and how execution went."""

    round: int
    name: str
    proposed: int
    accepted: bool
    promoted: Tuple[str, ...]
    held_false: int
    exec_proved: int
    exec_total: int
    spent: int
    budget: int
    exhausted: bool
    updates: int
    feedback: bool
    sound: bool

    @property
    def coverage(self) -> float:
        return self.exec_proved / self.exec_total if self.exec_total else 0.0

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "name": self.name,
            "proposed": self.proposed,
            "accepted": self.accepted,
            "promoted": list(self.promoted),
            "held_false": self.held_false,
            "exec_proved": self.exec_proved,
            "exec_total": self.exec_total,
            "spent": self.spent,
            "budget": self.budget,
            "exhausted": self.exhausted,
            "updates": self.updates,
            "feedback": self.feedback,
            "sound": self.sound,
            "coverage": round(self.coverage, 6),
        }


@dataclass(frozen=True)
class ControlResult:
    """The whole control run: the grown theory and the per-round execution trace."""

    theory: Theory
    stats: Tuple[ControlRound, ...]

    @property
    def rounds(self) -> int:
        return len(self.stats)

    @property
    def false_assert(self) -> int:
        return sum(s.held_false for s in self.stats)

    @property
    def sound(self) -> bool:
        return all(s.sound for s in self.stats)

    @property
    def total_proved(self) -> int:
        return sum(s.exec_proved for s in self.stats)

    @property
    def total_goals(self) -> int:
        return sum(s.exec_total for s in self.stats)

    @property
    def mean_coverage(self) -> float:
        return self.total_proved / self.total_goals if self.total_goals else 0.0

    @property
    def total_updates(self) -> int:
        return sum(s.updates for s in self.stats)

    def to_dict(self) -> dict:
        return {
            "rounds": self.rounds,
            "params": self.theory.params,
            "false_assert": self.false_assert,
            "sound": self.sound,
            "mean_coverage": round(self.mean_coverage, 6),
            "total_proved": self.total_proved,
            "total_goals": self.total_goals,
            "total_updates": self.total_updates,
            "weights": {k: round(v, 6) for k, v in sorted(self.theory.weights().items())},
            "trace": [s.to_dict() for s in self.stats],
        }


def run_control_loop(
    tasks,
    *,
    feedback: bool = True,
    scramble: bool = False,
    order: str = "score",
    executor_budget: int = 100000,
    max_body: int = 2,
    extra_vars: int = 1,
    max_arity: int = 3,
    induction_budget: int = 20000,
    cost: float = 0.02,
    lr: float = 0.1,
    seed: int = 0,
    name: str = "control",
    initial: Optional[Theory] = None,
    max_rounds: Optional[int] = None,
    decoys: Sequence[Clause] = (),
    scorer: Optional[Callable[[Atom, Clause], float]] = None,
) -> ControlResult:
    """Grow a theory, then learn *how to run it* from the execution trace.

    Each round: propose with the fused inducer, gate on the kernel reward, promote
    the sound clauses, then execute the held-out goals under a fixed budget.  When
    ``feedback`` is on, the trace's per-clause credit is fed back through the fused
    perceptron so the next round's order prefers the clauses that actually closed
    proofs.  ``scramble`` swaps hits and waste -- the mislearned-order control.
    """
    tasks = tuple(tasks)
    if max_rounds is not None:
        tasks = tasks[:max_rounds]
    theory = initial if initial is not None else Theory(name, ())
    rng = Random(seed)
    stats = []
    for index, task in enumerate(tasks):
        kb = theory.to_kb(task.kb)
        program = propose(
            kb,
            task.positives,
            task.negatives,
            max_body=max_body,
            extra_vars=extra_vars,
            max_arity=max_arity,
            budget=induction_budget,
        )
        verdict = evaluate(kb, program, task.positives, task.negatives, cost=cost)
        accepted = verdict.sound and verdict.coverage > 0.0 and verdict.reward >= 0.0
        promoted: Tuple[str, ...] = ()
        if accepted and program:
            before = set(theory.names())
            theory = promote(theory, program)
            promoted = tuple(n for n in theory.names() if n not in before)

        # execution candidates = what the loop learned + the injected decoys;
        # decoys never enter the induction KB, so they cannot seed the proposer.
        exec_theory = Theory(theory.name, theory.clauses + tuple(decoys))
        exec_kb = exec_theory.to_kb(task.kb)
        execution = execute(
            exec_kb,
            exec_theory,
            task.held_pos,
            budget=executor_budget,
            order=order,
            rng=rng,
            scorer=scorer,
        )
        sound = check_sound(exec_kb, exec_theory, execution)

        updates = 0
        if feedback and order == "score":
            # Exact per-step credit: the trace already says which clause closed a
            # proof and which one only spent budget.  We update each clause by its
            # own net credit -- the fused `matched`/`subsumes` view would smear a
            # general clause with the waste of every over-specific rule it covers.
            credit = credits(execution)
            if scramble:
                credit = Credit(credit.waste, credit.hits)
            updated = apply_credit(exec_theory, credit, lr=lr)
            theory = theory.with_weights(updated.weights())
            updates = sum(1 for v in credit.net().values() if v != 0)

        closed = closure(theory.to_kb(task.kb))
        held_false = len(set(task.held_neg) & closed)
        stats.append(
            ControlRound(
                round=index,
                name=task.name,
                proposed=len(program),
                accepted=bool(accepted),
                promoted=promoted,
                held_false=held_false,
                exec_proved=len(execution.proved),
                exec_total=len(execution.goals),
                spent=execution.spent,
                budget=execution.budget,
                exhausted=execution.exhausted,
                updates=updates,
                feedback=bool(feedback and order == "score"),
                sound=sound,
            )
        )
    return ControlResult(theory, tuple(stats))
