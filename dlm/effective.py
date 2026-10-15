"""DLM v0.0052 -- measuring whether the integral is EFFECTIVE (untrusted).

v0.0049 showed the three integral layers are *well-posed*: the forward closure is
a path-independent potential, the evidence integral is a normalised measure, and
the order/credit field is a connection with nonzero holonomy.  Well-posedness is
necessary, not sufficient.  This module turns it into a *measurement*: given a
matched, held-out, equal-budget setup, does the integral select or order **better
than the point baselines it is supposed to generalise**?

Two instruments, both read off the kernel only:

* the **evidence integral as a predictor**.  MAP takes the single train-best
  theory; the posterior *marginal* predicts every held-out atom with probability
  ``sum_T p(T) [atom in closure(theory T)]``.  Under a proper score the posterior
  mean is Bayes-optimal, so with a usable train likelihood the marginal cannot
  lose to MAP -- and strictly wins when several energy-tied theories disagree on
  held-out.
* the **order integral as a controller**.  :func:`path_order` runs the bounded
  search, reads the proof-DAG credit, and advances the next order along the path
  integral (a running sum over rounds).  It never asserts; the kernel remains the
  only judge.

One-way import (stdlib + the kernel + the untrusted integrators);
``dlm/__init__.py`` never imports it.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Dict, Iterable, List, Sequence, Tuple

from . import Atom, KnowledgeBase, Rule, closure
from .connection import Credit, deep_credit, execute
from .integral import Evidence

__all__ = [
    "close_with",
    "marginal_prediction",
    "map_prediction",
    "positive_set",
    "brier",
    "logloss",
    "order_by_credit",
    "path_order",
    "OrderPath",
]


def close_with(kb: KnowledgeBase, rules: Iterable[Rule]) -> frozenset:
    """The kernel closure of ``kb + rules`` -- the only source of truth."""
    tkb = kb.copy()
    for r in rules:
        tkb.add_rule(r)
    return frozenset(closure(tkb))


# ============================================================================
# 1. the evidence integral as a predictor
# ============================================================================
def marginal_prediction(
    ev: Evidence,
    theories: Sequence[Sequence[Rule]],
    kb: KnowledgeBase,
    universe: Sequence[Atom],
) -> Dict[Atom, float]:
    """Posterior-marginal ``P(atom derivable) = sum_T p(T) [atom in closure(T)]``.

    This is the integral's prediction: it *hedges* over every candidate theory
    weighted by its evidence instead of committing to the single MAP theory.
    """
    marg: Dict[Atom, float] = {a: 0.0 for a in universe}
    for p, rules in zip(ev.posterior, theories):
        if p <= 0.0:
            continue
        got = close_with(kb, rules)
        for a in universe:
            if a in got:
                marg[a] += p
    return marg


def map_prediction(
    ev: Evidence,
    theories: Sequence[Sequence[Rule]],
    kb: KnowledgeBase,
    universe: Sequence[Atom],
) -> Dict[Atom, float]:
    """The point baseline: predict 1 exactly on the MAP theory's closure."""
    got = close_with(kb, theories[ev.map_index])
    return {a: (1.0 if a in got else 0.0) for a in universe}


def positive_set(pred: Dict[Atom, float], threshold: float = 0.5) -> set:
    """Atoms the predictor commits to (probability at least ``threshold``)."""
    return {a for a, p in pred.items() if p >= threshold}


def brier(pred: Dict[Atom, float], universe: Sequence[Atom], truth: set) -> float:
    """Mean squared error of the per-atom probability against the held-out truth."""
    n = len(universe)
    if n == 0:
        return 0.0
    return sum((pred.get(a, 0.0) - (1.0 if a in truth else 0.0)) ** 2 for a in universe) / n


def logloss(
    pred: Dict[Atom, float], universe: Sequence[Atom], truth: set, *, eps: float = 1e-9
) -> float:
    """Mean log loss (a strictly proper score) of the predictor."""
    n = len(universe)
    if n == 0:
        return 0.0
    total = 0.0
    for a in universe:
        q = min(max(pred.get(a, 0.0), eps), 1.0 - eps)
        y = 1.0 if a in truth else 0.0
        total += -(y * log(q) + (1.0 - y) * log(1.0 - q))
    return total / n


# ============================================================================
# 2. the order integral as a controller (the path integral over orders)
# ============================================================================
@dataclass(frozen=True)
class OrderPath:
    """The trajectory of a bounded search whose order is moved by credit."""

    rounds: Tuple[dict, ...]

    @property
    def first_proved(self) -> int:
        return self.rounds[0]["proved"] if self.rounds else 0

    @property
    def final_proved(self) -> int:
        return self.rounds[-1]["proved"] if self.rounds else 0

    def to_dict(self) -> dict:
        return {"rounds": [dict(r) for r in self.rounds],
                "first_proved": self.first_proved,
                "final_proved": self.final_proved}


def order_by_credit(rules: Sequence[Rule], cr: Credit) -> Dict[str, float]:
    """Priority = net credit: a rule that proved things is tried before waste."""
    net = cr.net()
    return {r.name: float(net.get(r.name, 0)) for r in rules}


def path_order(
    kb: KnowledgeBase,
    rules: Sequence[Rule],
    goals: Sequence[Atom],
    *,
    rounds: int = 4,
    probe_budget: int = 100000,
    eval_budget: int = 500,
    max_depth: int = 64,
    lr: float = 1.0,
    base: Dict[str, float] = None,
) -> OrderPath:
    """The path integral over orders: accumulate credit, re-order, re-search.

    Each round runs the bounded search at ``eval_budget`` (the *equal* test
    budget), reads the proof-DAG credit, and adds it to the running weight
    vector.  The endpoint depends on the path, which is why this is an integral
    and not a descent; the kernel still decides every proof.
    """
    rules = tuple(rules)
    weights: Dict[str, float] = dict(base or {})
    hist: List[dict] = []
    for rd in range(rounds):
        tr = execute(kb, rules, goals, priority=weights, budget=eval_budget,
                     max_depth=max_depth)
        hist.append({
            "round": rd,
            "proved": len(tr.proved),
            "spent": tr.spent,
            "exhausted": tr.exhausted,
            "weights": dict(sorted(weights.items())),
        })
        cr = deep_credit(kb, rules, goals, priority=weights,
                         budget=probe_budget, max_depth=max_depth)
        for name, value in cr.net().items():
            weights[name] = weights.get(name, 0.0) + lr * float(value)
    return OrderPath(tuple(hist))