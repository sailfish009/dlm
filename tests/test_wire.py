"""Tests for the System-One wire boundary (module 9)."""
from __future__ import annotations

import pytest

from dlm.convert import Ingestor
from dlm.kb import DictStateGrounder, KnowledgeBase, StateBinding
from dlm.logic import Schema, SchemaRegistry
from dlm.reader import AGENT, PATIENT, LexicalReader
from dlm.wire import (
    DlmService,
    WireError,
    WireService,
    render_choice,
    render_noul,
    render_score,
    systemone,
)


def ingestor() -> Ingestor:
    registry = SchemaRegistry(
        [Schema("calls", (AGENT, PATIENT)), Schema("knows", (AGENT, PATIENT))]
    )
    reader = LexicalReader(predicates={"calls", "knows"})
    grounder = DictStateGrounder([StateBinding("edge", "calls", (AGENT, PATIENT))])
    return Ingestor(reader, registry, grounder)


def request(**overrides):
    base = {
        "state": {},
        "questions": {
            "q": {"type": "noul", "instructions": "Alice knows Bob"},
        },
    }
    base.update(overrides)
    return base


def service(**kwargs) -> DlmService:
    return DlmService(ingestor(), **kwargs)


# -- noul ------------------------------------------------------------------
def test_noul_true_through_a_rule_with_proof():
    svc = service()
    resp = svc.answer(
        request(theory=["(calls alice bob)", "(rule (knows ?x ?y) (calls ?x ?y))"])
    )
    a = resp["answers"]["q"]
    assert a["type"] == "noul" and a["abstain"] is False
    assert a["noul"] == 1.0 and a["verdict"] == "asserted"
    assert a["literal"] == "(knows alice bob)" and a["proof"]


def test_noul_false_only_from_an_explicit_negative():
    svc = service()
    resp = svc.answer(
        request(theory=["(not (calls alice bob))"],
                questions={"q": {"type": "noul", "instructions": "Alice calls Bob"}})
    )
    a = resp["answers"]["q"]
    assert a["noul"] == 0.0 and a["abstain"] is False


def test_noul_abstains_when_absence_is_not_refutation():
    resp = service().answer(request(theory=["(calls alice bob)"]))
    a = resp["answers"]["q"]
    assert a["abstain"] is True and a["noul"] is None and a["reason"] == "not on record"


def test_noul_abstains_when_statement_is_not_normalizable():
    resp = service().answer(
        request(questions={"q": {"type": "noul", "instructions": "Alice flies"}})
    )
    a = resp["answers"]["q"]
    assert a["abstain"] is True and a["literal"] is None
    assert a["reason"] == "statement not normalizable"


# -- choice ----------------------------------------------------------------
def test_choice_picks_the_single_provable_option():
    resp = service().answer(
        request(
            theory=["(calls alice bob)"],
            questions={
                "q": {
                    "type": "choice",
                    "criteria": {"a": "Alice calls Bob", "b": "Bob calls Alice"},
                }
            },
        )
    )
    a = resp["answers"]["q"]
    assert a["choice"] == "a" and a["abstain"] is False and a["confidence"] == 1.0
    assert a["probabilities"] == {"a": 1.0, "b": 0.0}
    assert a["verdicts"]["a"] == "asserted"


def test_choice_abstains_when_nothing_is_provable():
    resp = service().answer(
        request(
            questions={
                "q": {
                    "type": "choice",
                    "criteria": {"a": "Alice calls Bob", "b": "Bob calls Alice"},
                }
            }
        )
    )
    a = resp["answers"]["q"]
    assert a["choice"] is None and a["abstain"] is True
    assert a["reason"] == "no option is provable" and "confidence" not in a


def test_choice_abstains_when_multiple_options_are_provable():
    resp = service().answer(
        request(
            theory=["(calls alice bob)", "(calls bob alice)"],
            questions={
                "q": {
                    "type": "choice",
                    "criteria": {"a": "Alice calls Bob", "b": "Bob calls Alice"},
                }
            },
        )
    )
    a = resp["answers"]["q"]
    assert a["choice"] is None and a["abstain"] is True
    assert "ambiguous" in a["reason"]


# -- score -----------------------------------------------------------------
def test_score_question_abstains_template_only():
    resp = service().answer(
        request(questions={"q": {"type": "score", "criteria": ["low", "high"]}})
    )
    a = resp["answers"]["q"]
    assert a == {
        "type": "score",
        "score": None,
        "abstain": True,
        "reason": "score questions are outside the function-free Horn fragment",
    }


# -- seam A: grounded state ------------------------------------------------
def test_state_is_grounded_and_used():
    svc = service()
    resp = svc.answer(
        request(
            state={"edge": ["alice", "bob"]},
            questions={"q": {"type": "noul", "instructions": "Alice calls Bob"}},
        )
    )
    assert resp["answers"]["q"]["noul"] == 1.0


# -- validation ------------------------------------------------------------
def test_validation_errors():
    svc = service()
    with pytest.raises(WireError):
        svc.answer({"questions": {"q": {"type": "noul", "instructions": "x"}}})
    with pytest.raises(WireError):
        svc.answer({"state": {}, "questions": {}})
    with pytest.raises(WireError):
        svc.answer({"state": {}, "questions": {"q": {"type": "mystery"}}})
    with pytest.raises(WireError):
        svc.answer(
            {"state": {}, "questions": {"q": {"type": "choice", "criteria": {}}}}
        )
    with pytest.raises(WireError):
        svc.answer({"state": {}, "questions": {"q": {"type": "noul"}}, "theory": "x"})
    with pytest.raises(WireError):
        svc.answer(
            {"state": {}, "questions": {"q": {"type": "noul"}}, "theory": ["(rule"]}
        )
    with pytest.raises(WireError):
        svc.answer(
            {
                "state": {},
                "questions": {"q": {"type": "noul"}},
                "theory": ["(calls ?x bob)"],  # non-ground fact -> not admissible
            }
        )


def test_request_does_not_mutate_the_base_kb():
    kb = KnowledgeBase()
    svc = service(kb=kb)
    svc.answer(request(theory=["(calls alice bob)"]))
    assert kb.facts() == ()


# -- usage / shape ---------------------------------------------------------
def test_usage_counts_and_model():
    resp = service().answer(
        request(
            theory=["(calls alice bob)"],
            questions={
                "a": {"type": "noul", "instructions": "Alice calls Bob"},
                "b": {"type": "noul", "instructions": "Alice knows Bob"},
            },
        )
    )
    assert resp["model"] == "dlm-v0.0006"
    assert resp["usage"] == {
        "billing_units": 2,
        "questions": 2,
        "asserted": 1,
        "abstained": 1,
    }


# -- interoperability ------------------------------------------------------
class _FakeService:
    def answer(self, request):
        return {"model": "fake", "answers": {}, "usage": {}}


def test_wire_service_protocol_and_systemone_dispatch():
    assert isinstance(_FakeService(), WireService)
    assert isinstance(service(), WireService)
    assert systemone(_FakeService(), request())["model"] == "fake"


# -- egress renderers are directly usable ----------------------------------
def test_renderers_shape():
    assert render_noul(None, None, reason="why")["abstain"] is True
    assert render_choice("a", {"a": 1.0, "b": 0.0}, {"a": "asserted"}, {"a": "(x)"})[
        "choice"
    ] == "a"
    assert render_score()["abstain"] is True