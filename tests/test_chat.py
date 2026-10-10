"""Tests for module 12: the S-expression chatbot (NOTE.md §35)."""
from __future__ import annotations

from random import Random

import pytest

from dlm.chat import (
    ChatRule,
    ChatScript,
    ChatSession,
    chat_once,
    fill,
    match,
    random_elt,
    swap_pronouns,
)
from dlm.convert import Ingestor
from dlm.kb import KnowledgeBase
from dlm.logic import Schema, SchemaRegistry
from dlm.reader import AGENT, PATIENT, SUBJECT, LexicalReader
from dlm.sexp import Sym, dump, parse


def make_ingestor() -> Ingestor:
    codes = {
        "calls": (AGENT, PATIENT),
        "likes": (AGENT, PATIENT),
        "happy": (SUBJECT,),
    }
    reader = LexicalReader(predicates=codes)
    registry = SchemaRegistry([Schema(p, r) for p, r in codes.items()])
    return Ingestor(reader, registry)


def make_session(**kwargs) -> ChatSession:
    return ChatSession(make_ingestor(), **kwargs)


# -- pattern engine ---------------------------------------------------------
def test_match_literal_and_single_wildcard():
    tokens = tuple(Sym(t) for t in "i feel sad".split())
    assert match((Sym("i"), Sym("feel"), Sym("*x")), tokens) == {"x": (Sym("sad"),)}
    assert match((Sym("i"), Sym("feel"), Sym("?x")), tokens) == {"x": Sym("sad")}
    assert match((Sym("i"), Sym("feel"), Sym("_")), tokens) == {}


def test_match_zero_or_more_backtracks():
    pattern = (Sym("a"), Sym("*x"), Sym("d"))
    assert match(pattern, tuple(Sym(t) for t in "a b c d".split())) == {
        "x": (Sym("b"), Sym("c"))
    }
    assert match(pattern, tuple(Sym(t) for t in "a d".split())) == {"x": ()}
    # the trailing "d" forces the greedy wildcard to give one back
    assert match(pattern, tuple(Sym(t) for t in "a d d".split())) == {
        "x": (Sym("d"),)
    }


def test_match_conflict_and_failure():
    pattern = (Sym("?x"), Sym("is"), Sym("?x"))
    assert match(pattern, tuple(Sym(t) for t in "bob is bob".split())) == {"x": Sym("bob")}
    assert match(pattern, tuple(Sym(t) for t in "bob is alice".split())) is None
    assert match((Sym("hello"),), (Sym("bye"),)) is None
    assert match((Sym("a"),), Sym("a")) is None  # list pattern needs a list form


def test_match_nested_lists():
    pattern = (Sym("f"), (Sym("?x"), Sym("?y")))
    form = (Sym("f"), (Sym("a"), Sym("b")))
    assert match(pattern, form) == {"x": Sym("a"), "y": Sym("b")}


# -- substitution / reflection ----------------------------------------------
def test_fill_reflects_only_bound_text():
    b = {"x": (Sym("my"), Sym("mother"))}
    assert fill("why do you feel {x}?", b) == "why do you feel your mother?"
    assert fill("no placeholder", b) == "no placeholder"
    assert fill("unknown {y} kept", b) == "unknown {y} kept"


def test_swap_pronouns():
    assert swap_pronouns("i am my own") == "you are your own"
    assert swap_pronouns("you are happy") == "i am happy"


def test_random_elt_is_deterministic_and_rejects_empty():
    class Stub:
        def randrange(self, n):
            return n - 1

    assert random_elt(("a", "b", "c"), Stub()) == "c"
    with pytest.raises(ValueError):
        random_elt((), Random(0))


# -- script -----------------------------------------------------------------
def test_chat_rule_needs_a_response():
    with pytest.raises(ValueError):
        ChatRule((Sym("x"),), ())


def test_script_first_match_wins_and_returns_none_without_match():
    rules = (
        ChatRule((Sym("a"),), ("first {x}",)),
        ChatRule((Sym("a"), Sym("*x")), ("second {x}",)),
    )
    script = ChatScript(rules)
    assert script.respond((Sym("a"),)) == "first {x}"
    assert script.respond((Sym("b"),)) is None
    assert len(script) == 2


def test_script_echoes_user_words_reflected():
    script = ChatScript((ChatRule((Sym("i"), Sym("feel"), Sym("*x")), ("why do you feel {x}?",)),))
    tokens = tuple(Sym(t) for t in "i feel my pain".split())
    assert script.respond(tokens) == "why do you feel your pain?"


# -- logic channel ----------------------------------------------------------
def test_assert_then_ask_round_trip():
    s = make_session()
    assert dump(s.respond(parse("(assert (parent alice bob))")[0])) == '(ok "learned" (parent alice bob))'
    reply = parse(chat_once(s, "(ask (parent alice bob))"))[0]
    assert reply[0] == Sym("answer")
    assert (Sym("verdict"), Sym("asserted")) in reply


