"""DLM v0.0049 -- the integral layers: forward closure and the evidence integral (untrusted).

Deduction needs *integration*, not a loss.  Induction learns by differentiation
(a scalar loss and its gradient); deduction's forward pass is already an integral
-- ``closure`` is the least fixed point of the immediate-consequence operator, the
union of its iterates, a discrete integral over derivation depth.  This module
makes the two *potential* layers explicit:

* :func:`forward` -- the forward integral ``D(T) = closure(kb + rules)`` and its
  **debt** (the target atoms it does not reach) plus ``false_assert`` (declared
  negatives it does reach).  The kernel decides the closure; the debt is read off
  it.  The result is path-INDEPENDENT: the least fixed point does not depend on
  the order in which rules are tried.
* :func:`evidence` -- the **evidence integral** over a set of candidate
  rule-sets: ``Z = sum_T exp(-E(T))``, free energy ``F = -log Z``, the MAP choice,
  the posterior and the multiplicity reward.  This is a *measure over theories*,
  not an objective to descend: it answers "how many good theories are there",
  which a single best theory (or a single loss value) cannot.

A scalar energy exists (debt + description length) and is genuine, because the
structure sector *is* integrable -- accepted structure moves strictly lower the
description length.  The order/credit sector is not; that is
:mod:`dlm.connection`'s subject, and it is deliberately kept separate.

One-way import (stdlib + the kernel); ``dlm/__init__.py`` never imports it.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Iterable, Sequence, Tuple

from . import Atom, KnowledgeBase, Rule, closure, description_length

__all__ = [
    "Forward",
    "forward",
    "loss_integral",
    "Evidence",
    "energy",
    "evidence",
    "atom_str",
]


def atom_str(a: Atom) -> str:
    """A readable ``pred(arg,...)`` label for an atom (the kernel has no __str__)."""
    if not a.args:
        return a.pred
    return a.pred + "(" + ",".join(getattr(t, "name", str(t)) for t in a.args) + ")"


# ============================================================================
# 1. the forward integral and its debt (kernel-decided)
# ============================================================================
@dataclass(frozen=True)
class Forward:
    """One forward pass: the closure (the integral) and its debt (the loss).

    ``closure``  the kernel's least fixed point over ``kb + rules`` (the integral).
    ``proved``   the target atoms it reaches (in the closure).
    ``debt``     the target atoms it does not reach (the content debt).
    ``excess``   atoms reached beyond the base closure and the target
                 (over-generalisation -- the integral ran past the target).
    ``false_assert``  declared negatives it reaches (the hard soundness gate).
    """

    closure: frozenset
    target: Tuple[str, ...]
    proved: Tuple[str, ...]
    debt: Tuple[str, ...]
    excess: Tuple[str, ...]
    false_assert: int

    @property
    def content_loss(self) -> int:
        """The deduction loss: uncovered targets plus unsound derivations."""
        return len(self.debt) + self.false_assert

    @property
    def sound(self) -> bool:
        return self.false_assert == 0

    def to_dict(self) -> dict:
        return {
            "closure": len(self.closure),
            "target": list(self.target),
            "proved": list(self.proved),
            "debt": list(self.debt),
            "excess": list(self.excess),
            "content_loss": self.content_loss,
            "false_assert": self.false_assert,
            "sound": self.sound,
        }


def forward(
    kb: KnowledgeBase,
    rules: Iterable[Rule],
    target: Iterable[Atom],
    *,
    negatives: Iterable[Atom] = (),
) -> Forward:
    """The forward integral ``closure(kb + rules)`` and its debt.

    The closure is the kernel's least fixed point -- the accumulated
    consequences -- and does not depend on the order the rules are applied in.
    The content loss is the target atoms *not* in it plus any declared negative
    that *is*.
    """
    target = tuple(sorted(target, key=atom_str))
    negs = frozenset(negatives)
    tkb = kb.copy()
    for r in rules:
        tkb.add_rule(r)
    closed = frozenset(closure(tkb))
    base = frozenset(closure(kb))
    target_set = set(target)
    proved = tuple(atom_str(a) for a in target if a in closed)
    debt = tuple(atom_str(a) for a in target if a not in closed)
    excess = tuple(sorted((atom_str(a) for a in (closed - base) - target_set), key=str))
    return Forward(
        closure=closed,
        target=tuple(atom_str(a) for a in target),
        proved=proved,
        debt=debt,
        excess=excess,
        false_assert=len(negs & closed),
    )


def loss_integral(values: Iterable[float], *, dt: float = 1.0) -> float:
    """Trapezoidal integral of a loss trajectory: ``∫ L dt``.

    The area under a learning curve.  A learner that reaches a low loss sooner
    has a smaller ``∫ L dt`` even when both end at the same fixpoint.
    """
    seq = [float(v) for v in values]
    if len(seq) < 2:
        return 0.0
    return float(dt) * (0.5 * seq[0] + sum(seq[1:-1]) + 0.5 * seq[-1])


# ============================================================================
# 2. the evidence integral over candidate theories (a measure)
# ============================================================================
@dataclass(frozen=True)
class Evidence:
    """The evidence integral over candidate theories: ``Z``, free energy, posterior."""

    names: Tuple[str, ...]
    energies: Tuple[float, ...]
    losses: Tuple[float, ...]
    log_z: float
    map_index: int
    posterior: Tuple[float, ...]

    @property
    def z(self) -> float:
        return exp(self.log_z)

    @property
    def free_energy(self) -> float:
        return -self.log_z

    @property
    def map_energy(self) -> float:
        return self.energies[self.map_index]

    @property
    def map_name(self) -> str:
        return self.names[self.map_index]

    @property
    def map_loss(self) -> float:
        return self.losses[self.map_index]

    @property
    def expected_loss(self) -> float:
        return sum(p * l for p, l in zip(self.posterior, self.losses))

    @property
    def multiplicity_reward(self) -> float:
        """How much the integral beats the single best energy: ``E_MAP - F``."""
        return self.map_energy - self.free_energy

    def to_dict(self) -> dict:
        return {
            "names": list(self.names),
            "energies": [round(e, 6) for e in self.energies],
            "losses": [round(l, 6) for l in self.losses],
            "log_z": round(self.log_z, 6),
            "z": round(self.z, 6),
            "free_energy": round(self.free_energy, 6),
            "map_index": self.map_index,
            "map_name": self.map_name,
            "expected_loss": round(self.expected_loss, 6),
            "multiplicity_reward": round(self.multiplicity_reward, 6),
            "posterior": [
                {"name": n, "p": round(p, 6)} for n, p in zip(self.names, self.posterior)
            ],
        }


def energy(
    kb: KnowledgeBase,
    rules: Sequence[Rule],
    target: Iterable[Atom],
    *,
    negatives: Iterable[Atom] = (),
    beta: float = 1.0,
    cost: float = 0.0,
) -> float:
    """``E(T) = beta * content_loss(T) + cost * description_length(T)``.

    The content loss is kernel-decided (:func:`forward`); the description length
    is the MDL regulariser.  Both are additive over structure, which is exactly
    why the structure sector is a genuine scalar potential.
    """
    f = forward(kb, rules, target, negatives=negatives)
    return beta * f.content_loss + cost * description_length(tuple(rules))


def evidence(
    candidates: Sequence[Tuple[str, Sequence[Rule]]],
    kb: KnowledgeBase,
    target: Iterable[Atom],
    *,
    negatives: Iterable[Atom] = (),
    beta: float = 1.0,
    cost: float = 0.0,
) -> Evidence:
    """Integrate over candidate theories: ``Z = sum_T exp(-E(T))``, ``F = -log Z``.

    Returns the partition function, the free energy (a lower bound on the best
    energy and a *calibrated* value over the whole posterior), the MAP choice,
    the posterior-expected content loss and the multiplicity reward.  MAP is the
    optimistic single best theory; the integral counts how many good theories
    there are.
    """
    candidates = tuple(candidates)
    if not candidates:
        raise ValueError("evidence needs at least one candidate theory")
    target = tuple(target)
    energies = []
    losses = []
    for _, rules in candidates:
        f = forward(kb, rules, target, negatives=negatives)
        losses.append(float(f.content_loss))
        energies.append(beta * f.content_loss + cost * description_length(tuple(rules)))
    m = min(energies)
    fm = -m
    logsum = log(sum(exp(-e - fm) for e in energies))
    log_z = fm + logsum
    posterior = tuple(exp(-e - log_z) for e in energies)
    map_index = min(range(len(energies)), key=lambda i: (energies[i], i))
    return Evidence(
        names=tuple(n for n, _ in candidates),
        energies=tuple(energies),
        losses=tuple(losses),
        log_z=log_z,
        map_index=map_index,
        posterior=posterior,
    )