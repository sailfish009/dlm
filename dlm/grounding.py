"""Natural-language grounding: sentence -> predicate atom.

This is the front-end the DLM needs to be communicable, and the SAME bottleneck
as web-text extraction: both must map language to atoms. The model is not in
this file; a Grounder only proposes atoms, and ABSTAINS when it cannot.

GrammarGrounder is the deterministic T1 grounding: a closed vocabulary of
phrase patterns. It is reliable but narrow, and it never guesses.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Protocol, Sequence, Tuple

from .interpreter import ParseError, parse_atom
from .terms import Atom

__all__ = [
    "Grounding",
    "Grounder",
    "Pattern",
    "GrammarGrounder",
    "ChainGrounder",
]


@dataclass(frozen=True)
class Grounding:
    """Result of grounding one sentence. `ok=False` means: abstain."""

    ok: bool
    atom: Optional[Atom] = None
    negated: bool = False
    kind: str = "query"  # "query" (ask) or "assert" (tell)
    source: str = "grammar"
    confidence: float = 1.0
    reason: str = ""
    raw: str = ""

    def __bool__(self) -> bool:  # convenience: `if grounding:`
        return self.ok

    def __str__(self) -> str:
        if not self.ok:
            return f"<abstain: {self.reason or 'no pattern'}>"
        sign = "not " if self.negated else ""
        return f"{self.kind}: {sign}{self.atom}"


class Grounder(Protocol):
    def ground(self, sentence: str) -> Grounding:  # pragma: no cover - protocol
        ...


@dataclass(frozen=True)
class Pattern:
    """A phrase pattern and the atom template it builds.

    phrase:   "is {x} a grandparent of {y}"   (placeholders are word tokens)
    template: "grandparent({x},{y})"
    kind:     "query" or "assert"
    """

    phrase: str
    template: str
    kind: str = "query"
    name: str = ""


_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def _normalize(sentence: str) -> str:
    s = sentence.strip().lower()
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("?", " ").replace(".", " ").replace("!", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^(please|could you tell me|tell me)\s+", "", s)
    return s


def _compile(phrase: str) -> "re.Pattern[str]":
    """Turn a phrase template into an anchored regex with named groups."""
    parts: List[str] = []
    pos = 0
    for m in _PLACEHOLDER.finditer(phrase):
        literal = phrase[pos:m.start()]
        if literal:
            parts.append(re.escape(literal.strip()).replace(r"\ ", r"\s+"))
        parts.append(f"(?P<{m.group(1)}>[a-z0-9_]+)")
        pos = m.end()
    tail = phrase[pos:]
    if tail:
        parts.append(re.escape(tail.strip()).replace(r"\ ", r"\s+"))
    body = r"\s+".join(p for p in parts if p)
    return re.compile(rf"^{body}$")


class GrammarGrounder:
    """Deterministic NL -> atom grounding over a closed pattern vocabulary."""

    def __init__(
        self,
        patterns: Sequence[Pattern],
        *,
        allow_negation: bool = True,
        normalize: bool = True,
    ) -> None:
        self.patterns: List[Pattern] = list(patterns)
        self.allow_negation = allow_negation
        self.normalize = normalize
        self._compiled: List[Tuple[Pattern, "re.Pattern[str]"]] = [
            (p, _compile(p.phrase)) for p in self.patterns
        ]

    def add(self, pattern: Pattern) -> "GrammarGrounder":
        self.patterns.append(pattern)
        self._compiled.append((pattern, _compile(pattern.phrase)))
        return self

    def ground(self, sentence: str) -> Grounding:
        raw = sentence
        s = _normalize(sentence) if self.normalize else sentence.strip()
        if not s:
            return Grounding(False, reason="empty input", raw=raw)

        negated = False
        s_used = s
        if self.allow_negation:
            # "not" may appear before the head noun; strip one occurrence.
            if " not " in f" {s} ":
                s_used = re.sub(r"\bnot\b\s*", "", s, count=1)
                s_used = re.sub(r"\s+", " ", s_used).strip()
                negated = True

        for pattern, rx in self._compiled:
            m = rx.match(s_used)
            if not m:
                continue
            try:
                atom = parse_atom(pattern.template.format(**m.groupdict()))
            except (ParseError, KeyError) as exc:
                return Grounding(False, reason=f"bad template: {exc}", raw=raw)
            return Grounding(
                ok=True,
                atom=atom,
                negated=negated,
                kind=pattern.kind,
                source=f"grammar:{pattern.name or pattern.phrase}",
                confidence=1.0,
                raw=raw,
            )

        return Grounding(False, reason="no pattern matched", raw=raw)


class ChainGrounder:
    """Try grounders in order; return the first that produces an atom.

    This is where an encoder (T2) or a constrained LLM parser (T3) plugs in
    *behind the same protocol*, without changing the decision path.
    """

    def __init__(self, grounders: Iterable[Grounder]) -> None:
        self.grounders = list(grounders)

    def ground(self, sentence: str) -> Grounding:
        last: Optional[Grounding] = None
        for g in self.grounders:
            try:
                out = g.ground(sentence)
            except Exception as exc:  # a plug-in must never crash the loop
                out = Grounding(False, reason=f"{type(g).__name__}: {exc}", raw=sentence)
            if out.ok:
                return out
            last = out
        return last or Grounding(False, reason="no grounder produced an atom", raw=sentence)