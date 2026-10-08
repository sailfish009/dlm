"""Option interpretation: surface text -> a logical atom, or an honest abstention.

The decision engine can only prove something about a question once the option is
turned into an :class:`~dlm.terms.Atom`. v0.0002 ships a deterministic
``SchemaInterpreter`` that reads a logical string (``edge(alice, bob)``,
``not edge(alice, bob)``). Perception grounding (image/patch features from
Franca / pyssl -> predicates) plugs in behind the same ``Interpreter`` protocol;
it is deliberately *not* implemented here, so no image is silently ignored.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Protocol, Sequence

from .terms import Atom, Const, Term

_NEG_PREFIX = re.compile(r"^\s*(?:not|!|~|¬)\s+", re.IGNORECASE)
_ATOM_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(\s*(.*?)\s*\))?\s*\.?$", re.DOTALL)


class ParseError(ValueError):
    """Raised when an option string is not a well-formed logical atom."""


@dataclass(frozen=True)
class ParsedOption:
    """An interpreted option. ``ok=False`` means abstain (never guess)."""

    atom: Atom | None
    negated: bool = False
    ok: bool = True
    reason: str = ""


def _parse_term(text: str) -> Term:
    text = text.strip()
    if not text:
        raise ParseError("empty argument")
    if text.startswith("?"):
        if len(text) == 1:
            raise ParseError("bare '?'")
        name = text[1:]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ParseError(f"bad variable {text!r}")
        from .terms import Var

        return Var(name)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return Const(text[1:-1])
    if not re.fullmatch(r"[A-Za-z0-9_./+-]+", text):
        raise ParseError(f"bad constant {text!r}")
    return Const(text)


def _split_args(body: str) -> list[str]:
    """Split on top-level commas. No function symbols, so no nested parens."""
    if body == "":
        return []
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                raise ParseError("unbalanced parenthesis")
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if depth != 0:
        raise ParseError("unbalanced parenthesis")
    parts.append("".join(cur))
    out = [p.strip() for p in parts]
    if any(p == "" for p in out):
        raise ParseError("empty argument")
    return out


def parse_atom(text: str) -> Atom:
    """Parse ``pred`` or ``pred(a, b)`` into an atom. Raises :class:`ParseError`."""
    m = _ATOM_RE.match(text.strip())
    if not m:
        raise ParseError(f"not an atom: {text!r}")
    pred, body = m.group(1), m.group(2)
    args = tuple(_parse_term(a) for a in _split_args(body)) if body is not None else ()
    return Atom(pred, args)


class Interpreter(Protocol):
    """Turn ``(state, option)`` into a :class:`ParsedOption`."""

    def interpret(self, state: Any, option: str) -> ParsedOption: ...


class SchemaInterpreter:
    """Read options as logical strings; abstain on anything that does not parse."""

    name = "schema"

    def interpret(self, state: Any, option: str) -> ParsedOption:
        text = option.strip()
        negated = False
        m = _NEG_PREFIX.match(text)
        if m:
            negated = True
            text = text[m.end():]
        try:
            return ParsedOption(atom=parse_atom(text), negated=negated, ok=True)
        except ParseError as e:
            return ParsedOption(atom=None, negated=negated, ok=False, reason=str(e))


class GroundingInterpreter:
    """Adapt an external grounding function (perception -> predicates).

    ``ground(state, option)`` returns a :class:`ParsedOption` (or ``None`` to
    abstain). Use for Franca / pyssl image features mapped to atoms; the
    decision path stays identical.
    """

    name = "grounding"

    def __init__(self, ground: Callable[[Any, str], ParsedOption | None]):
        self._ground = ground

    def interpret(self, state: Any, option: str) -> ParsedOption:
        got = self._ground(state, option)
        if got is None:
            return ParsedOption(atom=None, ok=False, reason="grounding produced no atom")
        return got


class ChainInterpreter:
    """First interpreter that succeeds wins; otherwise the last failure reason."""

    def __init__(self, *interpreters: Interpreter):
        if not interpreters:
            raise ValueError("ChainInterpreter needs at least one interpreter")
        self.interpreters: Sequence[Interpreter] = interpreters

    def interpret(self, state: Any, option: str) -> ParsedOption:
        last = ParsedOption(atom=None, ok=False, reason="no interpreter")
        for interp in self.interpreters:
            last = interp.interpret(state, option)
            if last.ok:
                return last
        return last