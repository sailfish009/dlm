"""DLM v0.0024 -- the verifiable-reward self-supervised loop (untrusted layer).

The fused core (:mod:`dlm.deductive`) already turns kernel verdicts into labels
and reweights clauses.  What was *missing* is the loop that closes the circle:

    propose a program  ->  the kernel verifies it  ->  reward filters it
          ^                                                   |
          |                                                   v
          +----  only verified programs are promoted  <--------
                 (the theory becomes the next round's environment)

A "program" here is a set of :class:`~dlm.Clause` -- i.e. Lisp-like code
(``(clause <name> <weight> (head) (body)...)``).  The proposer is
:func:`~dlm.induce_clauses` (LGG + greedy covering); the verifier/reward is the
kernel's :func:`~dlm.closure`; the learner is :func:`~dlm.learn`; the growing
program is a :class:`~dlm.Theory`.  Fusing them gives one self-supervised loop,
driven by **zero human labels** -- the reward is exactly "did the kernel derive
every positive and no negative".

Trust invariant (unchanged): promotion adds *structure* (rules) only.  A clause
weight is order and never reaches the kernel; the proposer never asserts.  The
reward is a *hard* gate: any false assertion makes a program worthless.

Controls, so a gain can be attributed to the reward and not to the loop itself:

* ``learn``       -- propose, verify, promote verified programs (the method);
* ``no_promote``  -- propose and verify but never feed back (no loop);
* ``scramble``    -- the label source is shuffled, so the reward is misaligned;
* ``random``      -- promote a random program regardless of the reward.

This is expert iteration / rejection sampling over programs, not policy
gradient: when the verifier is exact and free, filtering verified programs is
cheaper and more stable than a gradient.  Exploration for genuinely *new*
programs is a separate, later problem.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from random import Random
from typing import Optional, Sequence, Tuple

from . import (
    Atom,
    Clause,
    KnowledgeBase,
    Rule,
    Theory,
    Var,
    closure,
    induce_clauses,
    learn,
    lgg_atoms,
    literal_space,
    theory_sexp,
    variate,
)


__all__ = [
    "Verdict",
    "Task",
    "RoundStats",
    "StopPolicy",
    "LoopResult",
    "evaluate",
    "propose",
    "promote",
    "random_program",
    "sloppy_program",
    "scramble_task",
    "decide_stop",
    "run_loop",
    "reweight",
    "program_sexp",
    "MODES",
]

MODES = ("learn", "no_promote", "scramble", "random", "reward_hacking")


# ============================================================================
# 1. the reward: an exact, hard kernel verdict
# ============================================================================
@dataclass(frozen=True)
class Verdict:
    """What the kernel says about one proposed program."""

    proved: int
    total: int
    false_assert: int
    size: int
    reward: float

    @property
    def sound(self) -> bool:
        return self.false_assert == 0

    @property
    def coverage(self) -> float:
        return self.proved / self.total if self.total else 0.0

    def to_dict(self) -> dict:
        return {
            "proved": self.proved,
            "total": self.total,
            "false_assert": self.false_assert,
            "size": self.size,
            "reward": round(self.reward, 6),
            "sound": self.sound,
            "coverage": round(self.coverage, 6),
        }


def evaluate(
    kb: KnowledgeBase,
    program: Sequence[Clause],
    positives: Sequence[Atom],
    negatives: Sequence[Atom],
    *,
    cost: float = 0.02,
) -> Verdict:
    """The verifiable reward: kernel closure of ``kb + program`` vs pos/neg.

    ``false_assert`` is a hard gate -- a single derived negative collapses the
    reward to ``-1`` regardless of coverage.  Otherwise reward is coverage minus
    an Occam cost per clause, so the loop prefers the shortest sound program.
    """
    program = tuple(program)
    trial = kb.copy()
    for clause in program:
        trial.add_rule(clause.rule)  # idempotent; structure only
    closed = closure(trial)
    pos = set(positives)
    neg = set(negatives)
    proved = len(pos & closed)
    false = len(neg & closed)
    total = len(pos)
    if false:
        reward = -1.0
    else:
        reward = (proved / total if total else 0.0) - cost * len(program)
    return Verdict(proved, total, false, len(program), reward)


# ============================================================================
# 2. one round of evidence (a task) and its statistics
# ============================================================================
@dataclass(frozen=True)
class Task:
    """One round's evidence: a base KB, train pos/neg and a held-out probe set."""

    name: str
    kb: KnowledgeBase
    positives: Tuple[Atom, ...]
    negatives: Tuple[Atom, ...]
    held_pos: Tuple[Atom, ...] = ()
    held_neg: Tuple[Atom, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "positives", tuple(self.positives))
        object.__setattr__(self, "negatives", tuple(self.negatives))
        object.__setattr__(self, "held_pos", tuple(self.held_pos))
        object.__setattr__(self, "held_neg", tuple(self.held_neg))


