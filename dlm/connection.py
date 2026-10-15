"""DLM v0.0049 -- the connection: order-sensitive credit and its holonomy (untrusted).

Deduction needs integration in three layers.  Two of them are potentials: the
forward integral (:mod:`dlm.integral`) is the least fixed point and is
path-INDEPENDENT, and the evidence integral ``Z`` is a measure over theories.
The third is different.  Under a *bounded* search, per-rule credit depends on the
order rules are tried in: sweep the order and you sample a field whose discrete
circulation (holonomy / curl) is in general NONZERO.  So there is no scalar
``Phi(W)`` whose gradient is credit -- the order sector is a **connection**, and
learning it is a **path integral**, not a descent.  This is not a defect to hide;
it is the reason the credit/order layer is not a loss.

This module keeps the connection explicit (option A) rather than reifying it
away into structure (option B):

* :func:`execute` -- a bounded, order-sensitive backward-chaining search.  It
  only ORDERS rule attempts; it never adds a fact or a rule (the kernel is
  untouched, the trust invariant).
* :func:`credit` / :func:`deep_credit` -- per-rule credit from the trace, and the
  proof-DAG version that credits only rules on a COMPLETE proof while blaming the
  failure frontier.  The two differ exactly where the order mattered.
* :func:`curl` / :func:`holonomy` -- the discrete circulation of the credit field.
* :func:`integrate_credit` -- the path integral: the running sum of credit along a
  trajectory of orders.  The endpoint depends on the path; it is not a state.
* :func:`gauge_shift` -- adding a constant to every priority is a gauge
  transform; the curl is gauge-invariant.

One-way import (stdlib + the kernel); ``dlm/__init__.py`` never imports it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import exp, log
from typing import Callable, Dict, Iterable, Optional, Sequence, Tuple

from . import Atom, KnowledgeBase, NegAtom, Rule, Var, unify
from .proof import Proof, prove

__all__ = [
    "Step",
    "Trace",
    "execute",
    "Credit",
    "credit",
    "trace_frontier",
    "deep_credit",
    "proof_depth",
    "derivation_loss",
    "gauge_shift",
    "curl",
    "scalar_curl",
    "holonomy",
    "block_circulation",
    "integrate_credit",
]


# ============================================================================
# 1. the bounded, order-sensitive search (a heuristic; never asserts)
# ============================================================================
@dataclass(frozen=True)
class Step:
    """One rule attempt: goal under proof, rule name, success, search depth."""

    goal: Atom
    rule: str
    ok: bool
    depth: int


@dataclass(frozen=True)
class Trace:
    """The record of a bounded search.  ``exhausted`` means the budget bound."""

    goals: Tuple[Atom, ...]
    proved: Tuple[Atom, ...]
    steps: Tuple[Step, ...]
    spent: int
    budget: int
    max_depth: int
    exhausted: bool

    def to_dict(self) -> dict:
        return {
            "goals": [_atom_str(g) for g in self.goals],
            "proved": [_atom_str(g) for g in self.proved],
            "spent": self.spent,
            "budget": self.budget,
            "exhausted": self.exhausted,
            "steps": len(self.steps),
            "order": [s.rule for s in self.steps],
        }


def _atom_str(a: Atom) -> str:
    if not a.args:
        return a.pred
    return a.pred + "(" + ",".join(getattr(t, "name", str(t)) for t in a.args) + ")"


def _apply(atom: Atom, s: Dict[str, object]) -> Atom:
    return Atom(atom.pred, tuple(s.get(t.name, t) if isinstance(t, Var) else t for t in atom.args))


def _freshen(rule: Rule, tag: str) -> Rule:
    """Rename a rule's variables apart so it can be tried at every depth."""
    m: Dict[str, Var] = {}

    def conv(t):
        if isinstance(t, Var):
            if t.name not in m:
                m[t.name] = Var(t.name + tag)
            return m[t.name]
        return t

    head = Atom(rule.head.pred, tuple(conv(t) for t in rule.head.args))
    body = tuple(Atom(b.pred, tuple(conv(t) for t in b.args)) for b in rule.body)
    return Rule(head, body, rule.name)


def _positive(rule: Rule) -> bool:
    return all(not isinstance(b, NegAtom) for b in rule.body)


