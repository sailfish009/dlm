"""System-One wire types (Jev-compatible shape), standalone and dependency-free.

Mirrors ``strands_decider.schema`` without pydantic so the engine runs on the
6 GB research host. Three primitives, one mechanism: every question becomes N
options; the readout gives one score per option; a softmax gives the
distribution. Here the readout is a DLM proof, not a learned LM.

    noul   -> 2 slots (false, true)          -> P(true)
    choice -> N slots (one per option)       -> argmax + per-option probabilities
    score  -> L ordered levels               -> expected value over level indices
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Union

Content = Union[str, dict, list]
MAX_CHOICE_OPTIONS = 255
MIN_SCORE_LEVELS = 2
MAX_SCORE_LEVELS = 10


@dataclass
class NoulQuestion:
    """Yes/no. Returns the probability the statement is true."""

    instructions: Content
    criteria: dict[str, Content | None] | None = None
    type: Literal["noul"] = "noul"

    def __post_init__(self) -> None:
        if self.criteria is not None and not set(self.criteria).issubset({"true", "false"}):
            raise ValueError("noul criteria keys must be a subset of {'true', 'false'}")


@dataclass
class ChoiceQuestion:
    """Pick one of N named options. ``criteria`` maps option name -> description."""

    instructions: Content
    criteria: dict[str, Content | None]
    type: Literal["choice"] = "choice"

    def __post_init__(self) -> None:
        if not (MIN_SCORE_LEVELS <= len(self.criteria) <= MAX_CHOICE_OPTIONS):
            raise ValueError(f"choice needs 2..{MAX_CHOICE_OPTIONS} options")


@dataclass
class ScoreQuestion:
    """Rate against an ordered rubric. ``criteria`` is ascending (index 0 = low end)."""

    instructions: Content
    criteria: list[str]
    type: Literal["score"] = "score"

    def __post_init__(self) -> None:
        if not (MIN_SCORE_LEVELS <= len(self.criteria) <= MAX_SCORE_LEVELS):
            raise ValueError(f"score needs {MIN_SCORE_LEVELS}..{MAX_SCORE_LEVELS} levels")


Question = Union[NoulQuestion, ChoiceQuestion, ScoreQuestion]


@dataclass
class SystemOneRequest:
    state: Content
    questions: dict[str, Question]
    model: str = "dlm-engine-latest"
    images: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.questions:
            raise ValueError("at least one question is required")


@dataclass
class NoulAnswer:
    noul: float
    type: Literal["noul"] = "noul"
    abstained: bool = False
    reason: str = ""


@dataclass
class ChoiceAnswer:
    choice: str
    probabilities: dict[str, float]
    confidence: float
    type: Literal["choice"] = "choice"
    abstained: bool = False
    reason: str = ""


@dataclass
class ScoreAnswer:
    score: float
    legend: dict[str, str]
    probabilities: dict[str, float]
    confidence: float
    type: Literal["score"] = "score"
    abstained: bool = False
    reason: str = ""


Answer = Union[NoulAnswer, ChoiceAnswer, ScoreAnswer]


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class SystemOneResponse:
    model: str
    answers: dict[str, Answer]
    usage: Usage = field(default_factory=Usage)


def derive_confidence(probabilities: list[float]) -> float:
    """Normalised max-probability ``(N*p_max - 1) / (N - 1)``; uniform -> 0, one-hot -> 1."""
    n = len(probabilities)
    if n <= 1:
        return 1.0
    p_max = max(probabilities)
    return float(max(0.0, min(1.0, (n * p_max - 1.0) / (n - 1.0))))


def derive_score_confidence(probabilities: list[float], *, ordinal_smoothing: float = 0.0) -> float:
    """Confidence for an ordinal answer: ``(sigma_max - sigma) / (sigma_max - sigma_floor)``.

    On an ordered scale, mass on adjacent levels is confidence ("about 2.5"), not
    doubt; normalised std-dev captures that and ranks a bimodal distribution as
    worse than a uniform one.
    """
    n = len(probabilities)
    if n <= 1:
        return 1.0
    total = sum(probabilities)
    if total <= 0:
        return 0.0
    p = [x / total for x in probabilities]
    mean = sum(i * pi for i, pi in enumerate(p))
    sigma = (sum(pi * (i - mean) ** 2 for i, pi in enumerate(p))) ** 0.5
    sigma_max = (n - 1) / 2.0
    sigma_floor = ordinal_smoothing ** 0.5 if ordinal_smoothing > 0 else 0.0
    if sigma_max <= sigma_floor:
        return 1.0 if sigma <= sigma_floor else 0.0
    conf = (sigma_max - sigma) / (sigma_max - sigma_floor)
    return float(max(0.0, min(1.0, conf)))


def answer_to_dict(a: Answer) -> dict[str, Any]:
    d = dict(a.__dict__)
    return d