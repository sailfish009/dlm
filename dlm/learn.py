"""Module 13: a *trainable* reader -- the seam-B trainability probe (NOTE.md §38).

This module exists to answer one falsifiable question: **is the reader seam
(B) trainable at all?**  It provides a small, stdlib-only learned reader that
plugs into the very same ingress gate (``SchemaRegistry.normalize``) as the
hand-authored :class:`~dlm.reader.LexicalReader`.

The learned reader is a token tagger (averaged perceptron) over a fixed tag set::

    AGENT PATIENT FIGURE GROUND SUBJECT   -- role of an entity token
    PRED                                  -- the predicate token
    NEG                                   -- a negation marker
    O                                     -- everything else

Decoding is deterministic: exactly one PRED token, resolve it through a
surface->canonical predicate lexicon, collect the role tokens (a repeated role
is ambiguous -> abstain), and build a :class:`~dlm.logic.Frame`.  A frame that
``normalize`` cannot accept abstains, exactly like any other untrusted proposer.

What is *learned* here is role assignment and negation detection; predicate
identity is a lexicon looked up from the training pairs.  The probe in
``experiments/trainability.py`` measures whether that learned part generalizes
across entities, across unseen predicate lexemes, and across unseen sentence
templates -- and, crucially, whether errors are abstains or *false asserts*.

The core package stays stdlib-only; there is no torch/numpy dependency.
"""
from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .logic import Const, Frame
from .reader import AGENT, FIGURE, GROUND, PATIENT, SUBJECT, Reader, tokenize

__all__ = [
    "PRED",
    "NEG",
    "OTHER",
    "ROLE_LABELS",
    "TAG_LABELS",
    "ReaderExample",
    "token_features",
    "AveragedPerceptron",
    "LearnedReader",
    "build_pred_lexicon",
    "train_tagger",
    "train_reader",
]

PRED = "PRED"
NEG = "NEG"
OTHER = "O"
ROLE_LABELS: Tuple[str, ...] = (AGENT, PATIENT, FIGURE, GROUND, SUBJECT)
TAG_LABELS: Tuple[str, ...] = (*ROLE_LABELS, PRED, NEG, OTHER)

_FUNCTION_WORDS = frozenset(
    {"is", "are", "was", "were", "am", "be", "been", "being", "by", "not", "never", "do", "does", "did"}
)


@dataclass(frozen=True)
class ReaderExample:
    """One supervised reader example: sentence, gold frame, per-token tags.

    ``labels`` is aligned with ``tokenize(sentence)``.  The gold frame carries
    the *canonical* predicate (which a surface->canonical lexicon learns).
    """

    sentence: str
    frame: Frame
    labels: Tuple[str, ...]

    def tokens(self) -> Tuple[str, ...]:
        return tokenize(self.sentence)


def _shape(word: str) -> str:
    if word.isdigit():
        return "num"
    if word.isupper():
        return "upper"
    if word[:1].isupper():
        return "title"
    return "lower"


def token_features(tokens: Sequence[str], i: int) -> Tuple[str, ...]:
    """Local features for token ``i`` (identity, context, position, shape)."""
    n = len(tokens)
    w = tokens[i].lower()
    feats: List[str] = [
        "bias",
        f"w={w}",
        f"pos={i}",
        f"ipos={n - 1 - i}",
        f"func={w in _FUNCTION_WORDS}",
        f"shape={_shape(tokens[i])}",
    ]
    if i > 0:
        feats.append(f"w-1={tokens[i - 1].lower()}")
    if i + 1 < n:
        feats.append(f"w+1={tokens[i + 1].lower()}")
    if i > 1:
        feats.append(f"w-2={tokens[i - 2].lower()}")
    if i + 2 < n:
        feats.append(f"w+2={tokens[i + 2].lower()}")
    return tuple(feats)

