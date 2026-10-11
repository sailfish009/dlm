from dlm.answer import render_answer, resolve
from dlm.kb import KnowledgeBase
from dlm.logic import Atom, Const, Literal, Schema, SchemaRegistry
from dlm.query import YESNO, Query
from dlm.question import QuestionReader
from dlm.lexicon import third_person
from dlm.reader import AGENT, FIGURE, GROUND, PATIENT, SUBJECT
from dlm.realize import TemplateRealizer

SCHEMAS = (
    Schema("call", (AGENT, PATIENT)),
    Schema("happy", (SUBJECT,)),
    Schema("tall", (SUBJECT,)),
    Schema("in", (FIGURE, GROUND)),
)


def setup():
    kb = KnowledgeBase()
    kb.add_fact(Atom("call", (Const("alice"), Const("bob"))))
    kb.add_fact(Atom("happy", (Const("bob"),)))
    kb.add_fact(Atom("in", (Const("alice"), Const("tokyo"))))
    kb.add_negation(Atom("tall", (Const("alice"),)))
    registry = SchemaRegistry(SCHEMAS)
    qreader = QuestionReader(predicates=["call", "happy", "tall"], registry=registry, prepositions=["in"])
    template = TemplateRealizer(registry, surface=third_person)
    return kb, qreader, template


def test_yesno_yes():
    kb, qreader, template = setup()
    answer = resolve(qreader.query("is bob happy?"), kb)
    assert answer.decision == "yes" and not answer.abstain
    assert render_answer(answer, template) == "Yes, bob is happy."


def test_yesno_no_only_from_explicit_negative():
    kb, qreader, template = setup()
    answer = resolve(qreader.query("is alice tall?"), kb)
    assert answer.decision == "no"
    assert render_answer(answer, template) == "No, alice is not tall."


def test_yesno_unknown_is_not_no():
    kb, qreader, template = setup()
    answer = resolve(qreader.query("is alice happy?"), kb)
    assert answer.decision == "unknown" and answer.abstain
    assert render_answer(answer, template) == "I cannot decide whether alice is happy."


def test_wh_term():
    kb, qreader, template = setup()
    answer = resolve(qreader.query("who does alice call?"), kb)
    assert answer.decision == "list" and not answer.abstain
    assert render_answer(answer, template) == "alice calls bob."


def test_wh_predicate_answer():
    kb, qreader, template = setup()
    answer = resolve(qreader.query("what is bob?"), kb)
    assert answer.decision == "predicate"
    assert render_answer(answer, template) == "bob is happy."


def test_wh_miss_abstains():
    kb, qreader, template = setup()
    answer = resolve(qreader.query("where is bob?"), kb)
    assert answer.abstain and answer.decision == "unknown"


def test_yesno_negative_question():
    kb, qreader, template = setup()
    answer = resolve(qreader.query("is alice not tall?"), kb)
    assert answer.decision == "yes"
    assert render_answer(answer, template) == "Yes, alice is not tall."