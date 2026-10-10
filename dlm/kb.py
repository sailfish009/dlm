"""Knowledge base: facts + definite Horn rules + a negation side table (module 4),
and the state-grounding seam A (NOTE.md Part III).

Facts are ground atoms. Rules are definite Horn clauses. Negation is NOT
derivable: an explicit negative is stored in a side table and can only be
*checked*, never produced by deduction. Predicate indexing keeps retrieval cheap
on a small host.

Seam A -- ``state -> facts``. Structured state (a ``dict`` of fields) is NOT
natural language (NOTE.md §27); it is *grounded* into predicate frames here. A
:class:`StateGrounder` is an untrusted proposer (like :class:`~dlm.reader.Reader`):
it proposes role-labelled frames and :meth:`SchemaRegistry.normalize` disposes of
them. ``DictStateGrounder`` is the deterministic reference implementation.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol, Tuple, runtime_checkable

from .logic import Atom, Const, Frame, Rule, Term

__all__ = ["KnowledgeBase", "StateBinding", "StateGrounder", "DictStateGrounder"]


class KnowledgeBase:
    def __init__(self) -> None:
        self._facts: Dict[str, set] = {}
        self._rules: List[Rule] = []
        self._rules_by_head: Dict[str, List[Rule]] = {}
        self._negations: set = set()

    # -- construction ------------------------------------------------------
    def add_fact(self, atom: Atom) -> "KnowledgeBase":
        if not isinstance(atom, Atom):
            raise TypeError(f"fact must be an Atom, got {atom!r}")
        if not atom.is_ground():
            raise ValueError(f"a fact must be ground: {atom}")
        self._facts.setdefault(atom.pred, set()).add(atom)
        return self

    def add_rule(self, rule: Rule) -> "KnowledgeBase":
        if not isinstance(rule, Rule):
            raise TypeError(f"rule must be a Rule, got {rule!r}")
        if rule in self._rules:
            return self
        self._rules.append(rule)
        self._rules_by_head.setdefault(rule.head.pred, []).append(rule)
        return self

    def add_facts(self, atoms: Iterable[Atom]) -> "KnowledgeBase":
        """Add many ground facts at once (e.g. the output of seam A)."""
        for atom in atoms:
            self.add_fact(atom)
        return self

    def add_negation(self, atom: Atom) -> "KnowledgeBase":
        """Record an explicit negative fact in the side table (never derived)."""
        if not isinstance(atom, Atom):
            raise TypeError(f"negation must be an Atom, got {atom!r}")
        if not atom.is_ground():
            raise ValueError(f"an explicit negative must be ground: {atom}")
        self._negations.add(atom)
        return self

    def copy(self) -> "KnowledgeBase":
        """Independent duplicate (same immutable facts/rules, fresh indexes)."""
        other = KnowledgeBase()
        other._facts = {pred: set(fs) for pred, fs in self._facts.items()}
        other._rules = list(self._rules)
        other._rules_by_head = {h: list(rs) for h, rs in self._rules_by_head.items()}
        other._negations = set(self._negations)
        return other

    # -- queries -----------------------------------------------------------
    def facts(self) -> Tuple[Atom, ...]:
        return tuple(f for fs in self._facts.values() for f in fs)

    def facts_by_pred(self, pred: str) -> Tuple[Atom, ...]:
        return tuple(self._facts.get(pred, ()))

    def has_fact(self, atom: Atom) -> bool:
        return atom in self._facts.get(atom.pred, ())

    def is_negated(self, atom: Atom) -> bool:
        return atom in self._negations

    def negations(self) -> Tuple[Atom, ...]:
        return tuple(self._negations)

    def rules(self) -> Tuple[Rule, ...]:
        return tuple(self._rules)

    def rules_by_head(self, pred: str) -> Tuple[Rule, ...]:
        return tuple(self._rules_by_head.get(pred, ()))

    def has_rule(self, rule: Rule) -> bool:
        return rule in self._rules

    def remove_rule(self, rule: Rule) -> "KnowledgeBase":
        """Drop ``rule`` if present (idempotent); rebuilds the head index."""
        if rule not in self._rules:
            return self
        self._rules = [r for r in self._rules if r != rule]
        self._rules_by_head = {}
        for r in self._rules:
            self._rules_by_head.setdefault(r.head.pred, []).append(r)
        return self

    def remove_fact(self, atom: Atom) -> "KnowledgeBase":
        """Drop ``atom`` if present (idempotent); prunes an empty predicate bucket."""
        bucket = self._facts.get(atom.pred)
        if bucket is None:
            return self
        bucket.discard(atom)
        if not bucket:
            del self._facts[atom.pred]
        return self

    def remove_negation(self, atom: Atom) -> "KnowledgeBase":
        """Drop an explicit negative if present (idempotent)."""
        self._negations.discard(atom)
        return self

    def predicates(self) -> Tuple[str, ...]:
        return tuple(sorted(set(self._facts) | set(self._rules_by_head)))

    def __len__(self) -> int:
        return sum(len(fs) for fs in self._facts.values())


# -- seam A: state -> facts -------------------------------------------------
@dataclass(frozen=True)
class StateBinding:
    """Declares how one structured-state field grounds into a predicate frame.

    ``key`` is the state field, ``pred`` the predicate it grounds to, and
    ``roles`` the ordered roles its value(s) fill. A one-role binding consumes a
    scalar value; a multi-role binding consumes a ``mapping`` of role to filler
    or a sequence aligned with ``roles``.
    """

    key: str
    pred: str
    roles: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.roles:
            raise ValueError(f"state binding {self.key!r} needs at least one role")
        if len(set(self.roles)) != len(self.roles):
            raise ValueError(f"duplicate roles in state binding {self.key!r}: {self.roles}")


@runtime_checkable
class StateGrounder(Protocol):
    """Seam A. A CLM state head / learned encoder may replace the reference impl.

    The contract: given a structured state, return the tuple of role-labelled
    frame proposals it can ground. ``()`` means abstain. Like a reader, a state
    grounder is a proposer and is untrusted -- only the kernel asserts.
    """

    def ground(self, state: object) -> Tuple[Frame, ...]:  # pragma: no cover - protocol
        ...


class DictStateGrounder:
    """The deterministic reference :class:`StateGrounder`.

    It only grounds fields it has a :class:`StateBinding` for; undeclared fields
    are dropped (or, with ``strict=True``, make the whole state abstain). Values
    are never guessed: a string/int becomes a constant, a bool becomes
    ``true``/``false``, and anything else is ungroundable (abstain). No case
    folding is applied -- the caller owns identifier canonicalization.
    """

    def __init__(self, bindings: Iterable[StateBinding] = (), *, strict: bool = False) -> None:
        self._by_key: Dict[str, StateBinding] = {}
        for binding in bindings:
            if binding.key in self._by_key:
                raise ValueError(f"duplicate state binding for key {binding.key!r}")
            self._by_key[binding.key] = binding
        self.strict = strict

    @property
    def bindings(self) -> Tuple[StateBinding, ...]:
        return tuple(self._by_key.values())

    def ground(self, state: object) -> Tuple[Frame, ...]:
        if not isinstance(state, Mapping):
            return ()
        frames: List[Frame] = []
        for key, value in state.items():
            binding = self._by_key.get(key)
            if binding is None:
                if self.strict:
                    return ()
                continue
            slots = self._slots(binding, value)
            if slots is None:
                if self.strict:
                    return ()
                continue
            frames.append(Frame(binding.pred, slots))
        return tuple(frames)

    @staticmethod
    def _term(value: object) -> Optional[Term]:
        if isinstance(value, bool):
            return Const("true" if value else "false")
        if isinstance(value, int):
            return Const(str(value))
        if isinstance(value, str):
            return Const(value)
        return None

    def _slots(self, binding: StateBinding, value: object):
        roles = binding.roles
        if len(roles) == 1:
            term = self._term(value)
            return None if term is None else ((roles[0], term),)
        if isinstance(value, Mapping):
            if set(value.keys()) != set(roles):
                return None
            slots = []
            for role in roles:
                term = self._term(value[role])
                if term is None:
                    return None
                slots.append((role, term))
            return tuple(slots)
        if isinstance(value, (list, tuple)):
            if len(value) != len(roles):
                return None
            slots = []
            for role, item in zip(roles, value):
                term = self._term(item)
                if term is None:
                    return None
                slots.append((role, term))
            return tuple(slots)
        return None

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"DictStateGrounder(bindings={self.bindings!r}, strict={self.strict})"