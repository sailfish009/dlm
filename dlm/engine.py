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
from .logic import Atom, Const, Literal, Var
from .unify import Subst, apply_atom, unify, walk

__all__ = ["closure", "derivations", "entails", "prove", "prove_from_support", "holds", "Retriever"]


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
class _Store:
    """A predicate->atoms index plus an argument->atoms index for joins.

    The argument index lets a join start from the smallest bucket instead of
    scanning every atom of a predicate.  That is what keeps transitive closure
    from being quadratic in the number of edges.
    """

    __slots__ = ("by_pred", "by_arg", "size")

    def __init__(self) -> None:
        self.by_pred: Dict[str, Set[Atom]] = {}
        self.by_arg: Dict[str, Dict[int, Dict[Const, Set[Atom]]]] = {}
        self.size = 0

    def add(self, atom: Atom) -> bool:
        bucket = self.by_pred.setdefault(atom.pred, set())
        if atom in bucket:
            return False
        bucket.add(atom)
        self.size += 1
        per_pos = self.by_arg.setdefault(atom.pred, {})
        for i, arg in enumerate(atom.args):
            if isinstance(arg, Const):
                per_pos.setdefault(i, {}).setdefault(arg, set()).add(atom)
        return True

    def candidates(self, atom: Atom, subst: Subst) -> Iterable[Atom]:
        best: Optional[Set[Atom]] = None
        for i, arg in enumerate(atom.args):
            bound = walk(arg, subst)
            if isinstance(bound, Const):
                bucket = self.by_arg.get(atom.pred, {}).get(i, {}).get(bound)
                if bucket is None:
                    return ()
                if best is None or len(bucket) < len(best):
                    best = bucket
        if best is not None:
            return tuple(best)
        return tuple(self.by_pred.get(atom.pred, ()))

    def atoms(self) -> Iterable[Atom]:
        for bucket in self.by_pred.values():
            yield from bucket


def _match(atoms: Tuple[Atom, ...], index: _Store, subst: Subst):
    """Yield every substitution making all ``atoms`` true in ``index``."""
    return _match_sources(atoms, (index,) * len(atoms), subst)


def _match_sources(atoms: Tuple[Atom, ...], stores: Tuple[_Store, ...], subst: Subst):
    """Like :func:`_match`, but each atom joins against its own store.

    Semi-naive evaluation needs one body position restricted to the *delta* set
    while the rest use the full index.
    """
    if not atoms:
        yield subst
        return
    first, rest = atoms[0], atoms[1:]
    for fact in stores[0].candidates(first, subst):
        s2 = unify(first, fact, subst)
        if s2 is not None:
            yield from _match_sources(rest, stores[1:], s2)


def _derivations(kb: KnowledgeBase):
    """Forward chaining to fixpoint (semi-naive / delta rules).

    Returns ``(index, support)`` where ``index`` maps a predicate to the set of
    derivable ground atoms and ``support[atom]`` records how the atom was first
    derived: ``("fact", None, None)`` or ``("rule", rule, substitution)``.

    Everything derivable in the previous round is already in ``index``, so a rule
    instance whose body is entirely old has been fired; only instances with at
    least one body atom from the previous round's *delta* can add anything.  That
    turns the ``while changed`` full re-join into a per-delta join and keeps the
    same least fixpoint (and therefore the same atom set).
    """
    index = _Store()
    delta = _Store()
    support: Dict[Atom, Tuple] = {}
    for f in kb.facts():
        if index.add(f):
            delta.add(f)
        support[f] = ("fact", None, None)

    rules = tuple(kb.rules())
    while delta.size:
        new = _Store()
        new_support: Dict[Atom, Tuple] = {}
        for rule in rules:
            body = rule.body
            if not body:
                continue
            n = len(body)
            for j in range(n):
                stores = (index,) * n
                stores = stores[:j] + (delta,) + stores[j + 1:]
                for subst in _match_sources(body, stores, {}):
                    head = apply_atom(rule.head, subst)
                    if not head.is_ground():
                        continue
                    if head in index.by_pred.get(head.pred, ()) or head in new.by_pred.get(head.pred, ()):
                        continue
                    new.add(head)
                    new_support[head] = ("rule", rule, dict(subst))
        for atom in new.atoms():
            index.add(atom)
        support.update(new_support)
        delta = new
    return index.by_pred, support


def closure(kb: KnowledgeBase) -> Set[Atom]:
    """All ground atoms derivable from ``kb`` (facts + Horn rules)."""
    index, _ = _derivations(kb)
    return {f for fs in index.values() for f in fs}


def derivations(kb: KnowledgeBase):
    """Public ``(index, support)`` from :func:`_derivations`.

    Exposed so a caller that must certify *many* goals against one immutable KB
    runs forward chaining once and reuses the support, instead of paying for a
    full closure on every :func:`prove`.  The support is valid only while the KB
    is unchanged; recompute it after any edit.
    """
    return _derivations(kb)


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


def prove_from_support(goal: Atom, support: Dict[Atom, Tuple]) -> Optional[Proof]:
    """Re-checkable certificate for a ground ``goal`` from a precomputed support.

    Identical to :func:`prove` except that the caller supplies the support from
    :func:`derivations`, so many goals share one forward-chaining pass.
    """
    if not goal.is_ground():
        return None
    if goal not in support:
        return None
    return _build_proof(goal, support, {})


def prove(kb: KnowledgeBase, goal: Atom) -> Optional[Proof]:
    """Return a re-checkable certificate for a **ground** goal, or ``None``.

    Complete w.r.t. :func:`entails`: ``prove`` succeeds iff ``goal`` is in the
    closure. For a non-ground goal it returns ``None`` (abstain) -- use
    :func:`closure` / :func:`entails` for existential questions.
    """
    _, support = _derivations(kb)
    return prove_from_support(goal, support)