@dataclass(frozen=True)
class RoundStats:
    """Everything one round did (reward, decision, promotion, held-out result)."""

    round: int
    name: str
    proposed: int
    accepted: bool
    verdict: Verdict
    held_proved: int
    held_total: int
    held_false: int
    promoted: Tuple[str, ...] = ()
    stopped_reason: Optional[str] = None

    @property
    def held_coverage(self) -> float:
        return self.held_proved / self.held_total if self.held_total else 0.0

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "name": self.name,
            "proposed": self.proposed,
            "accepted": self.accepted,
            "verdict": self.verdict.to_dict(),
            "held_proved": self.held_proved,
            "held_total": self.held_total,
            "held_false": self.held_false,
            "held_coverage": round(self.held_coverage, 6),
            "promoted": list(self.promoted),
            "stopped_reason": self.stopped_reason,
        }


@dataclass(frozen=True)
class LoopResult:
    """The whole run: the grown theory and the per-round trace."""

    theory: Theory
    stats: Tuple[RoundStats, ...]

    @property
    def rounds(self) -> int:
        return len(self.stats)

    @property
    def promoted(self) -> Tuple[str, ...]:
        return tuple(n for s in self.stats for n in s.promoted)

    @property
    def false_assert(self) -> int:
        return sum(s.held_false for s in self.stats)

    @property
    def mean_held_coverage(self) -> float:
        tot = sum(s.held_total for s in self.stats)
        return sum(s.held_proved for s in self.stats) / tot if tot else 0.0

    def to_dict(self) -> dict:
        return {
            "rounds": self.rounds,
            "params": self.theory.params,
            "promoted": list(self.promoted),
            "false_assert": self.false_assert,
            "mean_held_coverage": round(self.mean_held_coverage, 6),
            "theory_sexp": theory_sexp(self.theory),
            "trace": [s.to_dict() for s in self.stats],
        }


# ============================================================================
# 3. the stopping rule
# ============================================================================
@dataclass(frozen=True)
class StopPolicy:
    """When the self-supervised loop should stop."""

    max_rounds: int = 8
    min_reward: float = 0.0
    stop_on_unsound: bool = False
    stop_on_no_proposal: bool = True


def decide_stop(stats: Sequence[RoundStats], policy: StopPolicy) -> Optional[str]:
    """Return a stop reason, or ``None`` to keep looping."""
    last = stats[-1]
    if policy.stop_on_unsound and last.held_false > 0:
        return "unsound"
    if policy.stop_on_no_proposal and last.proposed == 0:
        return "no_proposal"
    if len(stats) >= policy.max_rounds:
        return "round_budget"
    return None


# ============================================================================
# 4. the proposer (untrusted) -- it may only *suggest* programs
# ============================================================================
def propose(
    kb: KnowledgeBase,
    positives: Sequence[Atom],
    negatives: Sequence[Atom],
    *,
    max_body: int = 2,
    extra_vars: int = 1,
    max_arity: int = 3,
    budget: int = 20000,
) -> Tuple[Clause, ...]:
    """Propose clauses with LGG + greedy covering; labels never come from here."""
    positives = tuple(positives)
    if not positives:
        return ()
    return induce_clauses(
        kb,
        positives,
        negatives,
        max_body=max_body,
        extra_vars=extra_vars,
        max_arity=max_arity,
        budget=budget,
    )


def random_program(
    kb: KnowledgeBase,
    positives: Sequence[Atom],
    *,
    rng: Random,
    max_body: int = 2,
    max_arity: int = 3,
) -> Tuple[Clause, ...]:
    """A random (usually unsound) program -- the reward-blind control arm."""
    positives = tuple(sorted(positives, key=str))
    if not positives:
        return ()
    head = lgg_atoms(positives) if len(positives) > 1 else variate(positives[0])
    variables = list(head.variables()) + [Var("E0")]
    universe = literal_space(kb, positives[0], variables, max_arity=max_arity)
    if not universe:
        return ()
    for _ in range(30):
        length = 1 if max_body < 2 else rng.choice((1, 2))
        body = tuple(rng.choice(universe) for _ in range(length))
        try:
            rule = Rule(head, body, f"random_{head.pred}")
        except ValueError:
            continue
        return (Clause(rule, 0.0),)
    return ()


