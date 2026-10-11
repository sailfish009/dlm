"""Module 24: query resolution -- question -> trusted answer, or abstain.

This is seam C for questions: the only place a question becomes an answer.  It
uses the kernel/closure and the negative side table, never a proposer's score.

    Query --(resolve, kernel closure only)--> Answer
      yes/no : asserted -> yes ; explicit negative -> no ; else UNKNOWN (abstain)
      wh     : match the answer hole against closure -> ground facts (a list)
               predicate answer -> the entailed predicate(s)
               no match -> abstain (open-world: absent is NOT false)

Two honesty rules fall out structurally:

* **Unknown is not no.**  A yes/no question is ``no`` only when an explicit
  negative is on record (Horn cannot derive a negative).  Otherwise it abstains.
* **A wh miss abstains.**  If nothing in the closure matches the pattern, the
  answer is "I could not find one", never a fabricated filler.

The answer is *ground* by construction (yes/no literal, or matched closure atoms),
so :func:`render_answer` can be round-trip checked by the egress firewall.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from .engine import closure
from .judge import ProofJudge, Verdict
from .kernel import Proof
from .logic import Atom, Literal, Var
from .query import WH, YESNO, Query
from .unify import apply_atom, unify, walk

__all__ = ["Answer", "resolve", "render_answer"]


@dataclass(frozen=True)
class Answer:
    """The outcome of resolving a :class:`Query` against a knowledge base.

    ``decision`` is one of ``"yes"`` / ``"no"`` / ``"unknown"`` / ``"list"`` /
    ``"predicate"``.  ``literal`` is the (ground) proposition for a yes/no answer;
    ``facts`` are the matched ground literals for a wh answer.
    """

    query: Query
    decision: str
    literal: Optional[Literal] = None
    proof: Optional[Proof] = None
    facts: Tuple[Literal, ...] = ()
    abstain: bool = True

    @property
    def decided(self) -> bool:
        return not self.abstain


def _resolve_yesno(query: Query, kb, judge: ProofJudge) -> Answer:
    literal = query.literal
    assert literal is not None  # guaranteed by Query.__post_init__
    if not literal.negated:
        judgement = judge.judge(kb, literal)
        if judgement.verdict is Verdict.ASSERTED:
            return Answer(query, "yes", literal=literal, proof=judgement.proof, abstain=False)
        if kb.is_negated(literal.atom):
            return Answer(query, "no", literal=Literal(literal.atom, True), abstain=False)
        return Answer(query, "unknown", literal=literal, abstain=True)
    # the query itself is negative ("is alice not happy?")
    if kb.is_negated(literal.atom):
        return Answer(query, "yes", literal=literal, abstain=False)
    positive = judge.judge(kb, Literal(literal.atom, negated=False))
    if positive.verdict is Verdict.ASSERTED:
        return Answer(query, "no", literal=literal, abstain=False)
    return Answer(query, "unknown", literal=literal, abstain=True)


def _resolve_wh(query: Query, kb) -> Answer:
    atoms = closure(kb)
    facts: list[Literal] = []
    predicates: set[str] = set()
    for pattern in query.patterns:
        if query.answer_var is None:
            # predicate answer: the whole (ground) pattern must be entailed
            if pattern.is_ground() and pattern in atoms:
                predicates.add(pattern.pred)
                lit = Literal(pattern, negated=False)
                if lit not in facts:
                    facts.append(lit)
            continue
        variable = query.answer_var
        for atom in atoms:
            substitution = unify(pattern, atom)
            if substitution is None:
                continue
            if isinstance(walk(variable, substitution), Var):
                continue
            ground = apply_atom(pattern, substitution)
            if not ground.is_ground():
                continue
            lit = Literal(ground, negated=False)
            if lit not in facts:
                facts.append(lit)

    facts.sort(key=str)
    if not facts:
        return Answer(query, "unknown", abstain=True)
    decision = "predicate" if query.answer_is_predicate else "list"
    return Answer(query, decision, facts=tuple(facts), abstain=False)


def resolve(query: Query, kb, *, judge: Optional[ProofJudge] = None) -> Answer:
    """Resolve ``query`` against ``kb`` using only trusted signal (proof/closure).

    ``judge`` is the trusted decision maker (default :class:`ProofJudge`).  It may
    be swapped, but only for another trusted judge -- never a proposer.
    """
    judge = judge if judge is not None else ProofJudge()
    if query.kind == YESNO:
        return _resolve_yesno(query, kb, judge)
    if query.kind == WH:
        return _resolve_wh(query, kb)
    raise ValueError(f"unknown query kind {query.kind!r}")


def render_answer(answer: Answer, template) -> Optional[str]:
    """Render a resolved answer to one sentence via the template realizer.

    Returns ``None`` when the answer has nothing ground to say (abstain with no
    literal).  The caller (a :class:`CheckedRealizer`) is responsible for the
    round-trip check; this function only proposes text.
    """
    query = answer.query
    if query.kind == YESNO:
        literal = answer.literal
        text = template.render(literal) if literal is not None else None
        if text is None:
            return None
        if answer.decision == "yes":
            return f"Yes, {text}."
        if answer.decision == "no":
            return f"No, {text}."
        return f"I cannot decide whether {text}."
    if not answer.facts:
        return None
    phrases = []
    for fact in answer.facts:
        rendered = template.render(fact)
        if rendered:
            phrases.append(rendered)
    if not phrases:
        return None
    if len(phrases) == 1:
        return phrases[0] + "."
    return "; ".join(phrases) + "."