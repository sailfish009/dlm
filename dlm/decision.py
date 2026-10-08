"""The System-One decision engine: proof-based answers to noul / choice / score.

Three primitives, one mechanism. Every option is interpreted to an atom, the KB
is queried, and the option gets a derivability score. A softmax over scores (at a
temperature) gives the distribution; the confidence formulas in ``schema`` are
unchanged from the reference decision models.

Two honest choices, both deliberate:

* **Closed-world negation.** A refuted claim scores 0 because Horn reasoning
  cannot prove a negative; the engine treats "not derivable" as false. This is an
  assumption, stated here and in ``RESULTS.md``, not a theorem.
* **Abstain, never guess.** If any option cannot be interpreted to an atom, the
  question is answered uniformly with ``abstained=True`` rather than compared on
  unequal footing. A learned calibrator may re-tie probabilities later; it may
  not invent an atom.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional

from .deduce import Engine
from .interpreter import Interpreter, ParsedOption, SchemaInterpreter
from .kb import KnowledgeBase
from .schema import (
    Answer,
    ChoiceAnswer,
    ChoiceQuestion,
    NoulAnswer,
    NoulQuestion,
    ScoreAnswer,
    ScoreQuestion,
    SystemOneRequest,
    SystemOneResponse,
    Usage,
    derive_confidence,
    derive_score_confidence,
)
from .terms import Atom

_DEFAULT_TEMPERATURE = 0.25


@dataclass
class OptionScore:
    """The discrete evidence the engine has about one option."""

    option: str
    parsed: ParsedOption
    derivable: bool
    n_proofs: int = 0
    min_depth: int = 0
    n_answers: int = 0

    @property
    def interpretable(self) -> bool:
        return self.parsed.ok and self.parsed.atom is not None


def as_text(content: Any) -> str:
    """Render a wire ``Content`` (str / dict / list) to a single option string."""
    if isinstance(content, str):
        return content
    if isinstance(content, (list, tuple)):
        return " ".join(as_text(x) for x in content)
    if isinstance(content, dict):
        return " ".join(f"{k}={as_text(v)}" for k, v in content.items())
    return str(content)


def softmax(logits: list[float], temperature: float = _DEFAULT_TEMPERATURE) -> list[float]:
    """Numerically stable softmax; uniform when all logits are equal or t<=0."""
    if not logits:
        return []
    t = temperature if temperature > 0 else 1.0
    m = max(logits)
    exps = [math.exp((x - m) / t) for x in logits]
    total = sum(exps)
    return [e / total for e in exps] if total > 0 else [1.0 / len(logits)] * len(logits)


class DecisionEngine:
    """Decide wire questions by deduction over a knowledge base."""

    def __init__(
        self,
        kb: KnowledgeBase,
        interpreter: Optional[Interpreter] = None,
        *,
        temperature: float = _DEFAULT_TEMPERATURE,
        smooth: float = 0.0,
        max_depth: int = 64,
        level_pred: str = "level",
    ) -> None:
        self.kb = kb
        self.interpreter: Interpreter = interpreter or SchemaInterpreter()
        self.temperature = temperature
        self.smooth = smooth              # floor/ceiling so exact answers are not 0/1 degenerate
        self.max_depth = max_depth
        self.level_pred = level_pred
        self._engines: dict[int, Engine] = {}

    # -- evidence ---------------------------------------------------------
    def _engine(self) -> Engine:
        key = id(self.kb)
        eng = self._engines.get(key)
        if eng is None:
            eng = Engine(self.kb, max_depth=self.max_depth)
            self._engines[key] = eng
        return eng

    def _solutions(self, atom: Atom):
        return list(self._engine().prove(atom))

    def score_option(self, state: Any, option: str) -> OptionScore:
        """Interpret one option and collect its proof evidence."""
        parsed = self.interpreter.interpret(state, option)
        if not parsed.ok or parsed.atom is None:
            return OptionScore(option=option, parsed=parsed, derivable=False)
        sols = self._solutions(parsed.atom)
        derivable = bool(sols)
        if parsed.negated:  # closed-world negation: "not X" holds iff X is not derivable
            derivable = not derivable
        depths = [s.proof.depth() for s in sols] if sols else []
        return OptionScore(
            option=option,
            parsed=parsed,
            derivable=derivable,
            n_proofs=len(sols),
            min_depth=min(depths) if depths else 0,
            n_answers=len(sols),
        )

    def _logit(self, sc: OptionScore) -> float:
        """Exact evidence first; the small head may refine this later (Tier 1)."""
        return 1.0 if sc.derivable else 0.0

    def _exact_probability(self, sc: OptionScore) -> float:
        """Map a derivability score to a probability with an optional smooth floor/ceiling."""
        return (1.0 - self.smooth) if sc.derivable else self.smooth

    # -- primitives -------------------------------------------------------
    def noul(self, q: NoulQuestion, state: Any = "") -> NoulAnswer:
        statement = as_text(q.instructions)
        if q.criteria and q.criteria.get("true") is not None:
            statement = as_text(q.criteria["true"])
        sc = self.score_option(state, statement)
        if not sc.interpretable:
            return NoulAnswer(noul=0.5, abstained=True, reason=sc.parsed.reason)
        return NoulAnswer(noul=self._exact_probability(sc))

    def choice(self, q: ChoiceQuestion, state: Any = "") -> ChoiceAnswer:
        names = list(q.criteria.keys())
        texts = [as_text(q.criteria[n]) if q.criteria[n] is not None else n for n in names]
        scores = [self.score_option(state, t) for t in texts]
        if any(not s.interpretable for s in scores):
            reason = next((s.parsed.reason for s in scores if not s.interpretable), "uninterpretable option")
            probs = {n: 1.0 / len(names) for n in names}
            return ChoiceAnswer(choice=names[0], probabilities=probs, confidence=0.0,
                                abstained=True, reason=reason)
        probs_list = softmax([self._logit(s) for s in scores], self.temperature)
        probabilities = {n: p for n, p in zip(names, probs_list)}
        best = max(range(len(names)), key=lambda i: probs_list[i])
        return ChoiceAnswer(choice=names[best], probabilities=probabilities,
                            confidence=derive_confidence(probs_list))

    def score(self, q: ScoreQuestion, state: Any = "") -> ScoreAnswer:
        """Ordinal decision: the KB must define ``level(i)`` (``level_pred``) per level."""
        levels = list(range(len(q.criteria)))
        scores = [self.score_option(state, f"{self.level_pred}({i})") for i in levels]
        legend = {str(i): q.criteria[i] for i in levels}
        if any(not s.interpretable for s in scores):
            probs = [1.0 / len(levels)] * len(levels)
            return ScoreAnswer(score=(len(levels) - 1) / 2.0, legend=legend,
                               probabilities={str(i): p for i, p in zip(levels, probs)},
                               confidence=0.0, abstained=True, reason="uninterpretable level")
        probs = softmax([self._logit(s) for s in scores], self.temperature)
        expected = sum(i * p for i, p in zip(levels, probs))
        return ScoreAnswer(score=expected, legend=legend,
                           probabilities={str(i): p for i, p in zip(levels, probs)},
                           confidence=derive_score_confidence(probs))

    # -- orchestration ----------------------------------------------------
    def decide(self, request: SystemOneRequest) -> SystemOneResponse:
        answers: dict[str, Answer] = {}
        for name, q in request.questions.items():
            if isinstance(q, NoulQuestion):
                answers[name] = self.noul(q, request.state)
            elif isinstance(q, ChoiceQuestion):
                answers[name] = self.choice(q, request.state)
            elif isinstance(q, ScoreQuestion):
                answers[name] = self.score(q, request.state)
            else:  # pragma: no cover - guarded by the wire types
                raise TypeError(f"unknown question type: {type(q)!r}")
        return SystemOneResponse(model=request.model, answers=answers, usage=Usage())