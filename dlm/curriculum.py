"""DLM v0.0056 -- weakness-targeted self-improvement (untrusted).

This is the closed loop the model was missing: it does not wait for a human to
hand it a source list.  It

    1. ASSESS   the current ability from the kernel closure (dlm.ability)
    2. PICK     an actionable weak spot (an unproved target whose missing premise
                is externally acquirable)
    3. ASK      build a search request from that gap
    4. ACQUIRE  web search (abstain -- return no fact -- when evidence is missing)
    5. RE-CLOSE the enlarged knowledge base through the kernel
    6. SCORE    the round (which targets became provable) and repeat

It stops on a NAMED reason: ``saturated`` (no weak spot left), ``no_actionable``
(weak spots remain but nothing the web can supply), ``acquire_empty`` (the web
gave nothing), ``no_progress`` (a fact was added but no target improved), or
``max_rounds``.

``acquire`` is the only side-effecting seam and the only place the web is touched.
It MUST return ``{"facts": [...], "provenance": {...}}`` with provenance for every
fact it supplies, and abstain (empty facts) rather than invent.  That is what keeps
offline replay byte-for-byte deterministic.  The kernel remains the only judge;
this loop asserts nothing.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Sequence, Tuple

from . import Atom, Const, KnowledgeBase, Rule, closure
from .ability import (Ability, WeakSpot, ability_profile, improvement,
                      target_predicates, weak_spots)

__all__ = ["Round", "CurriculumResult", "run_curriculum", "pick_actionable",
           "close_with_rules"]

Acquire = Callable[[WeakSpot], dict]
Pick = Callable[[Sequence[WeakSpot]], Optional[WeakSpot]]


def _as_atom(x) -> Atom:
    if isinstance(x, Atom):
        return x
    return Atom(x[0], tuple(Const(t) for t in x[1:]))


def close_with_rules(facts: Iterable[Atom], rules: Sequence[Rule]) -> set:
    """The kernel closure of ``facts`` under ``rules`` -- the default oracle."""
    kb = KnowledgeBase({_as_atom(f) for f in facts})
    for r in rules:
        kb.add_rule(r)
    return closure(kb)


def pick_actionable(spots: Sequence[WeakSpot]) -> Optional[WeakSpot]:
    """Default agenda order: the first weak spot the web can actually fix."""
    for s in spots:
        if s.actionable:
            return s
    return None


@dataclass(frozen=True)
class Round:
    round: int
    kind: str
    target: str
    missing: Tuple[str, ...]
    query: str
    acquired: Tuple[Atom, ...]
    provenance: dict
    improved: bool
    gained: Tuple[str, ...]
    derived: int
    stop: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "round": self.round,
            "weak_spot": {"kind": self.kind, "target": self.target,
                          "missing": list(self.missing),
                          "query": self.query},
            "acquired": [str(a) for a in self.acquired],
            "provenance": self.provenance,
            "improved": self.improved,
            "gained": list(self.gained),
            "derived": self.derived,
            "stop": self.stop,
        }


@dataclass
class CurriculumResult:
    rounds: Tuple[Round, ...]
    facts: frozenset
    stop: str
    ability_before: Ability
    ability_after: Ability
    targets: Tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "stop": self.stop,
            "rounds": [r.to_dict() for r in self.rounds],
            "targets": list(self.targets),
            "ability_before": self.ability_before.to_dict(),
            "ability_after": self.ability_after.to_dict(),
            "facts": len(self.facts),
        }


def run_curriculum(facts: Iterable[Atom], rules: Sequence[Rule], *,
                   acquire: Acquire, external: Iterable[str] = (),
                   targets: Optional[Sequence[str]] = None, max_rounds: int = 8,
                   min_gain: int = 1, pick: Optional[Pick] = None,
                   close: Optional[Callable[[set], set]] = None,
                   evidence: Optional[dict] = None,
                   query_builder: Optional[Callable[[WeakSpot], str]] = None
                   ) -> CurriculumResult:
    """Run the assess -> ask -> acquire -> re-close -> score loop to a stop.

    ``targets`` is fixed once (default: every rule head plus fact predicate) so the
    agenda cannot drift as facts are acquired.  ``close`` defaults to the kernel
    closure of the facts under ``rules``; a caller may pass a typed/closed-world
    closure instead.
    """
    rules = tuple(rules)
    facts = {_as_atom(f) for f in facts}
    ext = frozenset(external)
    if targets is None:
        targets = target_predicates(rules, facts)
    targets = tuple(targets)
    close_fn = close or (lambda fs: close_with_rules(fs, rules))

    before = ability_profile(rules, close_fn(facts), facts=facts, external=ext,
                             targets=targets, evidence=evidence)
    first = before
    rounds = []
    stop: Optional[str] = None
    pick_fn = pick or pick_actionable
    for i in range(max_rounds):
        spots = weak_spots(before)
        if not spots:
            stop = "saturated"
            break
        action = pick_fn(spots)
        if action is None:
            stop = "no_actionable"
            break
        query = (query_builder(action) if query_builder is not None
                 else f"{action.target}({','.join(action.missing)})")
        got = acquire(action) or {}
        raw = list(got.get("facts", ()))
        newf = {_as_atom(x) for x in raw}
        prov = dict(got.get("provenance", {}) or {})
        query = got.get("query", query)
        if not newf:
            rounds.append(Round(i, action.kind, action.target, action.missing,
                                query, (), prov, False, (), before.derived_total,
                                "acquire_empty"))
            stop = "acquire_empty"
            break
        facts |= newf
        after = ability_profile(rules, close_fn(facts), facts=facts, external=ext,
                                targets=targets, evidence=evidence)
        imp = improvement(before, after)
        progress = (len(imp["gained"]) + len(imp["deepened"])) >= min_gain
        rstop = None if progress else "no_progress"
        rounds.append(Round(i, action.kind, action.target, action.missing, query,
                            tuple(sorted(newf, key=str)), prov, imp["improved"],
                            imp["gained"], after.derived_total, rstop))
        before = after
        if rstop:
            stop = rstop
            break
        if i + 1 >= max_rounds:
            stop = "max_rounds"
    if stop is None:
        stop = "max_rounds"
    return CurriculumResult(tuple(rounds), frozenset(facts), stop, first, before,
                            targets)