"""Module 9: the System-One wire boundary (``state + questions -> answers``).

The CLM / strands-decider / TypeSafe services all speak the same JSON shape
(``{state, questions: {id: Question}} -> {model, answers: {id: Answer}, usage}``)
with three question types -- ``noul`` (a truth), ``choice`` (pick an option) and
``score`` (a graded level).  This module puts DLM behind that *same* interface so
the services are interchangeable: anything with ``answer(request) -> response``
satisfies :class:`WireService`.

Two standing rules from the design (NOTE.md):

* **NL lives only at this boundary.**  ``state`` is grounded to facts (seam A)
  and every question's ``instructions`` / ``criteria`` are converted to a
  ``Literal`` (seam B) the moment they arrive.  Downstream sees logic only.
* **Egress is template-only.**  A DLM answer is assembled by *rendering* a
  proof-backed verdict; it never generates prose.  Where TypeSafe has no place
  to say "I cannot", DLM adds explicit honesty fields (``abstain``, ``literal``,
  ``proof``, ``verdict``).  A consumer must check ``abstain`` before trusting
  the value -- so DLM never guesses to fill a slot.

DLM extension beyond the CLM wire: an optional ``theory`` list of S-expr strings
(rules / facts / explicit negatives) that a request may carry.  That is what
makes deduction possible; ``state`` supplies the situation, ``theory`` the laws.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Protocol, Tuple, runtime_checkable

from .convert import Ingestor
from .judge import Adjudicator, Judge, Judgement, Policy, ProofJudge, Verdict
from .kb import KnowledgeBase
from .logic import Atom, Literal, Rule
from .sexp import SexpError

__all__ = [
    "QUESTION_TYPES",
    "NOUL_KEYS",
    "WireError",
    "render_noul",
    "render_choice",
    "render_score",
    "WireService",
    "DlmService",
    "systemone",
]

QUESTION_TYPES = ("noul", "choice", "score")
NOUL_KEYS = ("false", "true")
MODEL = "dlm-v0.0007"


class WireError(ValueError):
    """A malformed request.  Distinct from an abstain (a well-formed miss)."""


# -- egress: template-only rendering of a trusted verdict ------------------
def _confidence(probabilities: Mapping[str, float]) -> float:
    """TypeSafe-style confidence: top probability minus the mean of the rest."""
    values = list(probabilities.values())
    if len(values) < 2:
        return 1.0
    j = max(range(len(values)), key=values.__getitem__)
    rest = [v for i, v in enumerate(values) if i != j]
    return max(0.0, min(1.0, values[j] - sum(rest) / len(rest)))


def render_noul(
    literal: Optional[Literal],
    value: Optional[bool],
    judgement: Optional[Judgement] = None,
    *,
    reason: Optional[str] = None,
) -> dict:
    """Answer a ``noul`` question, or abstain when the truth is not on record."""
    verdict = judgement.verdict.value if judgement is not None else Verdict.ABSTAIN.value
    proof = str(judgement.proof) if judgement is not None and judgement.proof else None
    out: dict = {
        "type": "noul",
        "noul": None if value is None else (1.0 if value else 0.0),
        "abstain": value is None,
        "verdict": verdict,
        "literal": str(literal) if literal is not None else None,
        "proof": proof,
    }
    if reason:
        out["reason"] = reason
    return out


def render_choice(
    chosen: Optional[str],
    probabilities: Mapping[str, float],
    verdicts: Mapping[str, str],
    literals: Mapping[str, Optional[str]],
    *,
    reason: Optional[str] = None,
) -> dict:
    """Answer a ``choice`` question from per-option verdicts (never by guessing)."""
    out: dict = {
        "type": "choice",
        "choice": chosen,
        "abstain": chosen is None,
        "probabilities": dict(probabilities),
        "verdicts": dict(verdicts),
        "literals": dict(literals),
    }
    if chosen is not None:
        out["confidence"] = _confidence(probabilities)
    if reason:
        out["reason"] = reason
    return out


def render_score(*, reason: Optional[str] = None) -> dict:
    """A ``score`` question is outside the function-free Horn fragment -> abstain."""
    return {
        "type": "score",
        "score": None,
        "abstain": True,
        "reason": reason
        or "score questions are outside the function-free Horn fragment",
    }


# -- the service interface (interchangeable with CLM / strands / TypeSafe) --
@runtime_checkable
class WireService(Protocol):
    def answer(self, request: Mapping[str, Any]) -> dict:
        ...


def _validate(
    request: Mapping[str, Any],
) -> Tuple[Any, Mapping[str, Any], Tuple[Any, ...]]:
    if not isinstance(request, Mapping):
        raise WireError("request must be a JSON object")
    if "state" not in request:
        raise WireError("request must have 'state'")
    questions = request.get("questions")
    if not isinstance(questions, Mapping) or not questions:
        raise WireError("request must have a non-empty 'questions' object")
    for qid, q in questions.items():
        if not isinstance(q, Mapping) or q.get("type") not in QUESTION_TYPES:
            raise WireError(f"question {qid!r} must have type in {QUESTION_TYPES}")
    theory = request.get("theory") or ()
    if not isinstance(theory, (list, tuple)):
        raise WireError("'theory' must be a list of S-expr strings or forms")
    return request["state"], questions, tuple(theory)


def _add_logic(kb: KnowledgeBase, logic: Any) -> None:
    if isinstance(logic, Rule):
        kb.add_rule(logic)
    elif isinstance(logic, Literal):
        if logic.negated:
            kb.add_negation(logic.atom)
        else:
            kb.add_fact(logic.atom)
    elif isinstance(logic, Atom):
        kb.add_fact(logic)
    else:  # pragma: no cover - form_to_logic only emits the three above
        raise TypeError(f"unsupported logic object {logic!r}")


class DlmService:
    """DLM as a System-One service: ingress (A/B) -> judge (D) -> template egress.

    ``kb`` is the fixed base theory (laws).  Each request runs against a copy,
    augmented by the request's ``theory`` forms and the grounded ``state``.
    """

    def __init__(
        self,
        ingestor: Ingestor,
        kb: Optional[KnowledgeBase] = None,
        *,
        judge: Optional[Judge] = None,
        policy: Policy = Policy.GATE,
        model: str = MODEL,
    ) -> None:
        self.ingestor = ingestor
        self.kb = kb if kb is not None else KnowledgeBase()
        self.adjudicator = Adjudicator(judge=judge or ProofJudge(), policy=policy)
        self.model = model

    # -- request-local KB --------------------------------------------------
    def _build_kb(self, state: Any, theory: Tuple[Any, ...]) -> KnowledgeBase:
        kb = self.kb.copy()
        for item in theory:
            try:
                logic = self.ingestor.logic(item) if isinstance(item, str) else self.ingestor.form(item)
            except SexpError as exc:
                raise WireError(f"theory entry is not valid S-expr: {exc}") from exc
            except (TypeError, ValueError) as exc:
                raise WireError(f"theory entry is not function-free Horn: {exc}") from exc
            if logic is None:
                raise WireError("theory entry must be exactly one S-expr form")
            try:
                _add_logic(kb, logic)
            except (TypeError, ValueError) as exc:
                raise WireError(f"theory entry is not a ground fact / rule: {exc}") from exc
        for atom in self.ingestor.facts(state):
            kb.add_fact(atom)
        return kb

    # -- ingress helper ----------------------------------------------------
    def _text_literal(self, text: Any) -> Optional[Literal]:
        if not isinstance(text, str) or not text.strip():
            return None
        return self.ingestor.literal(text)

    def _truth(self, kb: KnowledgeBase, literal: Literal) -> Tuple[Optional[bool], Judgement]:
        """The truth value of a ground literal as a proposition, or ``None``.

        True iff the literal itself is established; False iff its **opposite** is
        on record (proof for a positive, the side table for a negative).  Uses
        only the trusted judge; never guesses from absence.
        """
        judge = self.adjudicator.judge
        j = judge.judge(kb, literal)
        if literal.negated:
            if j.verdict is Verdict.REFUTED:
                return True, j
            opposite = judge.judge(kb, Literal(literal.atom, negated=False))
            if opposite.verdict is Verdict.ASSERTED:
                return False, opposite
            return None, j
        if j.verdict is Verdict.ASSERTED:
            return True, j
        opposite = judge.judge(kb, Literal(literal.atom, negated=True))
        if opposite.verdict is Verdict.REFUTED:
            return False, opposite
        return None, j

    # -- question handlers -------------------------------------------------
    def _noul(self, kb: KnowledgeBase, question: Mapping[str, Any]) -> dict:
        literal = self._text_literal(question.get("instructions"))
        if literal is None:
            return render_noul(None, None, reason="statement not normalizable")
        value, judgement = self._truth(kb, literal)
        if value is None:
            return render_noul(literal, None, judgement, reason="not on record")
        return render_noul(literal, value, judgement)

    def _choice(self, kb: KnowledgeBase, question: Mapping[str, Any]) -> dict:
        criteria = question.get("criteria")
        if not isinstance(criteria, Mapping) or not criteria:
            raise WireError("choice question needs a non-empty 'criteria' object")
        keys = list(criteria)
        literals: Dict[Any, Optional[str]] = {}
        verdicts: Dict[Any, str] = {}
        values: Dict[Any, Optional[bool]] = {}
        for key in keys:
            raw = criteria[key]
            text: Any = raw if isinstance(raw, str) and raw.strip() else key
            literal = self._text_literal(text)
            literals[key] = str(literal) if literal is not None else None
            if literal is None:
                values[key] = None
                verdicts[key] = Verdict.ABSTAIN.value
                continue
            value, judgement = self._truth(kb, literal)
            values[key] = value
            verdicts[key] = judgement.verdict.value
        true_keys = [k for k in keys if values[k] is True]
        zeros = {k: 0.0 for k in keys}
        if len(true_keys) == 1:
            chosen = true_keys[0]
            probabilities = {k: (1.0 if k == chosen else 0.0) for k in keys}
            return render_choice(chosen, probabilities, verdicts, literals)
        if not true_keys:
            return render_choice(None, zeros, verdicts, literals, reason="no option is provable")
        return render_choice(
            None, zeros, verdicts, literals, reason="ambiguous: multiple options provable"
        )

    def _answer_question(self, kb: KnowledgeBase, question: Mapping[str, Any]) -> dict:
        qtype = question["type"]
        if qtype == "noul":
            return self._noul(kb, question)
        if qtype == "choice":
            return self._choice(kb, question)
        return render_score()

    # -- the wire entry point ---------------------------------------------
    def answer(self, request: Mapping[str, Any]) -> dict:
        state, questions, theory = _validate(request)
        kb = self._build_kb(state, theory)
        answers = {qid: self._answer_question(kb, q) for qid, q in questions.items()}
        asserted = sum(1 for a in answers.values() if not a.get("abstain", True))
        return {
            "model": self.model,
            "answers": answers,
            "usage": {
                "billing_units": len(answers),
                "questions": len(answers),
                "asserted": asserted,
                "abstained": len(answers) - asserted,
            },
        }


def systemone(service: WireService, request: Mapping[str, Any]) -> dict:
    """Run one System-One request against any wire service (CLM / strands / DLM)."""
    return service.answer(request)