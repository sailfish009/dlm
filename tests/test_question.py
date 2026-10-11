from dlm.logic import Atom, Const, Schema, SchemaRegistry, Var
from dlm.query import WH, YESNO
from dlm.question import QuestionReader, looks_like_question
from dlm.reader import AGENT, FIGURE, GROUND, PATIENT, SUBJECT

PREDS = ["call", "like", "happy", "tall"]
PREPS = ["in", "at"]
SCHEMAS = (
    Schema("call", (AGENT, PATIENT)),
    Schema("like", (AGENT, PATIENT)),
    Schema("happy", (SUBJECT,)),
    Schema("tall", (SUBJECT,)),
    Schema("in", (FIGURE, GROUND)),
    Schema("at", (FIGURE, GROUND)),
)


def reader() -> QuestionReader:
    return QuestionReader(predicates=PREDS, registry=SchemaRegistry(SCHEMAS), prepositions=PREPS)


def test_yesno_copula():
    q = reader().query("is alice happy?")
    assert q is not None and q.kind == YESNO
    assert q.literal.atom == Atom("happy", (Const("alice"),))


def test_yesno_do_support_lemmatised():
    q = reader().query("does alice call bob?")
    assert q is not None and q.kind == YESNO
    assert q.literal.atom == Atom("call", (Const("alice"), Const("bob")))


def test_yesno_copula_preposition():
    q = reader().query("is alice in tokyo?")
    assert q is not None and q.kind == YESNO
    assert q.literal.atom == Atom("in", (Const("alice"), Const("tokyo")))


def test_wh_term_who_do():
    q = reader().query("who does alice call?")
    assert q is not None and q.kind == WH and q.answer_var == Var("x")
    assert Atom("call", (Const("alice"), Var("x"))) in q.patterns


def test_wh_enumerates_relations_for_where():
    q = reader().query("where is alice?")
    assert q is not None and q.kind == WH and q.answer_var == Var("x")
    preds = {p.pred for p in q.patterns}
    assert preds == {"in", "at"}
    assert all(p.args[1] == Var("x") for p in q.patterns)


def test_wh_predicate_answer():
    q = reader().query("what is alice?")
    assert q is not None and q.kind == WH and q.answer_is_predicate
    assert {p.pred for p in q.patterns} == {"happy", "tall"}


def test_declarative_is_not_a_question():
    assert reader().read("alice calls bob") == ()
    assert not looks_like_question("alice calls bob")


def test_looks_like_question_markers():
    assert looks_like_question("alice calls bob?")
    assert looks_like_question("who calls bob")
    assert looks_like_question("does alice call bob")