class AveragedPerceptron:
    """A tiny deterministic multiclass averaged perceptron (stdlib only)."""

    def __init__(self, labels: Iterable[str] = TAG_LABELS, *, seed: int = 0) -> None:
        self.labels: Tuple[str, ...] = tuple(labels)
        self.seed = seed
        self._w: Dict[Tuple[str, str], float] = {}
        self._totals: Dict[Tuple[str, str], float] = {}
        self._stamps: Dict[Tuple[str, str], int] = {}
        self.step = 0

    def scores(self, feats: Sequence[str]) -> Dict[str, float]:
        w = self._w
        return {label: sum(w.get((f, label), 0.0) for f in feats) for label in self.labels}

    def predict(self, feats: Sequence[str]) -> str:
        best, best_score = self.labels[0], None
        for label, score in self.scores(feats).items():
            if best_score is None or score > best_score:
                best, best_score = label, score
        return best

    def predict_all(self, tokens: Sequence[str]) -> Tuple[str, ...]:
        return tuple(self.predict(token_features(tokens, i)) for i in range(len(tokens)))

    def _bump(self, feat: str, label: str, delta: float) -> None:
        key = (feat, label)
        self._totals[key] = self._totals.get(key, 0.0) + delta * (self.step - self._stamps.get(key, 0))
        self._stamps[key] = self.step
        self._w[key] = self._w.get(key, 0.0) + delta

    def update(self, feats: Sequence[str], gold: str, pred: str) -> None:
        for feat in feats:
            self._bump(feat, gold, 1.0)
            self._bump(feat, pred, -1.0)

    def tick(self) -> None:
        """Advance the averaging clock for one training instance."""
        self.step += 1

    def finalize(self) -> "AveragedPerceptron":
        """Replace weights with their average over training (voted perceptron)."""
        avg: Dict[Tuple[str, str], float] = {}
        for key, weight in self._w.items():
            total = self._totals.get(key, 0.0) + weight * (self.step - self._stamps.get(key, 0))
            if self.step:
                total /= self.step
            avg[key] = total
        self._w = avg
        self._totals = {}
        self._stamps = {}
        return self


def train_tagger(
    examples: Sequence[ReaderExample],
    labels: Sequence[str] = TAG_LABELS,
    *,
    epochs: int = 12,
    seed: int = 0,
) -> AveragedPerceptron:
    """Train an averaged perceptron token tagger from gold-tagged examples."""
    model = AveragedPerceptron(labels, seed=seed)
    data = [(ex.tokens(), ex.labels) for ex in examples]
    rng = Random(seed)
    for _ in range(epochs):
        rng.shuffle(data)
        for tokens, gold in data:
            if len(tokens) != len(gold):
                continue
            feats = [token_features(tokens, i) for i in range(len(tokens))]
            preds = [model.predict(f) for f in feats]
            for i, (g, p) in enumerate(zip(gold, preds)):
                if g != p:
                    model.update(feats[i], g, p)
                model.tick()
    return model.finalize()


def build_pred_lexicon(examples: Sequence[ReaderExample]) -> Dict[str, str]:
    """Map each surface predicate token to the canonical predicate it denotes."""
    lex: Dict[str, str] = {}
    for ex in examples:
        tokens = ex.tokens()
        for tok, tag in zip(tokens, ex.labels):
            if tag == PRED:
                lex.setdefault(tok.lower(), ex.frame.pred)
    return lex


@dataclass
class LearnedReader:
    """A trainable seam-B reader: tagger + surface->canonical predicate lexicon.

    ``read`` never guesses structure it was not trained to see: if there is not
    exactly one predicate token, if the predicate is unknown to the lexicon, or
    if a role is assigned twice, it returns no frames (i.e. it abstains).
    """

    tagger: AveragedPerceptron
    lexicon: Dict[str, str]

    def read(self, sentence: str) -> Tuple[Frame, ...]:
        tokens = tokenize(sentence)
        if not tokens:
            return ()
        tags = self.tagger.predict_all(tokens)

        pred_positions = [i for i, t in enumerate(tags) if t == PRED]
        if len(pred_positions) != 1:
            return ()
        pred = self.lexicon.get(tokens[pred_positions[0]].lower())
        if pred is None:
            return ()

        slots: List[Tuple[str, Const]] = []
        seen: set = set()
        for i, t in enumerate(tags):
            if t in ROLE_LABELS:
                if t in seen:
                    return ()
                seen.add(t)
                slots.append((t, Const(tokens[i].lower())))

        negated = any(t == NEG for t in tags)
        try:
            frame = Frame(pred, tuple(slots), negated)
        except (TypeError, ValueError):
            return ()
        return (frame,)


def train_reader(
    examples: Sequence[ReaderExample],
    labels: Sequence[str] = TAG_LABELS,
    *,
    epochs: int = 12,
    seed: int = 0,
    tagger: Optional[AveragedPerceptron] = None,
) -> LearnedReader:
    """Train a :class:`LearnedReader` end to end from supervised examples."""
    if tagger is None:
        tagger = train_tagger(examples, labels, epochs=epochs, seed=seed)
    return LearnedReader(tagger=tagger, lexicon=build_pred_lexicon(examples))
