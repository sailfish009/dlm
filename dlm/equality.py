"""DLM v0.0051 -- equality / congruence over a FINITE symbol set (D7a, untrusted).

Equality is the first D7 rung: it lets the kernel conclude that two DIFFERENT
symbols denote the SAME thing.  It stays a conservative extension of the
function-free Horn substrate -- over a finite, given symbol set the congruence
(``same_kind`` = the equivalence classes of a canonical kind) is a finite ground
relation, and three new rules

    uses_layer(m, L) :- has_layer(m, X), same_kind(X, L)
    uses_layer(m, L) :- method_of(m, f), calls(f, X), same_kind(X, L)
    uses_layer(m, L) :- calls(m, X),     same_kind(X, L)

just feed the SAME closed-world shape as before.  Nothing here asserts truth; the
kernel still decides.

Falsifier that forced it: the program CALLS ``f_max_pool2d`` (and *creates*
``nn_conv2d``) yet D5 certified ``absent(net, maxpool2d)`` -- positive evidence
uses library aliases while the candidate universe uses canonical layer kinds, and
the two vocabularies were never tied by equality.  The fix is exact: the same
layer kind, reached through any alias, blocks the absence.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from . import Atom, Const, NegAtom, Rule, Var

# canonical layer kind of a symbol name after stripping a library prefix
_LAYER_ALIASES: Dict[str, str] = {
    "max_pool2d": "maxpool2d", "max_pool": "maxpool2d",
    "batchnorm": "batchnorm2d", "layer_norm": "layernorm",
    "conv2d": "conv2d", "linear": "linear", "dropout": "dropout",
    "batchnorm2d": "batchnorm2d", "layernorm": "layernorm", "normalize": "normalize",
    "gru": "gru", "lstm": "lstm", "attention": "attention",
}
_PREFIXES = ("f_", "nn_", "transforms_")


def canonical(symbol: str) -> str:
    for pre in _PREFIXES:
        if symbol.startswith(pre):
            return symbol[len(pre):]
    return symbol


def kind(symbol: str) -> str:
    """The canonical layer kind an alias denotes (identity if not a layer)."""
    c = canonical(symbol)
    return _LAYER_ALIASES.get(c, c)


def same_kind_pairs(symbols: Iterable[str]) -> List[Tuple[str, str]]:
    """The congruence closure: all ordered pairs within each canonical class.

    Reflexive, symmetric and transitive by construction over the finite set.
    """
    groups: Dict[str, Set[str]] = {}
    for s in symbols:
        groups.setdefault(kind(s), set()).add(s)
    out: Set[Tuple[str, str]] = set()
    for k, members in groups.items():
        cls = set(members) | {k}
        for a in cls:
            for b in cls:
                out.add((a, b))
    return sorted(out)


def same_kind_facts(symbols: Iterable[str]) -> List[Atom]:
    return [Atom("same_kind", (Const(a), Const(b))) for a, b in same_kind_pairs(symbols)]


def uses_layer_rules() -> List[Rule]:
    """A module uses a layer kind if it defines, inherits through, or calls it."""
    m, f, x, l = Var("m"), Var("f"), Var("x"), Var("l")
    return [
        Rule(Atom("uses_layer", (m, l)),
             (Atom("has_layer", (m, x)), Atom("same_kind", (x, l))),
             name="uses_layer_by_definition"),
        Rule(Atom("uses_layer", (m, l)),
             (Atom("method_of", (m, f)), Atom("calls", (f, x)), Atom("same_kind", (x, l))),
             name="uses_layer_by_method_call"),
        Rule(Atom("uses_layer", (m, l)),
             (Atom("calls", (m, x)), Atom("same_kind", (x, l))),
             name="uses_layer_by_call"),
    ]


def absence_rule_equality() -> Rule:
    """D5 closed world, now over the congruence-respecting ``uses_layer``."""
    m, l = Var("m"), Var("l")
    return Rule(
        Atom("absent", (m, l)),
        (Atom("is_module", (m,)), Atom("candidate_layer", (l,)),
         NegAtom(Atom("uses_layer", (m, l)))),
        name="absent_by_closed_world_equality",
    )


def symbols_in(atoms: Iterable[Atom]) -> List[str]:
    """Every ground constant occurring in ``atoms`` (the finite equality domain)."""
    return sorted({t.name for a in atoms for t in a.args if isinstance(t, Const)})