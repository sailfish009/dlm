"""Re-checkable certificate -- the trusted judgment (module 6).

A ``Proof`` is a finite tree. Leaves are ground facts; an internal node is a
ground instance of a KB rule. ``verify`` re-checks it against the KB with **no
search**: it must bottom out only in known facts and use only known rules. This
is the only component allowed to *assert*; learners may only propose.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .kb import KnowledgeBase
from .logic import Atom, Rule
from .unify import Subst, unify

__all__ = ["Proof", "verify"]


@dataclass(frozen=True)
class Proof:
    atom: Atom
    rule: Optional[Rule] = None
    premises: Tuple["Proof", ...] = ()

    @property
    def is_fact(self) -> bool:
        return self.rule is None

    def __str__(self) -> str:
        if self.rule is None:
            return str(self.atom)
        head = self.rule.name or "rule"
        inner = f"{self.atom} {head}"
        if self.premises:
            inner += " " + " ".join(str(p) for p in self.premises)
        return f"(proof {inner})"


def verify(proof: Proof, kb: KnowledgeBase) -> bool:
    """Re-check ``proof`` against ``kb``. Returns True only if sound."""
    if not isinstance(proof, Proof) or not proof.atom.is_ground():
        return False
    if proof.rule is None:
        return kb.has_fact(proof.atom)
    rule = proof.rule
    if not kb.has_rule(rule):
        return False
    if len(proof.premises) != len(rule.body):
        return False
    s: Optional[Subst] = unify(proof.atom, rule.head)
    if s is None:
        return False
    for body_atom, premise in zip(rule.body, proof.premises):
        s = unify(body_atom, premise.atom, s)
        if s is None:
            return False
    return all(verify(p, kb) for p in proof.premises)