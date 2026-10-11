"""Module 22: the question IR -- what a question *is*, before any answer.

The gap this module closes (NOTE.md Part II / the "structure not settled" note):
the model had ``Literal`` (a proposition) but no first-class notion of a
*question*.  ``nl_talk.py`` faked it with ``sentence.endswith("?")`` and then
judged a ground literal.  A question is structurally different:

* a **yes/no** question supplies a whole ground proposition and asks whether the
  kernel can decide it (asserted / refuted / unknown);
* a **wh** question supplies a *pattern* with a hole and asks for the fillers the
  closure entails -- and the hole may be a **term** (``where is alice?`` ->
  the place) or the **predicate itself** (``what is alice?`` -> happy/tall).

Both are function-free Horn.  A wh question is therefore a *finite disjunction of
candidate goal atoms* (enumerated from the schema/lexicon, i.e. data) plus one
designated answer slot.  No predicate variables enter the kernel: the
enumeration is a proposer's job, the entailment is the kernel's.

Trust position: :class:`Query` is a *proposal* structure.  It is produced by the
untrusted :mod:`dlm.question` reader; :mod:`dlm.answer` resolves it using only
proof/closure and the side table.  A query never asserts anything.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .logic import Atom, Literal, Var

__all__ = ["YESNO", "WH", "Query", "answer_atoms"]

#: A yes/no question: judge ``literal``.
YESNO = "yesno"
#: A wh question: find fillers among ``patterns``.
WH = "wh"


@dataclass(frozen=True)
class Query:
    """A question in normal form.

    ``literal``      -- yes/no only: the ground proposition to judge.
    ``patterns``     -- wh only: candidate goal atoms (each open in ``answer_var``,
                        or ground when the answer is the predicate).
    ``answer_var``   -- wh term answer: the variable to bind.
    ``answer_is_predicate`` -- wh predicate answer: report the predicate(s) that hold.
    ``focus``        -- the surface wh-word (``who``/``what``/``where``/...), for realisation.
    ``rule``         -- the interrogative rule that produced it (a derivation id).
    """

    kind: str
    raw: Optional[str] = None
    literal: Optional[Literal] = None
    patterns: Tuple[Atom, ...] = ()
    answer_var: Optional[Var] = None
    answer_is_predicate: bool = False
    focus: Optional[str] = None
    rule: Optional[str] = None

    def __post_init__(self) -> None:
        if self.kind not in (YESNO, WH):
            raise ValueError(f"unknown query kind {self.kind!r}")
        if self.kind == YESNO:
            if self.literal is None:
                raise ValueError("a yes/no query needs a literal")
        else:
            if not self.patterns:
                raise ValueError("a wh query needs at least one candidate pattern")
            if self.answer_var is None and not self.answer_is_predicate:
                raise ValueError("a wh query needs an answer variable or predicate flag")

    def is_yesno(self) -> bool:
        return self.kind == YESNO

    def is_wh(self) -> bool:
        return self.kind == WH

    def __str__(self) -> str:
        if self.kind == YESNO:
            return f"(? {self.literal})"
        if self.answer_is_predicate:
            body = " | ".join(str(p) for p in self.patterns)
            return f"(?pred {body})"
        return f"(?{self.answer_var} {self.patterns[0]})"


def answer_atoms(query: Query) -> Tuple[Atom, ...]:
    """The candidate goal atoms a wh query ranges over (empty for yes/no)."""
    if query.kind != WH:
        return ()
    return query.patterns