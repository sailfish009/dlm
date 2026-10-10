"""Tests for module 11: the checked egress boundary (seam E)."""
from __future__ import annotations

import pytest

from dlm.convert import Ingestor
from dlm.judge import Judgement, ProofJudge, Verdict
from dlm.kb import KnowledgeBase
from dlm.logic import Atom, Const, Literal, Schema, SchemaRegistry
from dlm.reader import AGENT, FIGURE, GROUND, PATIENT, SUBJECT, LexicalReader
from dlm.realize import (
    Bundle,
    CheckedRealizer,
    Realization,
    RealizedService,
    Realizer,
    TemplateRealizer,
    bundle_from_answer,
)
from dlm.wire import DlmService


def C(name):
    return Const(name)


def A(pred, *names):
    return Atom(pred, tuple(C(n) for n in names))


CODES = {
    "calls": (AGENT, PATIENT),
    "sleeps": (AGENT,),
    "happy": (SUBJECT,),
    "on": (FIGURE, GROUND),
}


def make_ingestor() -> Ingestor:
    registry = SchemaRegistry([Schema(p, roles) for p, roles in CODES.items()])
    reader = LexicalReader(predicates=CODES.keys())
    return Ingestor(reader, registry)


def lit(pred, *names, negated=False):
    return Literal(A(pred, *names), negated=negated)


# -- the template realizer -------------------------------------------------
@pytest.mark.parametrize(
    "literal, text",
    [
        (lit("calls", "alice", "bob"), "alice calls bob"),
        (lit("sleeps", "alice"), "alice sleeps"),
        (lit("happy", "alice"), "alice is happy"),
        (lit("on", "book", "table"), "book is on table"),
        (lit("calls", "alice", "bob", negated=True), "alice not calls bob"),
        (lit("happy", "alice", negated=True), "alice is not happy"),
    ],
)
def test_template_realizer_renders_each_shape(literal, text):
    realizer = TemplateRealizer(make_ingestor().registry)
    assert realizer.realize(Bundle("asserted", False, literal)) == text


def test_template_round_trips_through_the_ingestor():
    ingestor = make_ingestor()
    realizer = TemplateRealizer(ingestor.registry)
    for literal in [
        lit("calls", "alice", "bob"),
        lit("sleeps", "alice"),
        lit("happy", "alice"),
        lit("on", "book", "table"),
        lit("calls", "alice", "bob", negated=True),
        lit("happy", "alice", negated=True),
    ]:
        text = realizer.realize(Bundle("asserted", False, literal))
        assert ingestor.literal(text) == literal


def test_template_declines_unknown_predicate_and_non_ground():
    from dlm.logic import Var

    registry = SchemaRegistry([Schema("calls", (AGENT, PATIENT))])
    realizer = TemplateRealizer(registry)
    unknown = Literal(A("unknown", "a", "b"))
    assert realizer.realize(Bundle("asserted", False, unknown)) is None
    # a variable-laden literal is not ground -> decline
    nonground = Literal(Atom("calls", (Var("x"), C("b"))))
    assert realizer.render(nonground) is None


def test_template_never_realizes_an_abstain_bundle():
    realizer = TemplateRealizer(make_ingestor().registry)
    assert realizer.realize(Bundle("abstain", True, lit("calls", "alice", "bob"))) is None


# -- the checked gate ------------------------------------------------------
class _Liar:
    """A realizer that always returns a false claim."""

    def __init__(self, text: str) -> None:
        self.text = text

    def realize(self, bundle: Bundle):
        return self.text


def test_check_accepts_a_faithful_candidate():
    ingestor = make_ingestor()
    checked = CheckedRealizer(TemplateRealizer(ingestor.registry), ingestor)
    literal = lit("calls", "alice", "bob")
    result = checked.realize_checked(Bundle("asserted", False, literal))
    assert (result.accepted, result.round_trip, result.source) == (True, True, "realizer")
    assert result.text == "alice calls bob"


