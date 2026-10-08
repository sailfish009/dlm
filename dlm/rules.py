"""DLM v0.0001 — Horn rules and facts.

A ``Rule`` is a Horn clause ``head :- body``. A ``Fact`` is a ground ``Atom``.
Rules are immutable; ``rename`` performs a safe alpha-renaming so a stored
rule can be used many times without variable capture.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, Tuple

from .terms import Atom, Const, Subst, Term, Var, substitute_atom


@dataclass(frozen=True)
class Rule:
    head: Atom
    body: Tuple[Atom, ...] = ()
    name: str = ""

    def __str__(self) -> str:
        label = f"{self.name}: " if self.name else ""
        if not self.body:
            return f"{label}{self.head}."
        bodystr = ", ".join(str(b) for b in self.body)
        return f"{label}{self.head} :- {bodystr}."

    def vars(self) -> Iterator[str]:
        yield from self.head.vars()
        for b in self.body:
            yield from b.vars()

    def rename(self, suffix: str) -> "Rule":
        """Alpha-rename every variable with ``suffix`` (prevents capture)."""
        out: Subst = {}
        for name in self.vars():
            if name not in out:
                out[name] = Var(f"{name}#{suffix}")
        return Rule(
            substitute_atom(self.head, out),
            tuple(substitute_atom(b, out) for b in self.body),
            self.name,
        )


def rule(head: Atom, *body: Atom, name: str = "") -> Rule:
    return Rule(head, tuple(body), name)


def fact(pred: str, *args: Term) -> Atom:
    """Build a ground atom, coercing plain strings to constants."""
    from .terms import atom as _atom

    coerced = tuple(a if isinstance(a, Term) else Const(str(a)) for a in args)
    return _atom(pred, *coerced)


def is_ground(atom_: Atom) -> bool:
    return atom_.is_ground()


def ground_facts(rule_or_fact: object) -> bool:
    if isinstance(rule_or_fact, Atom):
        return rule_or_fact.is_ground()
    if isinstance(rule_or_fact, Rule):
        return not rule_or_fact.body and rule_or_fact.head.is_ground()
    raise TypeError(type(rule_or_fact))