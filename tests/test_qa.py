from dlm.logic import Schema
from dlm.qa import default_qa_session
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


def session():
    return default_qa_session(PREDS, PREPS, SCHEMAS)


def test_learn_then_yes():
    s = session()
    assert s.turn("alice calls bob").startswith("OK, I learned")
    assert s.turn("does alice call bob?") == "Yes, alice calls bob."


def test_unknown_is_not_false_assertion():
    s = session()
    s.turn("alice calls bob")
    assert s.turn("does bob call alice?") == "I cannot decide whether bob calls alice."


def test_wh_question():
    s = session()
    s.turn("alice calls bob")
    assert s.turn("who does alice call?") == "alice calls bob."


def test_explicit_negative_gives_no():
    s = session()
    s.turn("alice is not tall")
    assert s.turn("is alice tall?") == "No, alice is not tall."


def test_predicate_answer():
    s = session()
    s.turn("alice is happy")
    assert s.turn("what is alice?") == "alice is happy."


def test_chatter_fallback_is_assertion_free():
    s = session()
    reply = s.turn("hello")
    assert "Sorry" not in reply


def test_unreadable_sentence_abstains():
    s = session()
    assert s.turn("the quick brown fox") == "Sorry, I could not understand that sentence."