"""Module 23: the interrogative reader -- question patterns as data.

Seam B for questions.  The declarative :class:`~dlm.grammar.GrammarReader` reads
``E V E`` etc.; a question has a *different* surface order (do-support, subject/
aux inversion, wh-movement) and a different *output* (a :class:`~dlm.query.Query`,
not a proposition).  Keeping that in the same hand-coded branch is what made the
old pipeline unable to answer even ``is alice happy?``.

So this module is the reader's grammar-as-data for questions, exactly parallel to
``grammar.py``: every question form is a :class:`QuestionRule` (data), matching is
whole-sentence, ambiguity is preserved, and anything unmatched abstains.

The rule declares an optional predicate slot, role fillers, and (for wh) which
role is the hole ``?x`` or that the *predicate itself* is the answer.  The reader
returns :class:`Query` proposals; it never decides truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .lexicon import PredicateLexicon
from .logic import Const, Frame, SchemaRegistry, Term, Var
from .query import WH, YESNO, Query
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
    "WHO_WORDS",
    "HOLE",
    "QuestionRule",
    "QuestionReader",
    "DEFAULT_QUESTION_RULES",
    "looks_like_question",
]

#: Surface wh-words that open a question.
WHO_WORDS = frozenset({"who", "what", "where", "when", "which", "why", "how", "whose", "whom"})

#: The reserved variable name that marks the answer hole inside a rule's roles.
HOLE = "?x"

_CATEGORIES = frozenset({"ent", "pred", "cop", "prep", "aux", "any"})

Role = Tuple[str, str]


def _pattern_vars(pattern: Sequence[str]) -> frozenset:
    return frozenset(t[1:].partition(":")[0] for t in pattern if t.startswith("?"))


@dataclass(frozen=True)
class QuestionRule:
    """One interrogative reading rule, as data.

    ``head`` is the predicate ``?var`` (or a literal word); ``head=None`` means
    *enumerate* candidate predicates from the schema registry (a wh question that
    does not name its relation, e.g. ``where is alice?``).  ``head_class``
    restricts enumeration (``"prep"`` / ``"unary"`` / ``None``).
    """

    name: str
    kind: str
    pattern: Tuple[str, ...]
    head: Optional[str] = None
    roles: Tuple[Role, ...] = ()
    answer_role: Optional[str] = None
    answer_pred: bool = False
    focus: Optional[str] = None
    head_class: Optional[str] = None
    negated: bool = False

    def __post_init__(self) -> None:
        if self.kind not in (YESNO, WH):
            raise ValueError(f"rule {self.name!r}: unknown kind {self.kind!r}")
        if not self.pattern:
            raise ValueError(f"rule {self.name!r}: empty pattern")
        for tok in self.pattern:
            if tok.startswith("?"):
                _, _, cat = tok[1:].partition(":")
                if cat and cat not in _CATEGORIES:
                    raise ValueError(f"rule {self.name!r}: unknown category {cat!r}")
        if self.head is not None and not self.head.startswith("?"):
            raise ValueError(f"rule {self.name!r}: head must be a ?variable")
        bound = _pattern_vars(self.pattern)
        holes = 0
        for _, ref in self.roles:
            if ref == HOLE:
                holes += 1
            elif ref.startswith("?") and ref[1:] not in bound:
                raise ValueError(f"rule {self.name!r}: role {ref!r} not bound by pattern")
        if self.kind == YESNO:
            if holes:
                raise ValueError(f"rule {self.name!r}: a yes/no rule has no hole")
        elif self.answer_pred:
            if holes:
                raise ValueError(f"rule {self.name!r}: a predicate answer has no hole")
        elif holes != 1:
            raise ValueError(f"rule {self.name!r}: a wh term rule needs exactly one {HOLE}")


DEFAULT_QUESTION_RULES: Tuple[QuestionRule, ...] = (
    # -- yes/no ------------------------------------------------------------
    QuestionRule(
        "yesno_do",
        YESNO,
        ("?a:aux", "?e0:ent", "?v:pred", "?e1:ent"),
        head="?v",
        roles=((AGENT, "?e0"), (PATIENT, "?e1")),
    ),
    QuestionRule(
        "yesno_intrans_do",
        YESNO,
        ("?a:aux", "?e0:ent", "?v:pred"),
        head="?v",
        roles=((AGENT, "?e0"),),
    ),
    QuestionRule(
        "yesno_cop_pred",
        YESNO,
        ("?c:cop", "?e0:ent", "?v:pred"),
        head="?v",
        roles=((SUBJECT, "?e0"),),
    ),
    QuestionRule(
        "yesno_cop_prep",
        YESNO,
        ("?c:cop", "?e0:ent", "?p:prep", "?e1:ent"),
        head="?p",
        roles=((FIGURE, "?e0"), (GROUND, "?e1")),
    ),
    # -- wh with a named relation -----------------------------------------
    QuestionRule(
        "wh_who_do",
        WH,
        ("who", "?a:aux", "?e0:ent", "?v:pred"),
        head="?v",
        roles=((AGENT, "?e0"), (PATIENT, HOLE)),
        answer_role=PATIENT,
        focus="who",
    ),
    QuestionRule(
        "wh_what_do",
        WH,
        ("what", "?a:aux", "?e0:ent", "?v:pred"),
        head="?v",
        roles=((AGENT, "?e0"), (PATIENT, HOLE)),
        answer_role=PATIENT,
        focus="what",
    ),
    QuestionRule(
        "wh_where_do",
        WH,
        ("where", "?a:aux", "?e0:ent", "?v:pred"),
        head="?v",
        roles=((FIGURE, "?e0"), (GROUND, HOLE)),
        answer_role=GROUND,
        focus="where",
    ),
    # -- wh that does not name its relation (enumerate predicates) ---------
    QuestionRule(
        "wh_where_cop",
        WH,
        ("where", "?c:cop", "?e0:ent"),
        head=None,
        head_class="prep",
        roles=((FIGURE, "?e0"), (GROUND, HOLE)),
        answer_role=GROUND,
        focus="where",
    ),
    QuestionRule(
        "wh_who_cop",
        WH,
        ("who", "?c:cop", "?e0:ent"),
        head=None,
        head_class="prep",
        roles=((FIGURE, "?e0"), (GROUND, HOLE)),
        answer_role=GROUND,
        focus="who",
    ),
    QuestionRule(
        "wh_what_cop",
        WH,
        ("what", "?c:cop", "?e0:ent"),
        head=None,
        head_class="unary",
        roles=((SUBJECT, "?e0"),),
        answer_pred=True,
        focus="what",
    ),
)


def looks_like_question(sentence: str) -> bool:
    """True if the surface carries an interrogative marker (``?`` / wh / do)."""
    stripped = sentence.strip()
    if stripped.endswith("?"):
        return True
    tokens = tokenize(sentence)
    if not tokens:
        return False
    return tokens[0] in WHO_WORDS or tokens[0] in AUXILIARIES

class QuestionReader:
    """Read a sentence into :class:`Query` proposals via :class:`QuestionRule` data.

    Untrusted (seam B): it proposes candidate goal patterns and enumerates
    candidate predicates from the *schema registry* (data).  The resolver
    (:mod:`dlm.answer`) is what uses the kernel to decide.
    """

    def __init__(
        self,
        predicates: Iterable[str] = (),
        registry: Optional[SchemaRegistry] = None,
        prepositions: Iterable[str] = DEFAULT_PREPOSITIONS,
        *,
        lexicon: Optional[PredicateLexicon] = None,
        rules: Optional[Iterable[QuestionRule]] = None,
        copulas: Iterable[str] = COPULAS,
    ) -> None:
        self.predicates = frozenset(predicates)
        self.lexicon = lexicon if lexicon is not None else PredicateLexicon(predicates)
        self.registry = registry if registry is not None else SchemaRegistry()
        self.prepositions = frozenset(prepositions)
        self.copulas = frozenset(copulas)
        self.rules: List[QuestionRule] = list(
            rules if rules is not None else DEFAULT_QUESTION_RULES
        )

    # -- public ------------------------------------------------------------
    def add_rule(self, rule: QuestionRule) -> "QuestionReader":
        self.rules.append(rule)
        return self

    def normalize(self, sentence: str) -> Tuple[Tuple[str, ...], bool]:
        negated = False
        kept: List[str] = []
        for t in tokenize(sentence):
            if t in NEGATIONS:
                negated = True
                continue
            kept.append(t)
        return tuple(kept), negated

    def read(self, sentence: str) -> Tuple[Query, ...]:
        """All distinct query readings of ``sentence`` (empty = abstain)."""
        tokens, negated = self.normalize(sentence)
        out: List[Query] = []
        for rule in self.rules:
            query = self._match(rule, tokens, negated, sentence)
            if query is not None and not any(
                q.kind == query.kind and q.patterns == query.patterns and q.literal == query.literal
                for q in out
            ):
                out.append(query)
        return tuple(out)

    def query(self, sentence: str) -> Optional[Query]:
        """The unique reading, or ``None`` when zero/ambiguous (abstain)."""
        readings = self.read(sentence)
        if len(readings) == 1:
            return readings[0]
        return None

    # -- internals ---------------------------------------------------------
    def _is_pred(self, token: str) -> bool:
        return self.lexicon.is_pred(token)

    def _is_entity(self, token: str) -> bool:
        return (
            token not in WHO_WORDS
            and token not in self.copulas
            and token not in self.prepositions
            and token not in AUXILIARIES
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
        if cat == "aux":
            return token in AUXILIARIES
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

    def _slots(
        self, rule: QuestionRule, bindings: Dict[str, str], hole: Optional[Var]
    ) -> Optional[Tuple[Tuple[str, Term], ...]]:
        slots: List[Tuple[str, Term]] = []
        for role, ref in rule.roles:
            if ref == HOLE:
                if hole is None:
                    return None
                slots.append((role, hole))
            elif ref.startswith("?"):
                token = bindings.get(ref[1:])
                if token is None:
                    return None
                slots.append((role, Const(token)))
            else:
                slots.append((role, Const(ref)))
        return tuple(slots)

    def _candidate_preds(self, rule: QuestionRule, bindings: Dict[str, str]) -> List[str]:
        if rule.head is not None:
            head = self._resolve(rule.head, bindings)
            if head is None:
                return []
            return [self.lexicon.canonical(head)]
        required = frozenset(r for r, _ in rule.roles)
        if rule.answer_role is not None:
            required = required - {rule.answer_role}
        out: List[str] = []
        for pred in self.registry.known():
            schema = self.registry.get(pred)
            if schema is None or not required <= set(schema.roles):
                continue
            if rule.head_class == "prep" and pred not in self.prepositions:
                continue
            if rule.head_class == "unary" and set(schema.roles) != {SUBJECT}:
                continue
            out.append(pred)
        return sorted(out)

    def _match(
        self, rule: QuestionRule, tokens: Tuple[str, ...], negated: bool, raw: str
    ) -> Optional[Query]:
        if len(rule.pattern) != len(tokens):
            return None
        bindings: Dict[str, str] = {}
        for pattern, token in zip(rule.pattern, tokens):
            if not self._match_token(pattern, token, bindings):
                return None
        neg = rule.negated or negated

        if rule.kind == YESNO:
            head = self._resolve(rule.head, bindings) if rule.head else None
            if head is None:
                return None
            head = self.lexicon.canonical(head)
            slots = self._slots(rule, bindings, hole=None)
            if slots is None:
                return None
            literal = self.registry.normalize(Frame(head, slots, neg))
            if literal is None:
                return None
            return Query(YESNO, raw=raw, literal=literal, rule=rule.name)

        answer_var = None if rule.answer_pred else Var("x")
        atoms: List[object] = []
        for pred in self._candidate_preds(rule, bindings):
            slots = self._slots(rule, bindings, hole=answer_var)
            if slots is None:
                continue
            literal = self.registry.normalize(Frame(pred, slots, False))
            if literal is None:
                continue
            if literal.atom not in atoms:
                atoms.append(literal.atom)
        if not atoms:
            return None
        return Query(
            WH,
            raw=raw,
            patterns=tuple(atoms),
            answer_var=answer_var,
            answer_is_predicate=rule.answer_pred,
            focus=rule.focus,
            rule=rule.name,
        )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"QuestionReader(predicates={sorted(self.predicates)!r})"
