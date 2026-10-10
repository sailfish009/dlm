"""Module 3: sentence -> Frame (the conversion, seam B).

The reader is the untrusted proposer at seam B (NOTE.md Part III §13): it reads
a small, closed subset of English into role-labelled :class:`Frame` proposals.
It does **not** decide truth and it does **not** invent predicates or roles --
that is :meth:`SchemaRegistry.normalize`, the trust boundary. Anything the
closed subset cannot consume is dropped: **abstain, never guess**.

Pipeline position::

    sentence --(this module, seam B)--> Frame(s) --(normalize)--> Literal

Closed subset (deterministic, role-labelled, full-match only):

    E V             -> V(agent=E)                         intransitive
    E V E           -> V(agent=E, patient=E)              transitive SVO
    E COP P E       -> P(figure=E, ground=E)              copula + preposition
    E COP V         -> V(subject=E)                       copula + noun

where ``E`` is an entity token, ``V`` a known predicate word, ``P`` a known
preposition, ``COP`` a copula. Determiners and punctuation are dropped;
auxiliaries are dropped; a negation word sets ``negated`` on every frame.

Two deliberate design points, straight from NOTE.md §9:

* **Ambiguity is preserved, not resolved.** ``read`` returns *all* distinct
  readings (a tuple). An empty tuple means abstain. Collapsing N readings to one
  would be guessing; the normalizer/kernel dispose of what the reader proposes.
* **No predicate guessing.** ``V`` is only a predicate if it is in the reader's
  lexicon. An unknown word makes the whole sentence unreadable (abstain).

This module is stdlib-only and never evaluates text.
"""
from __future__ import annotations

import re
from typing import FrozenSet, Iterable, Protocol, Tuple, runtime_checkable

from .logic import Const, Frame

__all__ = [
    "AGENT",
    "PATIENT",
    "FIGURE",
    "GROUND",
    "SUBJECT",
    "COPULAS",
    "AUXILIARIES",
    "NEGATIONS",
    "DEFAULT_PREPOSITIONS",
    "Reader",
    "LexicalReader",
    "tokenize",
]


# -- role vocabulary -------------------------------------------------------
# The role names the closed subset can emit. The predicate's *schema* decides
# the argument order, so a role is meaning, not position.
AGENT = "agent"
PATIENT = "patient"
FIGURE = "figure"  # the located thing in a prepositional relation
GROUND = "ground"  # what it is located against
SUBJECT = "subject"  # single argument of a copular predication

# -- closed word classes ---------------------------------------------------
COPULAS: FrozenSet[str] = frozenset({"is", "are", "was", "were", "am", "be", "been", "being"})
AUXILIARIES: FrozenSet[str] = frozenset({"do", "does", "did"})
NEGATIONS: FrozenSet[str] = frozenset({"not", "never"})
DEFAULT_PREPOSITIONS: FrozenSet[str] = frozenset(
    {"on", "in", "at", "to", "from", "with", "under", "over", "near", "of", "by", "into", "onto"}
)

_DETERMINERS = re.compile(r"\b(?:a|an|the)\b")
_PUNCT = re.compile(r"[.,!?;:]+")


def tokenize(sentence: str) -> Tuple[str, ...]:
    """Lowercase, expand ``n't``, drop possessives/determiners/punctuation.

    The closed subset works token-by-token, so constants are lowercase single
    tokens (e.g. ``Alice`` and ``alice`` denote one individual). Multi-word
    entities are outside the fragment and therefore abstain.
    """
    s = sentence.strip().lower().replace("n't", " not ").replace("'s", " ")
    s = _PUNCT.sub(" ", s)
    s = _DETERMINERS.sub(" ", s)
    return tuple(s.split())


@runtime_checkable
class Reader(Protocol):
    """Seam B. A learned reader (CLM action head / seq2seq) may replace this.

    The contract: given a sentence, return the tuple of role-labelled frame
    proposals it can read. ``()`` means abstain. A reader is a proposer -- it is
    untrusted; only the kernel asserts.
    """

    def read(self, sentence: str) -> Tuple[Frame, ...]:  # pragma: no cover - protocol
        ...


class LexicalReader:
    """The deterministic closed-subset reader (the default :class:`Reader`).

    ``predicates`` is the predicate lexicon: a word can head a verb frame only
    if it is listed. ``prepositions`` governs the copula+preposition frame.
    """

    def __init__(
        self,
        predicates: Iterable[str] = (),
        prepositions: Iterable[str] = DEFAULT_PREPOSITIONS,
    ) -> None:
        self.predicates: FrozenSet[str] = frozenset(predicates)
        self.prepositions: FrozenSet[str] = frozenset(prepositions)

    # -- public ------------------------------------------------------------
    def read(self, sentence: str) -> Tuple[Frame, ...]:
        tokens = tokenize(sentence)
        negated = False
        kept = []
        for t in tokens:
            if t in NEGATIONS:
                negated = True
                continue
            if t in AUXILIARIES:
                continue
            kept.append(t)
        tokens = tuple(kept)

        frames = list(self._match(tokens))
        if negated:
            frames = [Frame(f.pred, f.slots, True) for f in frames]

        # preserve readings but drop duplicates, in order
        unique: list[Frame] = []
        for f in frames:
            if f not in unique:
                unique.append(f)
        return tuple(unique)

    # -- internals ---------------------------------------------------------
    def _is_entity(self, token: str) -> bool:
        return (
            token not in COPULAS
            and token not in self.prepositions
            and token not in self.predicates
        )

    def _match(self, tokens: Tuple[str, ...]) -> Iterable[Frame]:
        n = len(tokens)
        if n == 2:
            # E V  -> V(agent=E)
            if self._is_entity(tokens[0]) and tokens[1] in self.predicates:
                yield Frame(tokens[1], ((AGENT, Const(tokens[0])),))
        elif n == 3:
            # E V E  -> V(agent=E, patient=E)
            if (
                self._is_entity(tokens[0])
                and tokens[1] in self.predicates
                and self._is_entity(tokens[2])
            ):
                yield Frame(
                    tokens[1],
                    ((AGENT, Const(tokens[0])), (PATIENT, Const(tokens[2]))),
                )
            # E COP V -> V(subject=E)
            if (
                self._is_entity(tokens[0])
                and tokens[1] in COPULAS
                and tokens[2] in self.predicates
            ):
                yield Frame(tokens[2], ((SUBJECT, Const(tokens[0])),))
        elif n == 4:
            # E COP P E -> P(figure=E, ground=E)
            if (
                self._is_entity(tokens[0])
                and tokens[1] in COPULAS
                and tokens[2] in self.prepositions
                and self._is_entity(tokens[3])
            ):
                yield Frame(
                    tokens[2],
                    ((FIGURE, Const(tokens[0])), (GROUND, Const(tokens[3]))),
                )

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"LexicalReader(predicates={sorted(self.predicates)!r})"