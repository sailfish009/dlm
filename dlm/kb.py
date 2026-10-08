"""DLM v0.0001 — knowledge base with predicate indexing.

The KB stores ground facts and Horn rules, both indexed by predicate so that
retrieval and backward chaining can fetch candidates without scanning
everything. Predicate indexing is what keeps the engine usable on a 6 GB host:
memory scales with the number of distinct facts/rules, not with a dense table.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple

from .rules import Rule, fact
from .terms import Atom, Term


def _safe(r: Rule) -> bool:
    """Datalog safety: every head variable occurs in a positive body literal."""
    head_vars = set(r.head.vars())
    if not r.body:
        return not head_vars
    body_vars = set()
    for b in r.body:
        body_vars.update(b.vars())
    return head_vars <= body_vars


class KnowledgeBase:
    def __init__(self, check_safety: bool = True) -> None:
        self._facts: Dict[str, Set[Atom]] = {}
        self._rules: Dict[str, List[Rule]] = {}
        self._rule_names: Set[str] = set()
        self.check_safety = check_safety

    # -- mutation -----------------------------------------------------------
    def add_fact(self, a: Atom) -> bool:
        """Add a ground atom. Returns True if it was new."""
        if not a.is_ground():
            raise ValueError(f"fact must be ground: {a}")
        bucket = self._facts.setdefault(a.pred, set())
        if a in bucket:
            return False
        bucket.add(a)
        return True

    def add_rule(self, r: Rule) -> bool:
        """Add a Horn rule, indexed by head predicate. De-duplicates by name.

        Datalog safety is enforced: every head variable must appear in the
        body (set ``check_safety=False`` to bypass). Unsafe rules make SLD
        unsound on ground goals and are rejected by default.
        """
        if self.check_safety and not _safe(r):
            raise ValueError(f"unsafe rule (head variable not bound by body): {r}")
        bucket = self._rules.setdefault(r.head.pred, [])
        if r.name and r.name in self._rule_names:
            return False
        if r in bucket:
            return False
        bucket.append(r)
        if r.name:
            self._rule_names.add(r.name)
        return True

    # -- lookup -------------------------------------------------------------
    def facts_for(self, pred: str) -> Tuple[Atom, ...]:
        return tuple(self._facts.get(pred, ()))

    def rules_for(self, pred: str) -> Tuple[Rule, ...]:
        return tuple(self._rules.get(pred, ()))

    def has_fact(self, a: Atom) -> bool:
        return a in self._facts.get(a.pred, ())

    @property
    def predicates(self) -> Tuple[str, ...]:
        return tuple(sorted(set(self._facts) | set(self._rules)))

    @property
    def num_facts(self) -> int:
        return sum(len(b) for b in self._facts.values())

    @property
    def num_rules(self) -> int:
        return sum(len(b) for b in self._rules.values())

    def facts(self) -> Iterable[Atom]:
        for bucket in self._facts.values():
            yield from bucket

    def rules(self) -> Iterable[Rule]:
        for bucket in self._rules.values():
            yield from bucket

    def __repr__(self) -> str:  # pragma: no cover - debug only
        return f"KnowledgeBase(facts={self.num_facts}, rules={self.num_rules})"