def execute(
    kb: KnowledgeBase,
    rules: Iterable[Rule],
    goals: Iterable[Atom],
    *,
    priority: Optional[Dict[str, float]] = None,
    budget: int = 100000,
    max_depth: int = 64,
) -> Trace:
    """Bounded backward chaining; try the highest-priority rule first.

    ``priority`` ranks the rules (higher first, ties broken by name) -- this is
    the ORDER whose path-dependence we are going to measure.  A rule literal with
    negation is skipped (this is a Horn search heuristic); the kernel's
    :func:`dlm.closure` remains the only source of truth.
    """
    goals = tuple(goals)
    prio = dict(priority or {})
    rules = tuple(r for r in rules if _positive(r))
    by_pred: Dict[str, list] = {}
    for r in rules:
        by_pred.setdefault(r.head.pred, []).append(r)
    for v in by_pred.values():
        v.sort(key=lambda r: (-prio.get(r.name, 0.0), r.name))

    facts = set(kb.facts)
    facts_by_pred: Dict[str, list] = {}
    for f in facts:
        facts_by_pred.setdefault(f.pred, []).append(f)

    steps: list = []
    proved: list = []
    spent = 0
    exhausted = False
    memo: Dict[Atom, bool] = {}

    def solve(goal: Atom, subst: dict, depth: int):
        nonlocal spent, exhausted
        g = _apply(goal, subst)
        if g.is_ground() and (g in facts or memo.get(g)):
            return subst
        if depth >= max_depth:
            return None
        for f in facts_by_pred.get(g.pred, ()):
            ns = unify(g, f, subst)
            if ns is not None:
                return ns
        for rule in by_pred.get(g.pred, ()):
            if spent >= budget:
                exhausted = True
                return None
            spent += 1
            fresh = _freshen(rule, f"_{spent}_")
            ns = unify(fresh.head, g, subst)
            if ns is None:
                steps.append(Step(g, rule.name, False, depth))
                continue
            body_subst = ns
            ok = True
            for b in fresh.body:
                body_subst = solve(b, body_subst, depth + 1)
                if body_subst is None:
                    ok = False
                    break
            steps.append(Step(g, rule.name, ok, depth))
            if ok:
                if g.is_ground():
                    memo[g] = True
                return body_subst
        return None

    for goal in goals:
        g = _apply(goal, {})
        if g.is_ground() and (g in facts or memo.get(g)):
            proved.append(g)
            continue
        if solve(goal, {}, 0) is not None:
            proved.append(g)
        if exhausted:
            break
    return Trace(tuple(goals), tuple(proved), tuple(steps), spent, budget, max_depth, exhausted)


# ============================================================================
# 2. credit from the trace: shallow (per attempt) and deep (per complete proof)
# ============================================================================
@dataclass(frozen=True)
class Credit:
    """Per-rule credit: ``hits`` (useful attempts) and ``waste`` (wasted attempts)."""

    hits: Dict[str, int] = field(default_factory=dict)
    waste: Dict[str, int] = field(default_factory=dict)

    @property
    def rules(self) -> Tuple[str, ...]:
        return tuple(sorted(set(self.hits) | set(self.waste)))

    def net(self) -> Dict[str, int]:
        return {r: self.hits.get(r, 0) - self.waste.get(r, 0) for r in self.rules}

    def to_dict(self) -> dict:
        return {"hits": dict(sorted(self.hits.items())), "waste": dict(sorted(self.waste.items()))}


def credit(trace: Trace) -> Credit:
    """Shallow credit: a rule that ever succeeded on an attempted goal gets a hit."""
    hits: Dict[str, int] = {}
    waste: Dict[str, int] = {}
    for st in trace.steps:
        (hits if st.ok else waste)[st.rule] = (hits if st.ok else waste).get(st.rule, 0) + 1
    return Credit(hits, waste)


def trace_frontier(trace: Trace) -> Tuple[str, ...]:
    """Rules attempted on a goal that was never proved -- the blame frontier."""
    proved = set(trace.proved)
    return tuple(st.rule for st in trace.steps if not st.ok and st.goal not in proved)


def proof_depth(proof: Proof) -> int:
    """Longest rule chain under a proof (leaf facts have depth 1)."""
    if proof.rule is None or not proof.premises:
        return 1
    return 1 + max(proof_depth(p) for p in proof.premises)


def _rule_names(proof: Proof) -> Tuple[str, ...]:
    out: list = []

    def walk(node: Proof):
        if node.rule is not None:
            out.append(node.rule.name)
        for p in node.premises:
            walk(p)

    walk(proof)
    return tuple(out)