# ============================================================================
# 5. promotion -- structure only, and the loop itself
# ============================================================================
def sloppy_program(kb: KnowledgeBase, positives: Sequence[Atom]) -> Tuple[Clause, ...]:
    """Reuse the round-1 shape (``e(x,z),e(z,y)``) for *any* target predicate.

    A plausible-but-wrong program: it fits the round-1 positives and, with the
    hard gate removed, is promoted -- and then asserts held-out negatives.  This
    is the reward-hacking arm's proposal.
    """
    positives = tuple(sorted(positives, key=str))
    if not positives or positives[0].arity != 2:
        return ()
    head = lgg_atoms(positives) if len(positives) > 1 else variate(positives[0])
    if head.arity != 2 or not all(isinstance(a, Var) for a in head.args):
        return ()
    x, y = head.args
    z = Var("E0")
    body = (Atom("e", (x, z)), Atom("e", (z, y)))
    return (Clause(Rule(head, body, f"sloppy_{head.pred}"), 0.0),)


def promote(theory: Theory, program: Sequence[Clause]) -> Theory:
    """Append verified clauses to the theory (deduped); weights stay order."""
    seen = set(theory.names())
    clauses = list(theory.clauses)
    for clause in program:
        if clause.name in seen:
            continue
        seen.add(clause.name)
        clauses.append(clause)
    return Theory(theory.name, tuple(clauses))


def scramble_task(task: Task, rng: Random) -> Task:
    """Shuffle the pos/neg labels of a task -- the misaligned-reward control."""
    pool = list(task.positives) + list(task.negatives)
    order = list(range(len(pool)))
    rng.shuffle(order)
    shuffled = [pool[i] for i in order]
    n = len(task.positives)
    return Task(
        task.name, task.kb, tuple(shuffled[:n]), tuple(shuffled[n:]), task.held_pos, task.held_neg
    )


def run_loop(
    tasks: Sequence[Task],
    *,
    mode: str = "learn",
    policy: Optional[StopPolicy] = None,
    name: str = "selfsup",
    max_body: int = 2,
    extra_vars: int = 1,
    max_arity: int = 3,
    budget: int = 20000,
    cost: float = 0.02,
    seed: int = 0,
) -> LoopResult:
    """Run the self-supervised loop over a sequence of tasks.

    Each round: install the grown theory on the task's base KB, propose a
    program, score it with the kernel reward, and (unless ``no_promote``) promote
    it when it is sound, non-empty and meets ``min_reward``.  Held-out probes are
    always scored against the *true* task, so a scrambled reward is caught.
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")
    tasks = tuple(tasks)
    if policy is None:
        policy = StopPolicy(max_rounds=len(tasks))
    theory = Theory(name, ())
    rng = Random(seed)
    stats = []
    for index, task in enumerate(tasks):
        evidence = scramble_task(task, rng) if mode == "scramble" else task
        kb = theory.to_kb(evidence.kb)
        program = propose(
            kb,
            evidence.positives,
            evidence.negatives,
            max_body=max_body,
            extra_vars=extra_vars,
            max_arity=max_arity,
            budget=budget,
        )
        if mode == "random":
            program = random_program(kb, evidence.positives, rng=rng, max_body=max_body, max_arity=max_arity)
        elif mode == "reward_hacking":
            program = sloppy_program(kb, evidence.positives)
        verdict = evaluate(kb, program, evidence.positives, evidence.negatives, cost=cost)
        if mode == "reward_hacking":
            # the hard gate is removed: promote any non-empty proposal.  This is
            # the reward-hacking arm -- it shows why false_assert==0 is the anchor.
            accepted = bool(program)
        else:
            accepted = (
                mode != "no_promote"
                and verdict.sound
                and verdict.coverage > 0.0
                and verdict.reward >= policy.min_reward
            )
        promoted: Tuple[str, ...] = ()
        if accepted and program:
            before = set(theory.names())
            theory = promote(theory, program)
            promoted = tuple(n for n in theory.names() if n not in before)
        held = closure(theory.to_kb(task.kb))
        held_proved = len(set(task.held_pos) & held)
        held_false = len(set(task.held_neg) & held)
        stats.append(
            RoundStats(
                round=index,
                name=task.name,
                proposed=len(program),
                accepted=bool(accepted),
                verdict=verdict,
                held_proved=held_proved,
                held_total=len(task.held_pos),
                held_false=held_false,
                promoted=promoted,
            )
        )
        reason = decide_stop(stats, policy)
        if reason is not None:
            stats[-1] = replace(stats[-1], stopped_reason=reason)
            break
    return LoopResult(theory, tuple(stats))


def reweight(
    theory: Theory,
    pairs: Sequence[Tuple[object, object]],
    *,
    epochs: int = 1,
    lr: float = 0.1,
) -> Tuple[Theory, int]:
    """Order the grown clauses with the fused hard-negative perceptron."""
    return learn(theory, pairs, epochs=epochs, lr=lr)


def program_sexp(theory: Theory) -> str:
    """The grown theory as Lisp-like code -- the loop literally writes a program."""
    return theory_sexp(theory)
