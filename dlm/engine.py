"""Deduction over the KB: sound and complete (module 5).

Three operations, all sharing one forward-chaining core:

  * ``closure(kb)`` -- forward chaining to the least fixpoint; returns every
    derivable ground atom. This is the *evaluation* that logic self-supervision
    (B) uses as its correctness criterion.
  * ``prove(kb, goal)`` -- a re-checkable ``Proof`` certificate for a ground goal,
    or ``None``. The certificate is **reconstructed from the closure's support**
    (which rule instance first derived each atom), so it is complete by
    construction and can never disagree with ``entails``.

Why not backward SLD with a loop check? A path-based loop check is *incomplete*
on cyclic data: it rejects a valid ground atom whose only derivation goes around
a cycle (e.g. ``parent a b, parent b a`` entails ``ancestor a a``). Building the
certificate from the least-fixpoint support removes that class of bugs entirely:
every atom in the least fixpoint has a finite, well-founded support, and support
links strictly decrease in addition time, so reconstruction terminates.

Negation is never derived. ``holds`` checks a positive literal against the
closure and a negative literal against the KB side table.
"""
from __future__ import annotations

from typing import Dict, Iterable, Optional, Protocol, Set, Tuple, runtime_checkable

from .kb import KnowledgeBase
from .kernel import Proof
from .logic import Atom, Literal
from .unify import Subst, apply_atom, unify

__all__ = ["closure", "entails", "prove", "holds", "Retriever"]


@runtime_checkable
class Retriever(Protocol):
    """Seam B': an untrusted proposer that ranks candidate atoms to try.

    It only *orders* the search space; it never asserts. The proof kernel (C)
    still decides. Implemented by the learned scorer in ``selfsup.py``.
    """

    def retrieve(
        self, kb: KnowledgeBase, candidates: Iterable[Atom], *, limit: Optional[int] = None
    ) -> Tuple[Atom, ...]:
        ...


# -- forward chaining (shared core) ----------------------------------------
def _match(atoms: Tuple[Atom, ...], index: Dict[str, Set[Atom]], subst: Subst):
    """Yield every substitution making all ``atoms`` true in ``index``."""
    if not atoms:
        yield subst
        return
    first, rest = atoms[0], atoms[1:]
    for fact in tuple(index.get(first.pred, ())):
        s2 = unify(first, fact, subst)
        if s2 is not None:
            yield from _match(rest, index, s2)


def _derivations(kb: KnowledgeBase):
    """Forward chaining to fixpoint.

    Returns ``(index, support)`` where ``index`` maps a predicate to the set of
    derivable ground atoms and ``support[atom]`` records how the atom was first
    derived: ``("fact", None, None)`` or ``("rule", rule, substitution)``.
    """
    index: Dict[str, Set[Atom]] = {}
    support: Dict[Atom, Tuple] = {}
    for f in kb.facts():
        index.setdefault(f.pred, set()).add(f)
        support[f] = ("fact", None, None)

    changed = True
    while changed:
        changed = False
        for rule in kb.rules():
            for subst in _match(rule.body, index, {}):
                head = apply_atom(rule.head, subst)
                if not head.is_ground():
                    continue
                bucket = index.setdefault(head.pred, set())
                if head in bucket:
                    continue
                bucket.add(head)
                support[head] = ("rule", rule, dict(subst))
                changed = True
    return index, support


def closure(kb: KnowledgeBase) -> Set[Atom]:
    """All ground atoms derivable from ``kb`` (facts + Horn rules)."""
    index, _ = _derivations(kb)
    return {f for fs in index.values() for f in fs}


def entails(kb: KnowledgeBase, atom: Atom) -> bool:
    return atom in closure(kb)


def holds(kb: KnowledgeBase, literal: Literal) -> bool:
    """A positive literal by closure; a negative literal only by the side table."""
    if literal.negated:
        return kb.is_negated(literal.atom)
    return entails(kb, literal.atom)


# -- certificates: reconstruct from the closure's support ------------------
def _build_proof(atom: Atom, support: Dict[Atom, Tuple], memo: Dict[Atom, Proof]) -> Proof:
    cached = memo.get(atom)
    if cached is not None:
        return cached
    kind, rule, subst = support[atom]
    if kind == "fact":
        proof = Proof(atom, None, ())
    else:
        body = tuple(apply_atom(b, subst) for b in rule.body)
        premises = tuple(_build_proof(b, support, memo) for b in body)
        proof = Proof(atom, rule, premises)
    memo[atom] = proof
    return proof


def prove(kb: KnowledgeBase, goal: Atom) -> Optional[Proof]:
    """Return a re-checkable certificate for a **ground** goal, or ``None``.

    Complete w.r.t. :func:`entails`: ``prove`` succeeds iff ``goal`` is in the
    closure. For a non-ground goal it returns ``None`` (abstain) -- use
    :func:`closure` / :func:`entails` for existential questions.
    """
    if not goal.is_ground():
        return None
    _, support = _derivations(kb)
    if goal not in support:
        return None
    return _build_proof(goal, support, {})