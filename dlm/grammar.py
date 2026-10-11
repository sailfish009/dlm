"""Module 20: reading as a data-driven rewrite grammar -- parse-as-derivation.

The reader is seam B: a *proposer*.  What this module adds (NOTE.md Part II / the
Lisp layer discussion) is making that proposal **verifiable** by writing reading
as **grammar-as-data** instead of hand-coded branches.  Each rule is a
:class:`RewriteRule` -- data, inspectable and enumerable -- not a Python ``if``.

    sentence --(whole-sentence pattern match)--> Derivation --| replay |--> Frame

Reading is then a *derivation* that can be replayed (:func:`verify_reading`), the
same way a proof is re-checked by the kernel.  A sentence with no matching rule
abstains.  Ambiguity is preserved (all derivations are returned), never resolved
by guessing.  This is stdlib-only; matching never evaluates text.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .lexicon import PredicateLexicon
from .logic import Const, Frame, Term
from .reader import (
    AGENT,
    AUXILIARIES,
    COPULAS,
    DEFAULT_PREPOSITIONS,
    FIGURE,
    GROUND,
    NEGATIONS,
    PATIENT,
    SUBJECT,
    tokenize,
)

__all__ = [
    "RewriteRule",
    "Derivation",
    "Reading",
    "GrammarReader",
    "DEFAULT_RULES",
    "verify_reading",
]

#: A pattern token is a literal word, ``?name`` (any token) or ``?name:cat``.
_CATEGORIES = frozenset({"ent", "pred", "cop", "prep", "any"})

Role = Tuple[str, str]


@dataclass(frozen=True)
class RewriteRule:
    """One reading rule, as data.

    ``pattern`` is matched against the whole normalised token sequence, one
    token per position.  ``head`` is the ``?var`` whose token becomes the
    predicate; ``roles`` maps role names to ``?var`` fillers (or literals).
    """

    name: str
    pattern: Tuple[str, ...]
    head: str
    roles: Tuple[Role, ...]
    negated: bool = False

    def __post_init__(self) -> None:
        if not self.pattern:
            raise ValueError(f"rule {self.name!r} has an empty pattern")
        for tok in self.pattern:
            if tok.startswith("?"):
                _, _, cat = tok[1:].partition(":")
                if cat and cat not in _CATEGORIES:
                    raise ValueError(f"rule {self.name!r}: unknown category {cat!r}")
        if not self.head.startswith("?"):
            raise ValueError(f"rule {self.name!r}: head must be a ?variable")
        for _, ref in self.roles:
            if ref.startswith("?"):
                if ref[1:].partition(":")[0] not in _pattern_vars(self.pattern):
                    raise ValueError(f"rule {self.name!r}: role {ref!r} not bound by pattern")
        if not self.roles:
            raise ValueError(f"rule {self.name!r}: needs at least one role")


def _pattern_vars(pattern: Sequence[str]) -> frozenset:
    return frozenset(t[1:].partition(":")[0] for t in pattern if t.startswith("?"))


@dataclass(frozen=True)
class Derivation:
    """The verifiable record of one whole-sentence rule match."""

    rule_name: str
    tokens: Tuple[str, ...]
    bindings: Tuple[Tuple[str, str], ...]

    def binding(self, name: str) -> Optional[str]:
        for k, v in self.bindings:
            if k == name:
                return v
        return None

    def __str__(self) -> str:
        env = " ".join(f"{k}={v}" for k, v in self.bindings)
        return f"(derive {self.rule_name} ({env}))"


@dataclass(frozen=True)
class Reading:
    """A frame (the proposal) and the derivation (the why) that produced it."""

    frame: Frame
    derivation: Derivation


# -- the default grammar (equivalent to the closed subset of LexicalReader) --
DEFAULT_RULES: Tuple[RewriteRule, ...] = (
    RewriteRule("intransitive", ("?e0:ent", "?v:pred"), "?v", ((AGENT, "?e0"),)),
    RewriteRule(
        "transitive",
        ("?e0:ent", "?v:pred", "?e1:ent"),
        "?v",
        ((AGENT, "?e0"), (PATIENT, "?e1")),
    ),
    RewriteRule("copula_noun", ("?e0:ent", "?c:cop", "?v:pred"), "?v", ((SUBJECT, "?e0"),)),
    RewriteRule(
        "copula_prep",
        ("?e0:ent", "?c:cop", "?p:prep", "?e1:ent"),
        "?p",
        ((FIGURE, "?e0"), (GROUND, "?e1")),
    ),
)


class GrammarReader:
    """A :class:`~dlm.reader.Reader` driven by :class:`RewriteRule` data.

    Rules live in ``self.rules`` and can be added/replaced without touching code,
    which is what makes the reader inspectable: coverage, ambiguity and each
    derivation are all outputs of the same data.
    """

    def __init__(
        self,
        predicates: Iterable[str] = (),
        prepositions: Iterable[str] = DEFAULT_PREPOSITIONS,
        *,
        rules: Optional[Iterable[RewriteRule]] = None,
        copulas: Iterable[str] = COPULAS,
        lexicon: Optional[PredicateLexicon] = None,
    ) -> None:
        self.predicates = frozenset(predicates)
        self.prepositions = frozenset(prepositions)
        self.copulas = frozenset(copulas)
        # With a lexicon, a predicate token may be inflected and is canonicalised
        # to its base form; without one, the exact token must be declared.
        self.lexicon = lexicon
        self.rules: List[RewriteRule] = list(rules if rules is not None else DEFAULT_RULES)

    # -- public ------------------------------------------------------------
    def add_rule(self, rule: RewriteRule) -> "GrammarReader":
        self.rules.append(rule)
        return self

    def normalize(self, sentence: str) -> Tuple[Tuple[str, ...], bool]:
        """Tokens as the grammar sees them: negations/auxiliaries removed."""
        negated = False
        kept: List[str] = []
        for t in tokenize(sentence):
            if t in NEGATIONS:
                negated = True
                continue
            if t in AUXILIARIES:
                continue
            kept.append(t)
        return tuple(kept), negated

    def read(self, sentence: str) -> Tuple[Frame, ...]:
        out: List[Frame] = []
        for reading in self.read_with_proof(sentence):
            if reading.frame not in out:
                out.append(reading.frame)
        return tuple(out)

    def read_with_proof(self, sentence: str) -> Tuple[Reading, ...]:
        tokens, negated = self.normalize(sentence)
        out: List[Reading] = []
        for rule in self.rules:
            reading = self._match(rule, tokens, negated)
            if reading is not None and reading.frame not in [r.frame for r in out]:
                out.append(reading)
        return tuple(out)

    # -- internals ---------------------------------------------------------
    def _is_pred(self, token: str) -> bool:
        if self.lexicon is not None:
            return self.lexicon.is_pred(token)
        return token in self.predicates

    def _is_entity(self, token: str) -> bool:
        return (
            token not in self.copulas
            and token not in self.prepositions
            and not self._is_pred(token)
        )

    def _category_ok(self, cat: str, token: str) -> bool:
        if cat == "any":
            return True
        if cat == "ent":
            return self._is_entity(token)
        if cat == "pred":
            return self._is_pred(token)
        if cat == "cop":
            return token in self.copulas
        if cat == "prep":
            return token in self.prepositions
        raise ValueError(f"unknown category {cat!r}")

    def _match_token(self, pattern: str, token: str, bindings: Dict[str, str]) -> bool:
        if not pattern.startswith("?"):
            return pattern == token
        name, _, cat = pattern[1:].partition(":")
        if not self._category_ok(cat or "any", token):
            return False
        if name in bindings:
            return bindings[name] == token
        bindings[name] = token
        return True

    def _resolve(self, ref: str, bindings: Dict[str, str]) -> Optional[str]:
        if ref.startswith("?"):
            return bindings.get(ref[1:])
        return ref

    def _match(self, rule: RewriteRule, tokens: Tuple[str, ...], negated: bool) -> Optional[Reading]:
        if len(rule.pattern) != len(tokens):
            return None
        bindings: Dict[str, str] = {}
        for pattern, token in zip(rule.pattern, tokens):
            if not self._match_token(pattern, token, bindings):
                return None
        head = self._resolve(rule.head, bindings)
        if head is None:
            return None
        if self.lexicon is not None:
            head = self.lexicon.canonical(head)
        slots: List[Tuple[str, Term]] = []
        for role, ref in rule.roles:
            value = self._resolve(ref, bindings)
            if value is None:
                return None
            slots.append((role, Const(value)))
        frame = Frame(head, tuple(slots), rule.negated or negated)
        derivation = Derivation(
            rule_name=rule.name,
            tokens=tokens,
            bindings=tuple(sorted(bindings.items())),
        )
        return Reading(frame, derivation)


def verify_reading(reader: GrammarReader, sentence: str, reading: Reading) -> bool:
    """Replay one reading: re-match its rule and confirm the same frame.

    This is the reader's analogue of :func:`dlm.kernel.verify` -- a proposal is
    accepted only if the derivation reproduces it from the sentence.
    """
    if not isinstance(reading, Reading):
        return False
    tokens, negated = reader.normalize(sentence)
    for rule in reader.rules:
        if rule.name != reading.derivation.rule_name:
            continue
        produced = reader._match(rule, tokens, negated)
        return produced is not None and produced.frame == reading.frame
    return False