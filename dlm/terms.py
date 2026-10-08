"""DLM v0.0001 — first-order term language.

Minimal, immutable, dependency-free kernel used by every other module.
Terms are either variables (`Var`) or constants (`Const`). Atoms are a
predicate plus a tuple of terms. Unification is the standard Robinson
algorithm with an occurs-check, exposed as a pure function returning a new
substitution (or ``None`` on failure).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, Optional, Tuple


class Term:
    """Base class for first-order terms."""

    __slots__ = ()


@dataclass(frozen=True)
class Var(Term):
    """A logic variable. Stored without the leading '?'."""

    name: str

    def __str__(self) -> str:
        return f"?{self.name}"


@dataclass(frozen=True)
class Const(Term):
    """A ground constant (also used for predicate/function symbols)."""

    name: str

    def __str__(self) -> str:
        return self.name


# A substitution maps variable names to terms.
Subst = Dict[str, Term]


def V(name: str) -> Var:
    """Build a variable (accepts a name with or without a leading '?')."""
    return Var(name[1:] if name.startswith("?") else name)


def C(name: str) -> Const:
    """Build a constant."""
    return Const(name)


def is_var(t: Term) -> bool:
    return isinstance(t, Var)


def vars_of(t: Term) -> Iterator[str]:
    """Yield variable names occurring in a term."""
    if isinstance(t, Var):
        yield t.name


def walk(t: Term, s: Subst) -> Term:
    """Follow variable bindings until a non-bound term is reached."""
    seen = 0
    while isinstance(t, Var) and t.name in s:
        t = s[t.name]
        seen += 1
        if seen > 10_000:  # cyclic substitution guard
            raise RecursionError("cyclic substitution")
    return t


def occurs(name: str, t: Term, s: Subst) -> bool:
    """True if variable ``name`` occurs inside term ``t`` under ``s``."""
    t = walk(t, s)
    return isinstance(t, Var) and t.name == name


def unify(a: Term, b: Term, s: Optional[Subst] = None) -> Optional[Subst]:
    """Robinson unification with occurs-check. Returns a new Subst or None."""
    if s is None:
        s = {}
    a = walk(a, s)
    b = walk(b, s)
    if a == b:
        return s
    if isinstance(a, Var):
        if occurs(a.name, b, s):
            return None
        out = dict(s)
        out[a.name] = b
        return out
    if isinstance(b, Var):
        if occurs(b.name, a, s):
            return None
        out = dict(s)
        out[b.name] = a
        return out
    return None  # two distinct constants


def substitute(t: Term, s: Subst) -> Term:
    """Apply a substitution to a term (shallow: terms are flat strings)."""
    return walk(t, s)


@dataclass(frozen=True)
class Atom:
    """A predicate applied to terms, e.g. ``parent(?x, ?y)``."""

    pred: str
    args: Tuple[Term, ...] = ()

    def __str__(self) -> str:
        if not self.args:
            return self.pred
        return f"{self.pred}({', '.join(str(a) for a in self.args)})"

    def is_ground(self) -> bool:
        return all(isinstance(a, Const) for a in self.args)

    def vars(self) -> Iterator[str]:
        for a in self.args:
            yield from vars_of(a)


def atom(pred: str, *args: Term) -> Atom:
    """Build an atom, coercing plain strings to constants (like ``fact``)."""
    coerced = tuple(a if isinstance(a, Term) else Const(str(a)) for a in args)
    return Atom(pred, coerced)


def unify_atom(a: Atom, b: Atom, s: Optional[Subst] = None) -> Optional[Subst]:
    """Unify two atoms (predicate must match, arity must match)."""
    if a.pred != b.pred or len(a.args) != len(b.args):
        return None
    cur = s if s is not None else {}
    for x, y in zip(a.args, b.args):
        cur = unify(x, y, cur)
        if cur is None:
            return None
    return cur


def substitute_atom(a: Atom, s: Subst) -> Atom:
    return Atom(a.pred, tuple(substitute(t, s) for t in a.args))