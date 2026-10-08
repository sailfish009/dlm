"""Adapter layer: expose DLM to CLM / strands-decider shaped callers.

Two things live here.

``DlmTorso`` keeps the *shape* of a torso without being one. CLM heads and the
strands-decider heads consume a fixed-width vector per state/option. DLM has no
contextual embedding; it has a small number of **exact** signals. So the adapter
returns a vector whose width is ``FEATURE_NAMES`` — set the head's ``hidden`` to
that width and the head code is unchanged, but the representation is discrete
proof evidence, not learned statistics.

``SystemOneService`` is the wire boundary: parse a strands-decider-shaped request
dict, run :class:`~dlm.decision.DecisionEngine`, and serialise the response back
to plain dicts. It is the drop-in surface for an HTTP handler; no server is
started here.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Sequence

import numpy as np

from .decision import DecisionEngine, as_text
from .kb import KnowledgeBase
from .schema import (
    Answer,
    ChoiceQuestion,
    NoulQuestion,
    Question,
    ScoreQuestion,
    SystemOneRequest,
    SystemOneResponse,
)

# The exact signals a head may read. Width = len(FEATURE_NAMES).
FEATURE_NAMES = (
    "interpretable",   # could the option be turned into an atom?
    "derivable",       # did the KB entail it (after closed-world negation)?
    "negated",         # was the option stated as a negation?
    "exact_prob",      # smoothly floored derivability probability
    "n_proofs",        # number of proofs found
    "min_depth",       # depth of the shallowest proof
    "log_n_proofs",    # log1p(n_proofs), for a head that wants scale-free input
)


class DlmTorso:
    """A torso-shaped view of DLM that returns discrete features, not embeddings.

    The reference CLM head maps a 4096-d encoder embedding; here set the head's
    input width to ``len(FEATURE_NAMES)`` (7). Use ``features`` / ``batch_features``
    for option-level heads (pointer) and ``state_features`` for pooled heads (slot).
    """

    num_features = len(FEATURE_NAMES)

    def __init__(self, engine: DecisionEngine):
        self.engine = engine

    def features(self, state: Any, option: str) -> np.ndarray:
        sc = self.engine.score_option(state, option)
        return np.asarray([
            1.0 if sc.interpretable else 0.0,
            1.0 if sc.derivable else 0.0,
            1.0 if sc.parsed.negated else 0.0,
            self.engine._exact_probability(sc) if sc.interpretable else 0.0,
            float(sc.n_proofs),
            float(sc.min_depth),
            math.log1p(sc.n_proofs),
        ], dtype=np.float32)

    def batch_features(self, state: Any, options: Sequence[str]) -> np.ndarray:
        """-> [N, num_features] float32, one row per option (pointer-head shape)."""
        if not options:
            return np.zeros((0, self.num_features), dtype=np.float32)
        return np.stack([self.features(state, o) for o in options])

    def state_features(self, state: Any = "") -> np.ndarray:
        """A fixed statistic of the KB, not a learned state embedding (slot-head shape)."""
        kb: KnowledgeBase = self.engine.kb
        facts = list(kb.facts())
        rules = list(kb.rules())
        n_facts = len(facts)
        n_rules = len(rules)
        preds = {a.pred for a in facts} | {r.head.pred for r in rules}
        return np.asarray([
            float(n_facts),
            float(n_rules),
            float(len(preds)),
            math.log1p(n_facts),
        ], dtype=np.float32)


# -- wire boundary ---------------------------------------------------------
def parse_question(d: dict[str, Any]) -> Question:
    t = d.get("type")
    if t == "noul":
        return NoulQuestion(instructions=d["instructions"], criteria=d.get("criteria"))
    if t == "choice":
        return ChoiceQuestion(instructions=d["instructions"], criteria=d["criteria"])
    if t == "score":
        return ScoreQuestion(instructions=d["instructions"], criteria=d["criteria"])
    raise ValueError(f"unknown question type: {t!r}")


def parse_request(d: dict[str, Any]) -> SystemOneRequest:
    return SystemOneRequest(
        state=d.get("state", ""),
        questions={name: parse_question(q) for name, q in d["questions"].items()},
        model=d.get("model", "dlm-engine-latest"),
        images=list(d.get("images", [])),
    )


def answer_to_dict(a: Answer) -> dict[str, Any]:
    return dict(a.__dict__)


def response_to_dict(resp: SystemOneResponse) -> dict[str, Any]:
    return {
        "model": resp.model,
        "answers": {name: answer_to_dict(a) for name, a in resp.answers.items()},
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
    }


class SystemOneService:
    """Handle a wire request dict end to end. No network; call ``handle`` directly."""

    def __init__(self, engine: DecisionEngine, model: str = "dlm-engine-latest"):
        self.engine = engine
        self.model = model

    def decide(self, request: SystemOneRequest) -> SystemOneResponse:
        if request.model == "dlm-engine-latest":
            request.model = self.model
        return self.engine.decide(request)

    def handle(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = parse_request(payload)
        return response_to_dict(self.decide(request))

    def handle_many(self, payloads: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.handle(p) for p in payloads]