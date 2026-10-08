"""DLM v0.0001 — candidate retrieval with provenance.

Retrieval is the open-world part of the stack: given a goal atom, fetch the
facts and rules that could apply, indexed by predicate, and attach a feature
vector so the decider can rank them. Nothing is asserted as true here — a
retrieved item is a *candidate* until deduction (or the decider's entailment
check) accepts it.

Keeping retrieval separate from deduction matches the interface contract in
work.txt: retrieval is approximate, deduction is exact, and the decider is the
gate between them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .kb import KnowledgeBase
from .rules import Rule
from .terms import Atom, Const, Subst, Term, Var, unify_atom


@dataclass(frozen=True)
class Candidate:
    """A retrieved fact or rule plus features for the decider."""

    item: object  # Atom (fact) or Rule
    kind: str  # "fact" | "rule"
    features: Tuple[float, ...]
    source: str = "kb"

    def __str__(self) -> str:
        return f"{self.kind}:{self.item}"


def _var_names(atom_: Atom) -> frozenset:
    return frozenset(a.name for a in atom_.args if isinstance(a, Var))


def _const_names(atom_: Atom) -> frozenset:
    return frozenset(a.name for a in atom_.args if isinstance(a, Const))


def feature_vector(
    query: Atom, item: object, kind: str, kb: Optional[KnowledgeBase] = None
) -> Tuple[float, ...]:
    """Hand-built features shared by facts and rules.

    Order (fixed, decider depends on it):
      0 predicate match (1/0)
      1 arity match (1/0)
      2 shared constants (raw count, normalised by query arity)
      3 kind==fact
      4 kind==rule
      5 rule body length (0 for facts)
      6 variable overlap (1/0)
      7 fraction of a rule's body predicates backed by KB facts (1 for facts)
    """
    target = item.head if isinstance(item, Rule) else item
    pred = 1.0 if target.pred == query.pred else 0.0
    arity = 1.0 if len(target.args) == len(query.args) else 0.0
    shared = len(_const_names(query) & _const_names(target))
    denom = max(1, len(query.args))
    body_len = float(len(item.body)) if isinstance(item, Rule) else 0.0
    var_overlap = 1.0 if _var_names(query) & (
        _var_names(item.head) if isinstance(item, Rule) else _var_names(item)
    ) else 0.0
    if isinstance(item, Rule) and kb is not None and item.body:
        backed = sum(1 for b in item.body if kb.facts_for(b.pred))
        instantiable = backed / len(item.body)
    else:
        instantiable = 1.0 if isinstance(item, Atom) else 0.0
    return (
        pred,
        arity,
        shared / denom,
        1.0 if kind == "fact" else 0.0,
        1.0 if kind == "rule" else 0.0,
        body_len,
        var_overlap,
        instantiable,
    )


class Retriever:
    NUM_FEATURES = 8

    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    def retrieve(self, query: Atom, limit: Optional[int] = None) -> List[Candidate]:
        """Fetch candidate facts and rules for ``query``, predicate-indexed."""
        out: List[Candidate] = []
        for f in self.kb.facts_for(query.pred):
            out.append(Candidate(f, "fact", feature_vector(query, f, "fact", self.kb)))
        for r in self.kb.rules_for(query.pred):
            out.append(Candidate(r, "rule", feature_vector(query, r, "rule", self.kb)))
        if limit is not None:
            out = out[:limit]
        return out

    def matching_facts(self, query: Atom) -> List[Tuple[Atom, Subst]]:
        """Exact (not approximate) unification of query against stored facts."""
        hits: List[Tuple[Atom, Subst]] = []
        for f in self.kb.facts_for(query.pred):
            s = unify_atom(query, f)
            if s is not None:
                hits.append((f, s))
        return hits