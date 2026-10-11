"""Module 18: the trusted axiom store -- tiers, provenance, and a promotion gate.

DLM must *learn and store* axioms (facts and rules).  The trust invariant forbids
a proposer from asserting, so a learned axiom may not enter the engine's KB
directly.  This module splits knowledge into tiers:

* ``candidate`` -- proposed by a learner / reader / inducer.  **Never usable for
  deduction** (a candidate fact/rule is absent from every KB this store builds).
* ``external``  -- corroborated by an external evidence channel (web oracle),
  admitted only by an explicit, auditable policy.  Weaker than kernel trust, so
  it is opt-in via ``min_tier``.
* ``kernel``    -- re-checked by the kernel: a ``Proof`` for a fact, a finite
  domain entailment check for a rule.  Sound; this is what a proof may rest on.

The gate is structural: :meth:`AxiomStore.kb` only ever emits axioms whose tier
is at least the requested minimum, and the default minimum excludes candidates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

from .kb import KnowledgeBase
from .kernel import Proof, verify
from .logic import Atom, Rule
from .oracle import Evidence, decide

__all__ = [
    "Axiom",
    "AxiomStore",
    "PromoteError",
    "TIER_CANDIDATE",
    "TIER_EXTERNAL",
    "TIER_KERNEL",
    "TRUST",
]

TIER_CANDIDATE = "candidate"
TIER_EXTERNAL = "external"
TIER_KERNEL = "kernel"

#: Trust ordering.  A KB built with ``min_tier`` admits axioms with trust >= it.
TRUST: Dict[str, int] = {TIER_CANDIDATE: 0, TIER_EXTERNAL: 1, TIER_KERNEL: 2}

Item = Union[Atom, Rule]


class PromoteError(ValueError):
    """Raised when a promotion gate rejects an axiom (it stays at its old tier)."""


@dataclass(frozen=True)
class Axiom:
    """A stored fact or rule, its trust tier, and why we believe it."""

    kind: str  # "fact" | "rule"
    item: Item
    tier: str
    source: str
    detail: str = ""
    certificate: Optional[Proof] = None
    evidence: Optional[Evidence] = None

    def __post_init__(self) -> None:
        if self.kind not in ("fact", "rule"):
            raise ValueError(f"unknown axiom kind {self.kind!r}")
        if self.kind == "fact" and not isinstance(self.item, Atom):
            raise TypeError("a fact axiom must hold an Atom")
        if self.kind == "rule" and not isinstance(self.item, Rule):
            raise TypeError("a rule axiom must hold a Rule")
        if self.tier not in TRUST:
            raise ValueError(f"unknown tier {self.tier!r}")

    @property
    def trust(self) -> int:
        return TRUST[self.tier]

    def key(self) -> tuple:
        return (self.kind, self.item)


def _kind_of(item: Item) -> str:
    if isinstance(item, Atom):
        return "fact"
    if isinstance(item, Rule):
        return "rule"
    raise TypeError(f"an axiom item must be Atom or Rule, got {item!r}")


class AxiomStore:
    """A provenance-tracked store with a structural candidate/certified boundary."""

    def __init__(self, *, base: Optional[KnowledgeBase] = None) -> None:
        self._by_key: Dict[tuple, Axiom] = {}
        if base is not None:
            for fact in base.facts():
                self.register(fact, source="seed")
            for rule in base.rules():
                self.register(rule, source="seed")

    # -- population --------------------------------------------------------
    def register(
        self,
        item: Item,
        *,
        source: str,
        detail: str = "",
        tier: str = TIER_KERNEL,
        certificate: Optional[Proof] = None,
        evidence: Optional[Evidence] = None,
    ) -> Axiom:
        """Add an axiom directly at ``tier`` (default kernel; used for seeds)."""
        ax = Axiom(_kind_of(item), item, tier, source, detail, certificate, evidence)
        self._by_key[ax.key()] = ax
        return ax

    def propose(self, item: Item, *, source: str, detail: str = "") -> Axiom:
        """Record an untrusted proposal.  It is stored but unusable for deduction."""
        return self.register(item, source=source, detail=detail, tier=TIER_CANDIDATE)

    # -- the gate ----------------------------------------------------------
    def promote_fact(
        self,
        atom: Atom,
        proof: Proof,
        *,
        source: str = "kernel",
        kb: Optional[KnowledgeBase] = None,
        detail: str = "",
    ) -> Axiom:
        """Promote a fact to kernel tier iff ``proof`` re-checks against the KB.

        The KB defaults to the current *certified* (kernel-tier) store, so a
        proof may only rest on other kernel axioms -- never on candidates or
        external evidence.
        """
        if not isinstance(atom, Atom):
            raise TypeError("promote_fact expects an Atom")
        if proof is None or proof.atom != atom:
            raise PromoteError("proof does not prove this atom")
        base = kb if kb is not None else self.certified_kb()
        if not verify(proof, base):
            raise PromoteError("proof failed kernel re-check")
        return self.register(atom, source=source, detail=detail, tier=TIER_KERNEL, certificate=proof)

    def promote_rule(
        self,
        rule: Rule,
        verifier: Callable[[Rule], bool],
        *,
        source: str = "kernel",
        detail: str = "",
    ) -> Axiom:
        """Promote a rule to kernel tier iff ``verifier(rule)`` says it is valid.

        ``verifier`` is normally :func:`dlm.induce.verify_rule` bound to a KB, so
        the rule is checked over the finite domain rather than assumed.
        """
        if not isinstance(rule, Rule):
            raise TypeError("promote_rule expects a Rule")
        if not verifier(rule):
            raise PromoteError("rule failed kernel validity check")
        return self.register(rule, source=source, detail=detail, tier=TIER_KERNEL)

    def promote_external(
        self,
        item: Item,
        evidence: Evidence,
        *,
        source: str = "external",
        detail: str = "",
        min_confirm: int = 2,
    ) -> Axiom:
        """Promote by external evidence policy (a contradiction rejects)."""
        if decide(evidence, min_confirm=min_confirm) != "certify":
            raise PromoteError(f"external evidence insufficient: {evidence}")
        return self.register(item, source=source, detail=detail, tier=TIER_EXTERNAL, evidence=evidence)

    # -- queries -----------------------------------------------------------
    def _items(self, min_tier: str) -> Iterable[Axiom]:
        floor = TRUST[min_tier]
        return (ax for ax in self._by_key.values() if ax.trust >= floor)

    def kb(self, *, min_tier: str = TIER_EXTERNAL) -> KnowledgeBase:
        """Build a KB from axioms at or above ``min_tier``.

        Candidates are **never** admitted: asking for them is a programming
        error, not a silent downgrade (a proposer must not feed deduction).
        """
        if min_tier not in TRUST:
            raise ValueError(f"unknown tier {min_tier!r}")
        if min_tier == TIER_CANDIDATE:
            raise ValueError("candidate axioms are never usable for deduction")
        out = KnowledgeBase()
        for ax in self._items(min_tier):
            if ax.kind == "fact":
                out.add_fact(ax.item)
            else:
                out.add_rule(ax.item)
        return out

    def certified_kb(self) -> KnowledgeBase:
        """The sound KB: kernel-tier axioms only."""
        return self.kb(min_tier=TIER_KERNEL)

    def axioms(self, *, min_tier: str = TIER_CANDIDATE) -> Tuple[Axiom, ...]:
        return tuple(sorted(self._items(min_tier), key=lambda a: (a.kind, str(a.item))))

    def candidates(self) -> Tuple[Axiom, ...]:
        return tuple(ax for ax in self._by_key.values() if ax.tier == TIER_CANDIDATE)

    def promoted(self, *, min_tier: str = TIER_EXTERNAL) -> Tuple[Axiom, ...]:
        return self.axioms(min_tier=min_tier)

    def provenance(self, item: Item) -> Optional[Axiom]:
        return self._by_key.get((_kind_of(item), item))

    def summary(self) -> dict:
        counts: Dict[str, int] = {t: 0 for t in TRUST}
        for ax in self._by_key.values():
            counts[ax.tier] += 1
        return {"total": len(self._by_key), "by_tier": counts}