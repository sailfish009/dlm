"""Web -> DLM kernel bridge for the v0.0020 IR-SSL experiment.

The deduction side.  Web triples become function-free Horn atoms plus a few
transitivity / inheritance rules, and the fixed DLM kernel (``closure`` /
``prove``) derives the multi-hop truth that is then used as *free* labels.  The
kernel is the only thing allowed to assert.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure, prove


def C(name: str) -> Const:
    return Const(name)


def V(name: str) -> Var:
    return Var(name)


def A(pred: str, a, b) -> Atom:
    return Atom(pred, (a, b))


def fact_to_atom(f) -> Atom:
    return A(f.pred, C(f.subj), C(f.obj))


def default_rules() -> tuple:
    """Transitivity / inheritance rules -- the general laws the kernel applies."""
    x, y, z = V("x"), V("y"), V("z")
    return (
        Rule(A("subclass_of", x, z), (A("subclass_of", x, y), A("subclass_of", y, z)), "subclass_trans"),
        Rule(A("occupation", x, z), (A("occupation", x, y), A("subclass_of", y, z)), "occupation_up"),
        Rule(A("instance_of", x, z), (A("instance_of", x, y), A("subclass_of", y, z)), "instance_up"),
        Rule(A("located_in", x, z), (A("located_in", x, y), A("located_in", y, z)), "located_in_trans"),
        Rule(A("part_of", x, z), (A("part_of", x, y), A("part_of", y, z)), "part_of_trans"),
    )


def build_kb(hierarchy: Iterable, facts: Iterable) -> KnowledgeBase:
    kb = KnowledgeBase()
    for rule in default_rules():
        kb.add_rule(rule)
    for f in list(hierarchy) + list(facts):
        kb.add_fact(fact_to_atom(f))
    return kb


def derived_atoms(kb: KnowledgeBase, base: Iterable) -> set:
    """Atoms the kernel derives that were NOT stated directly (multi-hop truth)."""
    base_atoms = {fact_to_atom(f) for f in base}
    return closure(kb) - base_atoms


def can_prove(kb: KnowledgeBase, atom: Atom) -> bool:
    return prove(kb, atom) is not None
