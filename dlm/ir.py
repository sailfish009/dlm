"""DLM v0.0048 -- the IR-TREE layer (untrusted).

The canonical intermediate representation is the **form tree** -- the same nested
tuple that atoms, rules, and macros already use::

    (rule (trans ?x ?y) (trans ?x ?z) (trans ?z ?y))     ; a Form = code = data

v0.0038 learned on flat ``Atom(pred, args)``; that is enough for first-order
subgoal abstraction but not for the syntactic abstractions (a macro rewrites a
*form* into a *form*; a recurring pattern is a *subtree*).  This layer names the
tree, walks it, canonicalises patterns up to variable renaming, and converts to
and from ``Atom``/``Rule``.  It is read-only: it never asserts anything, and the
kernel decides all truth.

A ``Frame`` is a *view over* this tree, never a separate type.
"""
from __future__ import annotations

from typing import Any, Iterator, List, Set, Tuple

from . import Atom, Rule
from .lisp import atom_to_form, form_to_atom, form_to_rule, is_var, rule_to_form

__all__ = [
    "Form", "is_form", "ir_head", "ir_children", "ir_walk",
    "pattern_key", "tree_features", "subforms",
    "ir_rule", "rule_ir", "ir_atom", "atom_ir",
]

Form = Any


def is_form(x: Any) -> bool:
    """A form is a non-empty tuple whose head is a symbol (a string)."""
    return isinstance(x, tuple) and len(x) > 0 and isinstance(x[0], str)


def ir_head(form: Any) -> Any:
    return form[0] if is_form(form) else None


def ir_children(form: Any) -> Tuple[Any, ...]:
    """The immediate sub-forms of ``form`` (non-form leaves are dropped)."""
    if not is_form(form):
        return ()
    return tuple(x for x in form[1:] if is_form(x))


def ir_walk(form: Any, path: Tuple[int, ...] = ()) -> Iterator[Tuple[Tuple[int, ...], Any]]:
    """Yield ``(path, subform)`` for every sub-form, the root first.

    ``path`` is the index tuple from the root; the root has path ``()``.
    """
    if is_form(form):
        yield path, form
        for i, x in enumerate(form[1:], start=1):
            yield from ir_walk(x, path + (i,))


def pattern_key(form: Any) -> str:
    """Canonical key of a form with variables abstracted to a single ``?``.

    Two patterns equal up to variable renaming share a key, so recurring
    structures can be grouped without committing to variable names.
    """
    if is_var(form) or form == "_":
        return "?"
    if is_form(form):
        return "(" + form[0] + " " + " ".join(pattern_key(x) for x in form[1:]) + ")"
    return str(form)


def tree_features(form: Any) -> Set[str]:
    """The symbol vocabulary of a form -- features for an untrusted proposer."""
    if is_form(form):
        feats = {"head:" + form[0]}
        for x in form[1:]:
            feats |= tree_features(x)
        return feats
    return {"sym:" + str(form)}


def subforms(form: Any, *, min_size: int = 1) -> List[Any]:
    """Every sub-form whose node count is at least ``min_size``."""
    out: List[Any] = []

    def size(f: Any) -> int:
        if is_form(f):
            return 1 + sum(size(x) for x in f[1:])
        return 1

    for _, f in ir_walk(form):
        if size(f) >= min_size:
            out.append(f)
    return out


# -- conversions (the tree is the IR; Atom/Rule are projections) -------------
def ir_rule(form: Any) -> Rule:
    return form_to_rule(form)


def rule_ir(rule: Rule) -> Form:
    return rule_to_form(rule)


def ir_atom(form: Any) -> Atom:
    return form_to_atom(form)


def atom_ir(atom: Atom) -> Form:
    return atom_to_form(atom)