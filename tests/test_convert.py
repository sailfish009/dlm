"""Tests for the input ingress (seam B gate, module 7)."""
from __future__ import annotations

import pytest

from dlm.convert import (
    Ingestor,
    form_to_logic,
    sentence_to_literal,
    sentence_to_literals,
)
from dlm.logic import Atom, Const, Frame, Literal, Rule, Schema, SchemaRegistry
from dlm.reader import AGENT, PATIENT, LexicalReader
from dlm.sexp import SexpError, parse


class FakeReader:
    """A stub proposer returning a fixed set of frames (for policy tests)."""

    def __init__(self, *frames: Frame) -> None:
        self._frames = frames

    def read(self, sentence: str):
        return tuple(self._frames)


def make_reader():
    return LexicalReader(predicates={"calls"})


def make_registry():
    return SchemaRegistry([Schema("calls", (AGENT, PATIENT))])


# -- path (a): text -> Literal ---------------------------------------------
def test_sentence_to_literals_transitive():
    got = sentence_to_literals(make_reader(), make_registry(), "Alice calls Bob")
    assert got == (Literal(Atom("calls", (Const("alice"), Const("bob")))),)


def test_sentence_to_literal_unique():
    lit = sentence_to_literal(make_reader(), make_registry(), "Alice calls Bob")
    assert isinstance(lit, Literal) and not isinstance(lit, str)
    assert str(lit) == "(calls alice bob)"


def test_unnormalizable_frame_is_dropped():
    # reader proposes a frame whose roles do not match the schema -> abstain.
    reg = SchemaRegistry([Schema("calls", (AGENT,))])
    assert sentence_to_literals(make_reader(), reg, "Alice calls Bob") == ()


def test_reader_unknown_predicate_abstains():
    assert sentence_to_literals(make_reader(), make_registry(), "Alice flies") == ()
    assert sentence_to_literal(make_reader(), make_registry(), "Alice flies") is None


def test_multiple_readings_are_preserved_but_single_gate_abstains():
    reg = make_registry()
    reader = FakeReader(
        Frame("calls", ((AGENT, Const("a")), (PATIENT, Const("b")))),
        Frame("calls", ((AGENT, Const("b")), (PATIENT, Const("a")))),
    )
    readings = sentence_to_literals(reader, reg, "ignored")
    assert len(readings) == 2
    # ambiguous -> the strict single-reading gate abstains (never guesses).
    assert sentence_to_literal(reader, reg, "ignored") is None


# -- path (b): symbolic form -> logic --------------------------------------
def test_form_to_logic_atom_literal_rule():
    atom = form_to_logic(parse("(calls alice bob)")[0])
    assert atom == Atom("calls", (Const("alice"), Const("bob")))

    neg = form_to_logic(parse("(not (calls alice bob))")[0])
    assert neg == Literal(Atom("calls", (Const("alice"), Const("bob"))), negated=True)

    rule = form_to_logic(parse("(rule (r ?x) (calls ?x bob))")[0])
    assert isinstance(rule, Rule)


def test_form_to_logic_rejects_nesting():
    with pytest.raises((SexpError, TypeError)):
        form_to_logic(parse("(p (f a))")[0])


# -- Ingestor facade -------------------------------------------------------
def test_ingestor_literals_and_literal():
    ing = Ingestor(make_reader(), make_registry())
    assert str(ing.literal("Alice calls Bob")) == "(calls alice bob)"
    assert ing.literal("Alice flies") is None


def test_ingestor_logic_single_form():
    ing = Ingestor(make_reader(), make_registry())
    got = ing.logic("(calls alice bob)")
    assert isinstance(got, Atom) and str(got) == "(calls alice bob)"


def test_ingestor_logic_abstains_on_multiple_forms():
    ing = Ingestor(make_reader(), make_registry())
    assert ing.logic("(calls a b) (calls b a)") is None


def test_ingestor_logic_raises_on_malformed():
    ing = Ingestor(make_reader(), make_registry())
    with pytest.raises(SexpError):
        ing.logic("(calls a b")


def test_ingestor_emits_only_logic_not_text():
    ing = Ingestor(make_reader(), make_registry())
    for value in (ing.literal("Alice calls Bob"), ing.logic("(calls alice bob)")):
        assert isinstance(value, (Atom, Literal, Rule))