def deep_credit(
    kb: KnowledgeBase,
    rules: Iterable[Rule],
    goals: Iterable[Atom],
    *,
    priority: Optional[Dict[str, float]] = None,
    budget: int = 100000,
    max_depth: int = 64,
) -> Credit:
    """Credit along COMPLETE proofs, blame the failure frontier.

    A rule that succeeds on a subgoal but sits on a branch that dead-ends gets no
    hit here (unlike :func:`credit`); the rules on the dead branch are blamed
    instead.  This is the proof-DAG (backward-pass) view of the same trace.
    """
    rules = tuple(r for r in rules if _positive(r))
    trace = execute(kb, rules, goals, priority=priority, budget=budget, max_depth=max_depth)
    tkb = kb.copy()
    for r in rules:
        tkb.add_rule(r)
    hits: Dict[str, int] = {}
    for g in trace.proved:
        p = prove(tkb, g)
        if p is not None:
            for name in _rule_names(p):
                hits[name] = hits.get(name, 0) + 1
    waste: Dict[str, int] = {}
    for name in trace_frontier(trace):
        waste[name] = waste.get(name, 0) + 1
    return Credit(hits, waste)


def derivation_loss(
    kb: KnowledgeBase,
    rules: Iterable[Rule],
    goals: Iterable[Atom],
    *,
    cost: float = 1.0,
) -> float:
    """``-log mean_T exp(-cost * depth(T))``: the derivation free energy.

    A scalar *only because it is read off the proof measure*, not a pointwise
    loss over the credit field (that field is a connection; see the module doc).
    """
    goals = tuple(goals)
    if not goals:
        return 0.0
    rules = tuple(r for r in rules if _positive(r))
    tkb = kb.copy()
    for r in rules:
        tkb.add_rule(r)
    mass = 0.0
    for g in goals:
        p = prove(tkb, g)
        if p is not None:
            mass += exp(-cost * proof_depth(p))
    if mass == 0.0:
        return float("inf")
    return -log(mass / len(goals))


# ============================================================================
# 3. the connection: curl, holonomy, gauge, path integral
# ============================================================================
def gauge_shift(priority: Dict[str, float], c: float) -> Dict[str, float]:
    """A gauge transform: add a constant to every priority (curl-invariant)."""
    return {k: v + c for k, v in priority.items()}


def curl(field: Callable[[float, float], Tuple[float, float]], a: float, b: float) -> float:
    """Discrete circulation of a 1-form field around the unit square ``(a,b)``.

    ``field(x, y) -> (fx, fy)``.  The four edge midpoints are sampled and Stokes'
    theorem is applied on the plaquette: ``H(a,b) + V(a+1,b) - H(a,b+1) - V(a,b)``.
    """
    fx0, _ = field(a + 0.5, b)
    _, fy1 = field(a + 1.0, b + 0.5)
    fx2, _ = field(a + 0.5, b + 1.0)
    _, fy0 = field(a, b + 0.5)
    return fx0 + fy1 - fx2 - fy0


def scalar_curl(f: Callable[[float, float], float], a: float, b: float) -> float:
    """Circulation of the gradient of a scalar -- identically zero (the control)."""
    return (
        (f(a + 1, b) - f(a, b))
        + (f(a + 1, b + 1) - f(a + 1, b))
        - (f(a + 1, b + 1) - f(a, b + 1))
        - (f(a, b + 1) - f(a, b))
    )


def holonomy(
    field: Callable[[float, float], Tuple[float, float]],
    cells: Iterable[Tuple[float, float]],
) -> Dict[str, float]:
    """The nonzero plaquette circulations of a field -- its holonomy."""
    out: Dict[str, float] = {}
    for (a, b) in cells:
        c = curl(field, a, b)
        if c != 0.0:
            out[f"{a:g},{b:g}"] = c
    return out


def block_circulation(
    field: Callable[[float, float], Tuple[float, float]], a: float, b: float, n: int = 2
) -> float:
    """Total circulation of an ``n x n`` block -- the holonomy of the loop round it."""
    return sum(curl(field, a + i, b + j) for i in range(n) for j in range(n))


def integrate_credit(
    credits: Iterable[Credit], *, lr: float = 1.0
) -> list:
    """The path integral: running sum of net credit along a trajectory of orders.

    Returns the accumulated weights after each step.  Because the credit field is
    a connection, the accumulated endpoint depends on the ORDER of the path, not
    only on its endpoints.
    """
    acc: Dict[str, float] = {}
    out: list = []
    for cr in credits:
        for name, value in cr.net().items():
            acc[name] = acc.get(name, 0.0) + lr * value
        out.append(dict(acc))
    return out