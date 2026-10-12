"""DLM v0.0028 -- a goal-conditioned control layer for the executor (untrusted).

v0.0027 gave the learned order control over *execution*, but the order was still a
single **global** weight per clause.  A global weight cannot say "this clause is
right for *this* goal and wrong for *that* one" -- exactly the routing a
backward-chaining search needs, because the same clause can close one goal cheaply
and burn the whole budget on another.  This module adds the missing *context*.

:func:`context_features` reads a ``(goal, clause)`` pair into named features -- the
clause's shape, the goal's predicate/arity, and (the key one) which of the clause's
body literals are **fact-backed once the clause head is matched to the goal**.
:class:`ControlScorer` is a learned linear model over those features;
:func:`train_control` fits it from an execution trace (a clause that closed a proof
for a goal is a positive example of that context, a clause that only spent budget a
negative one).  :class:`EpisodicMemory` records past ``(goal-signature, clause)``
successes and contributes a recall feature.

The scorer only *orders* clause attempts, exactly like v0.0027: it never asserts a
fact or a rule.  :func:`control_execute` still delegates to :func:`dlm.execute.execute`,
so every proof it returns is re-checked against the kernel closure.

Honest scope.  This version lands the **goal-conditioned scorer** and **episodic
memory**.  Open-vocabulary **invention** (predicates outside the induced signature)
is a *proposer* concern and is deferred to v0.0029; nothing here changes
:func:`dlm.selfsup.propose`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from dlm import Atom, Clause, Rule, Theory, Var, apply_atom, unify
from dlm.execute import Execution, execute

__all__ = [
    "goal_signature",
    "EpisodicMemory",
    "context_features",
    "ControlScorer",
    "train_control",
    "examples_from_execution",
    "control_execute",
    "rank_clauses",
]


# ============================================================================
# 1. episodic memory: remember which clause closed which goal shape
# ============================================================================
def goal_signature(goal: Atom) -> str:
    """A constant-free shape for a goal: predicate, arity and argument pattern.

    Ground goals have no shared variables, so the pattern records only which
    argument positions are equal (``eq``) or ground (``c``).  The signature is
    deliberately **coarse** -- it abstracts the constants away, so a memory entry
    transfers to a *new* goal of the same shape (or, when the shape carries no
    structure, only within one predicate).
    """
    seen: Dict[object, int] = {}
    marks: List[str] = []
    for t in goal.args:
        if isinstance(t, Var):
            if t not in seen:
                seen[t] = len(seen)
            marks.append(f"s{seen[t]}")
        else:
            marks.append("c")
    return f"{goal.pred}/{goal.arity}/" + ".".join(marks)


@dataclass(frozen=True)
class EpisodicMemory:
    """Net proof credit per ``(goal signature, clause)`` -- a recall table.

    ``observe`` folds an execution trace in (a successful clause attempt for a goal
    is ``+1``, a failed one ``-1``).  ``recall`` returns the accumulated value;
    ``context_features`` turns it into a ``memo:`` feature so a learned scorer can
    use past experience as one more piece of context.
    """

    table: Dict[Tuple[str, str], int] = field(default_factory=dict)

    def observe(self, execution: Execution) -> "EpisodicMemory":
        table = dict(self.table)
        for step in execution.steps:
            if step.clause is None:
                continue
            key = (goal_signature(step.goal), step.clause)
            table[key] = table.get(key, 0) + (1 if step.ok else -1)
        return EpisodicMemory(table)

    def recall(self, goal: Atom, clause: str) -> int:
        return self.table.get((goal_signature(goal), clause), 0)

    def merge(self, other: "EpisodicMemory") -> "EpisodicMemory":
        table = dict(self.table)
        for k, v in other.table.items():
            table[k] = table.get(k, 0) + v
        return EpisodicMemory(table)

    @property
    def size(self) -> int:
        return len(self.table)

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "table": {f"{sig}|{clause}": v for (sig, clause), v in sorted(self.table.items())},
        }


# ============================================================================
# 2. context: read a (goal, clause) pair into named features
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


def _supported(kb, atom: Atom) -> bool:
    """Can ``atom`` (after the head match) be backed by a base fact right now?"""
    if atom.is_ground():
        return kb.has_fact(atom)
    for fact in kb.facts_by_pred(atom.pred):
        if fact.arity != atom.arity:
            continue
        if unify(atom, fact) is not None:
            return True
    return False


def _head_subst(goal: Atom, rule: Rule) -> Optional[Dict]:
    """Match a freshened ``rule`` head to ``goal``; return the substitution or None."""
    fresh = _freshen_rule(rule, "__g")
    return unify(goal, fresh.head, {})


def context_features(
    kb,
    goal: Atom,
    clause: Clause,
    memory: Optional[EpisodicMemory] = None,
) -> Tuple[str, ...]:
    """The goal-conditioned feature vector for one candidate clause.

    Every feature is a *function of the goal*, which is exactly what a global
    clause weight cannot express.  The decisive ones are ``sup:<pred>`` /
    ``unsup:<pred>``: whether each body literal is backed by a fact once the head
    is matched to this goal (a one-step lookahead).  Features are returned sorted
    and deduped so the model is deterministic.
    """
    rule = clause.rule
    feats: List[str] = [
        f"goal={goal.pred}",
        f"garity={goal.arity}",
        f"clen={len(rule.body)}",
        f"cname={clause.name}",
        f"cpred={rule.head.pred}",
    ]
    subst = _head_subst(goal, rule)
    if subst is None:
        feats.append("nomatch")
        return tuple(sorted(set(feats)))
    fresh = _freshen_rule(rule, "__g")
    supported: List[str] = []
    for atom in fresh.body:
        backed = apply_atom(atom, subst)
        ok = _supported(kb, backed)
        feats.append(f"{'sup' if ok else 'unsup'}:{atom.pred}")
        if ok:
            supported.append(atom.pred)
    feats.append(f"nsup={len(supported)}")
    if fresh.body:
        if len(supported) == len(fresh.body):
            feats.append("frac=all")
        elif supported:
            feats.append("frac=some")
        else:
            feats.append("frac=none")
    if memory is not None:
        value = memory.recall(goal, clause.name)
        bucket = "pos" if value > 0 else "neg" if value < 0 else "zero"
        feats.append(f"memo={bucket}")
    return tuple(sorted(set(feats)))


# ============================================================================
# 3. the scorer: a learned linear model over context features
# ============================================================================
@dataclass(frozen=True)
class ControlScorer:
    """A goal-conditioned score -- ``weights . context_features(goal, clause)``.

    The weights live over *named features*, not over clauses, so the score can
    change with the goal.  An all-zero scorer is the frozen control (it reduces to
    the base weight / name order).
    """

    weights: Dict[str, float] = field(default_factory=dict)

    def features(
        self, kb, goal: Atom, clause: Clause, memory: Optional[EpisodicMemory] = None
    ) -> Tuple[str, ...]:
        return context_features(kb, goal, clause, memory)

    def score(
        self, kb, goal: Atom, clause: Clause, memory: Optional[EpisodicMemory] = None
    ) -> float:
        return sum(self.weights.get(f, 0.0) for f in context_features(kb, goal, clause, memory))

    def top_features(self, n: int = 12) -> List[Tuple[str, float]]:
        return sorted(self.weights.items(), key=lambda kv: (-abs(kv[1]), kv[0]))[:n]

    def to_dict(self) -> dict:
        return {"weights": {k: round(v, 6) for k, v in sorted(self.weights.items())}}


def examples_from_execution(
    kb, theory: Theory, execution: Execution
) -> Tuple[Tuple[Atom, Clause, int], ...]:
    """Turn a trace into supervised ``(goal, clause, label)`` context examples.

    A successful attempt (the clause closed that goal) is ``+1``; a failed attempt
    (the clause only spent budget) is ``-1``.  This is the same exact per-step
    signal v0.0027 used, read back as *context* labels.
    """
    by_name = {c.name: c for c in theory.clauses}
    out: List[Tuple[Atom, Clause, int]] = []
    for step in execution.steps:
        if step.clause is None:
            continue
        clause = by_name.get(step.clause)
        if clause is None:
            continue
        out.append((step.goal, clause, 1 if step.ok else -1))
    return tuple(out)


def train_control(
    model: ControlScorer,
    examples: Sequence[Tuple[Atom, Clause, int]],
    *,
    kb,
    memory: Optional[EpisodicMemory] = None,
    epochs: int = 1,
    lr: float = 0.1,
) -> Tuple[ControlScorer, int]:
    """Fit the goal-conditioned scorer with a perceptron over context features."""
    weights = dict(model.weights)
    updates = 0
    for _ in range(max(0, int(epochs))):
        for goal, clause, label in examples:
            feats = context_features(kb, goal, clause, memory)
            total = sum(weights.get(f, 0.0) for f in feats)
            if label * total <= 0:
                for f in feats:
                    weights[f] = weights.get(f, 0.0) + lr * label
                updates += 1
    return ControlScorer(weights), updates


# ============================================================================
# 4. run the executor with a goal-conditioned order (still only proposes)
# ============================================================================
def control_execute(
    kb,
    theory: Theory,
    goals,
    model: ControlScorer,
    *,
    memory: Optional[EpisodicMemory] = None,
    base: bool = True,
    **kwargs,
) -> Execution:
    """``execute`` with a goal-conditioned order; the kernel still verifies.

    ``base`` adds the clause weight to the context score, so the control layer is
    an *increment* on the v0.0027 global order rather than a replacement.
    """

    def order(goal: Atom, clause: Clause) -> float:
        score = model.score(kb, goal, clause, memory)
        return (clause.weight if base else 0.0) + score

    return execute(kb, theory, goals, scorer=order, **kwargs)


def rank_clauses(
    kb,
    goal: Atom,
    theory: Theory,
    model: ControlScorer,
    *,
    memory: Optional[EpisodicMemory] = None,
    base: bool = True,
) -> Tuple[Tuple[str, float], ...]:
    """The order the executor would try the goal's candidate clauses (descending)."""
    scored = [
        (
            c.name,
            (c.weight if base else 0.0) + model.score(kb, goal, c, memory),
        )
        for c in theory.clauses
        if c.rule.head.pred == goal.pred and c.rule.head.arity == goal.arity
    ]
    scored.sort(key=lambda kv: (-kv[1], kv[0]))
    return tuple((name, round(score, 6)) for name, score in scored)
