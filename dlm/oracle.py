"""Module 17: the external evidence channel -- web-as-oracle, kept as *evidence*.

DLM must be able to acquire axioms.  A tempting shortcut is to look the claim up
on the web and "verify" it there, using web agreement the way reinforcement
learning uses a reward.  That is a useful *signal* but it is **not soundness**:

* the web is noisy, incomplete and adversarial;
* sources are correlated (Wikipedia backs Wikidata), so "agreement" is not
  independence;
* absence is not falsity, so a failed lookup must **abstain**, never negate;
* a learner rewarded by "looks true on the web" can be gamed (Goodhart).

This module therefore models the web (and any other lookup) as an
:class:`Evidence` channel: a count of independent confirmations, contradictions
and unknowns.  A channel only ever *proposes* a tier; the promotion policy is a
single auditable function (:func:`decide`) and the proof / rule check in
``axiom.py`` remains the sound gate.  Nothing here asserts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, Tuple, runtime_checkable

from .logic import Atom

__all__ = [
    "Evidence",
    "Oracle",
    "StaticOracle",
    "combine",
    "decide",
    "CERTIFY",
    "REJECT",
    "CANDIDATE",
]

CERTIFY = "certify"
REJECT = "reject"
CANDIDATE = "candidate"


@dataclass(frozen=True)
class Evidence:
    """Counts of independent channels that confirm / contradict / are silent.

    ``sources`` records which channels spoke, so a promotion is auditable.  The
    counts are deliberately coarse: the point is a *policy*, not a probability.
    """

    confirm: int = 0
    contradict: int = 0
    unknown: int = 0
    sources: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("confirm", "contradict", "unknown"):
            if getattr(self, name) < 0:
                raise ValueError(f"evidence count {name} must be non-negative")

    @property
    def known(self) -> int:
        return self.confirm + self.contradict

    def decision(self, *, min_confirm: int = 2) -> str:
        """The promotion policy.  Any contradiction rejects; else need ``min_confirm``."""
        if self.contradict > 0:
            return REJECT
        if self.confirm >= min_confirm:
            return CERTIFY
        return CANDIDATE

    def __add__(self, other: "Evidence") -> "Evidence":
        if not isinstance(other, Evidence):
            return NotImplemented
        return Evidence(
            self.confirm + other.confirm,
            self.contradict + other.contradict,
            self.unknown + other.unknown,
            tuple(dict.fromkeys(self.sources + other.sources)),
        )


@runtime_checkable
class Oracle(Protocol):
    """An external lookup.  It returns evidence about a *ground atom*, never a verdict."""

    def check(self, item: Atom) -> Evidence:  # pragma: no cover - protocol
        ...


def combine(channels: Iterable[Evidence], *, sources: Tuple[str, ...] = ()) -> Evidence:
    """Sum independent channels into one pooled evidence record."""
    total = Evidence(sources=sources)
    for e in channels:
        total = total + e
    return total


def decide(evidence: Evidence, *, min_confirm: int = 2) -> str:
    """The one place the web-evidence policy lives (see :meth:`Evidence.decision`)."""
    return evidence.decision(min_confirm=min_confirm)


class StaticOracle:
    """A deterministic oracle over caller-supplied sets (tests and ablations).

    Used to ask "if the external channel were perfectly right / wrong / silent,
    what would the gate do?"  It is the honest way to test the policy without a
    live network.
    """

    def __init__(
        self,
        true_items: Iterable[Atom] = (),
        false_items: Iterable[Atom] = (),
        *,
        source: str = "static",
        silent_is_unknown: bool = True,
    ) -> None:
        self._true = set(true_items)
        self._false = set(false_items)
        self._source = source
        self._silent_is_unknown = bool(silent_is_unknown)

    def check(self, item: Atom) -> Evidence:
        confirm = 1 if item in self._true else 0
        contradict = 1 if item in self._false else 0
        unknown = 0 if (confirm or contradict) else (1 if self._silent_is_unknown else 0)
        return Evidence(confirm, contradict, unknown, (self._source,))