def test_check_rejects_a_lying_realizer():
    ingestor = make_ingestor()
    checked = CheckedRealizer(_Liar("bob calls alice"), ingestor)
    literal = lit("calls", "alice", "bob")
    result = checked.realize_checked(Bundle("asserted", False, literal))
    assert result.text is None and not result.accepted and not result.round_trip
    assert "mismatch" in result.reason


def test_check_rejects_unreadable_text():
    ingestor = make_ingestor()
    checked = CheckedRealizer(_Liar("the cat sat on the mat"), ingestor)
    result = checked.realize_checked(Bundle("asserted", False, lit("calls", "alice", "bob")))
    assert result.text is None and "unreadable" in result.reason


def test_fallback_is_checked_and_can_recover():
    ingestor = make_ingestor()
    checked = CheckedRealizer(
        _Liar("bob calls alice"),
        ingestor,
        fallback=TemplateRealizer(ingestor.registry),
    )
    literal = lit("calls", "alice", "bob")
    result = checked.realize_checked(Bundle("asserted", False, literal))
    assert result.accepted and result.source == "fallback" and result.text == "alice calls bob"


def test_check_is_a_structural_abstain_guard():
    ingestor = make_ingestor()
    # even a "perfect" realizer is not consulted for an abstain bundle
    checked = CheckedRealizer(_Liar("alice calls bob"), ingestor)
    result = checked.realize_checked(Bundle("abstain", True, lit("calls", "alice", "bob")))
    assert result.text is None and result.source == "guard"


def test_checked_realizer_is_a_realizer():
    assert isinstance(CheckedRealizer(_Liar("x"), make_ingestor()), Realizer)


# -- bundles ---------------------------------------------------------------
def test_bundle_from_judgement_carries_the_proof():
    kb = KnowledgeBase().add_fact(A("calls", "alice", "bob"))
    judgement = ProofJudge().judge(kb, lit("calls", "alice", "bob"))
    bundle = Bundle.from_judgement(judgement)
    assert bundle.asserted and not bundle.abstain and bundle.proof is not None
    assert bundle.literal == lit("calls", "alice", "bob")

    miss = ProofJudge().judge(kb, lit("calls", "bob", "alice"))
    assert Bundle.from_judgement(miss).abstain


def test_bundle_from_answer_parses_the_literal():
    ingestor = make_ingestor()
    answer = {"type": "noul", "verdict": "asserted", "abstain": False, "literal": "(calls alice bob)"}
    bundle = bundle_from_answer(answer, ingestor)
    assert bundle.literal == lit("calls", "alice", "bob") and not bundle.abstain


def test_bundle_from_choice_answer_uses_the_chosen_literal():
    ingestor = make_ingestor()
    answer = {
        "type": "choice",
        "choice": "b",
        "abstain": False,
        "literal": None,
        "literals": {"a": None, "b": "(sleeps alice)"},
    }
    bundle = bundle_from_answer(answer, ingestor)
    assert bundle.literal == lit("sleeps", "alice")


# -- wire integration ------------------------------------------------------
def test_realized_service_adds_text_only_to_decided_answers():
    ingestor = make_ingestor()
    kb = KnowledgeBase().add_fact(A("calls", "alice", "bob"))
    service = DlmService(ingestor, kb)
    checked = CheckedRealizer(TemplateRealizer(ingestor.registry), ingestor)
    realized = RealizedService(service, checked, ingestor)

    response = realized.answer(
        {
            "state": {},
            "questions": {
                "yes": {"type": "noul", "instructions": "Alice calls Bob"},
                "miss": {"type": "noul", "instructions": "Bob calls Alice"},
                "score": {"type": "score"},
            },
        }
    )
    answers = response["answers"]
    assert answers["yes"]["text"] == "alice calls bob"
    assert answers["miss"]["abstain"] and answers["miss"]["text"] is None
    assert answers["score"]["abstain"] and answers["score"]["text"] is None
    # the honesty fields are untouched
    assert answers["yes"]["verdict"] == "asserted"