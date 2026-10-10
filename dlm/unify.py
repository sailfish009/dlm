"""Unification and substitution over function-free terms.

Small and total: because there are no function symbols, unification cannot occur
and a binding is just ``Var -> Term``. This is shared by the engine (search) and
the kernel (certificate re-checking).
"""
from __future__ import annotations

from typing import Dict, Optional

from .logic import Atom, Term, Var

Subst = Dict[Var, Term]

__all__ = ["Subst", "walk", "apply_atom", "unify"]


def walk(t: Term, s: Subst) -> Term:
    """Follow variable bindings to a representative."""
    while isinstance(t, Var) and t in s:
        nxt = s[t]
        if nxt == t:  # defensive: a var bound to itself
            break
        t = nxt
    return t


def apply_atom(a: Atom, s: Subst) -> Atom:
    if not a.args:
        return a
    return Atom(a.pred, tuple(walk(x, s) for x in a.args))


def unify(a: Atom, b: Atom, s: Optional[Subst] = None) -> Optional[Subst]:
    """Unify two atoms under ``s``; return an extended substitution or ``None``."""
    if a.pred != b.pred or a.arity != b.arity:
        return None
    out: Subst = dict(s) if s else {}
    for x, y in zip(a.args, b.args):
        x = walk(x, out)
        y = walk(y, out)
        if x == y:
            continue
        if isinstance(x, Var):
            out[x] = y
        elif isinstance(y, Var):
            out[y] = x
        else:
            return None
    return out