def test_ask_abstains_when_unknown():
    reply = parse(chat_once(make_session(), "(ask (calls alice bob))"))[0]
    assert reply[0] == Sym("answer")
    assert (Sym("verdict"), Sym("abstain")) in reply


def test_side_table_refutes_the_positive():
    s = make_session()
    s.respond(parse("(assert (not (likes bob carol)))")[0])
    positive = parse(chat_once(s, "(ask (likes bob carol))"))[0]
    negative = parse(chat_once(s, "(ask (not (likes bob carol)))"))[0]
    assert (Sym("verdict"), Sym("refuted")) in positive
    assert (Sym("verdict"), Sym("asserted")) in negative


def test_assert_rejects_contradictions():
    s = make_session()
    s.respond(parse("(assert (calls alice bob))")[0])
    reply = parse(chat_once(s, "(assert (not (calls alice bob)))"))[0]
    assert reply[0] == Sym("no")

    s2 = make_session()
    s2.respond(parse("(assert (not (calls alice bob)))")[0])
    reply2 = parse(chat_once(s2, "(assert (calls alice bob))"))[0]
    assert reply2[0] == Sym("no")


def test_why_returns_proof_or_abstains():
    s = make_session()
    assert parse(chat_once(s, "(why (calls alice bob))"))[0][0] == Sym("abstain")
    s.respond(parse("(assert (parent alice bob))")[0])
    s.respond(parse("(rule (ancestor ?x ?y) (parent ?x ?y))")[0])
    proof = parse(chat_once(s, "(why (ancestor alice bob))"))[0]
    assert proof[0] == Sym("proof")
    derived = parse(chat_once(s, "(ask (ancestor alice bob))"))[0]
    assert (Sym("verdict"), Sym("asserted")) in derived


def test_rule_command_adds_a_rule():
    s = make_session()
    s.respond(parse("(assert (parent alice bob))")[0])
    reply = parse(chat_once(s, "(rule (ancestor ?x ?y) (parent ?x ?y))"))[0]
    assert reply[0] == Sym("ok")
    assert Sym("ancestor") in parse(chat_once(s, "(ask (ancestor alice bob))"))[0][1]


def test_retract_fact_and_rule():
    s = make_session()
    s.respond(parse("(assert (parent alice bob))")[0])
    s.respond(parse("(rule (ancestor ?x ?y) (parent ?x ?y))")[0])
    chat_once(s, "(retract (parent alice bob))")
    assert s.kb.has_fact(_atom("parent", "alice", "bob")) is False
    assert parse(chat_once(s, "(ask (ancestor alice bob))"))[0][0] == Sym("answer")


def test_facts_and_rules_dump_the_kb():
    s = make_session()
    s.respond(parse("(assert (calls alice bob))")[0])
    s.respond(parse("(rule (ancestor ?x ?y) (parent ?x ?y))")[0])
    facts = parse(chat_once(s, "(facts)"))[0]
    rules = parse(chat_once(s, "(rules)"))[0]
    assert facts[0] == Sym("facts") and Sym("calls") in facts[1]
    assert rules[0] == Sym("rules") and rules[1][0] == Sym("rule")


def test_read_command_uses_ingress():
    reply = parse(chat_once(make_session(), '(read "Alice calls Bob")'))[0]
    assert reply == (Sym("read"), (Sym("calls"), Sym("alice"), Sym("bob")))


# -- boundary + chatter -----------------------------------------------------
def test_nl_line_is_read_when_ingress_understands_it():
    reply = parse(chat_once(make_session(), "Alice calls Bob"))[0]
    assert reply[0] == Sym("read")


def test_chatter_reflects_without_asserting_anything():
    s = make_session()
    before = len(s.kb)
    reply = parse(chat_once(s, "i feel sad"))[0]
    assert reply[0] == Sym("reply")
    assert "sad" in reply[1]
    assert len(s.kb) == before  # chatter never grows the KB


def test_unreadable_line_abstains():
    reply = parse(chat_once(make_session(), "what is the meaning of life"))[0]
    assert reply[0] == Sym("abstain")


def test_reply_is_valid_sexp_round_trip():
    s = make_session()
    s.respond(parse("(assert (calls alice bob))")[0])
    for line in [
        "(ask (calls alice bob))",
        "(facts)",
        "(rules)",
        "(why (calls alice bob))",
        "i feel sad",
        "hello",
        "gibberish nonsense here",
    ]:
        text = chat_once(s, line)
        assert dump(parse(text)[0]) == text  # stable S-expression


def test_respond_accepts_string_and_form_equivalently():
    a = make_session()
    b = make_session()
    from_str = a.respond("hello")[1]
    from_form = b.respond((Sym("hello"),))[1]
    assert from_str == from_form


def _atom(pred, *names):
    from dlm.logic import Atom, Const

    return Atom(pred, tuple(Const(n) for n in names))