"""Tests for the closed-subset reader (seam B)."""
from __future__ import annotations

from dlm.logic import Const, Frame, Schema, SchemaRegistry
from dlm.reader import (
    AGENT,
    FIGURE,
    GROUND,
    PATIENT,
    SUBJECT,
    LexicalReader,
    Reader,
    tokenize,
)


def R(*preds):
    return LexicalReader(predicates=preds)


# -- tokenization ----------------------------------------------------------
def test_tokenize_lowercases_and_drops_determiners_and_punctuation():
    assert tokenize("The Cat sees A dog.") == ("cat", "sees", "dog")


def test_tokenize_expands_nt_and_possessive():
    assert tokenize("Alice doesn't like Bob's dog") == ("alice", "does", "not", "like", "bob", "dog")


# -- patterns --------------------------------------------------------------
def test_intransitive():
    assert R("runs").read("Alice runs") == (Frame("runs", ((AGENT, Const("alice")),)),)


def test_transitive_svo_is_role_labelled():
    got = R("calls").read("Alice calls Bob")
    assert got == (Frame("calls", ((AGENT, Const("alice")), (PATIENT, Const("bob")))),)


def test_copula_preposition_promotes_to_binary_predicate():
    got = R().read("The cat is on the mat")
    assert got == (Frame("on", ((FIGURE, Const("cat")), (GROUND, Const("mat")))),)


def test_copula_noun_predication_is_unary():
    got = R("person").read("Alice is a person")
    assert got == (Frame("person", ((SUBJECT, Const("alice")),)),)


def test_negation_sets_sign_on_every_frame():
    # after "does", the verb is its bare form "call" (an auxiliary is dropped)
    got = R("call").read("Alice does not call Bob")
    assert got == (
        Frame("call", ((AGENT, Const("alice")), (PATIENT, Const("bob"))), True),
    )


# -- abstain, never guess --------------------------------------------------
def test_unknown_predicate_abstains():
    # "flies" is not in the lexicon -> the sentence is unreadable, not guessed.
    assert R("calls").read("Alice flies") == ()


def test_unknown_shape_abstains():
    assert R("calls").read("Alice calls Bob loudly today") == ()


def test_empty_input_abstains():
    assert R("calls").read("   ") == ()


def test_identity_copula_abstains():
    # E COP E is deliberately outside the fragment (would need identity/eq).
    assert R("calls").read("Alice is Bob") == ()


# -- ambiguity is preserved ------------------------------------------------
def test_ambiguous_readings_are_all_returned():
    # "runs" is both a verb and a (noun) predicate; "Alice runs" is
    # intransitive, "Alice is runs" would be unary. A single token that is both
    # a copula and a predicate yields both readings.
    reader = LexicalReader(predicates={"runs", "is"})
    got = reader.read("Alice is runs")
    # E COP V -> runs(subject=alice)  AND  E V E is not matched (n=3, tokens[1]='is' in COPULAS)
    assert got == (Frame("runs", ((SUBJECT, Const("alice")),)),)


# -- protocol & registry integration --------------------------------------
def test_lexical_reader_satisfies_reader_protocol():
    assert isinstance(R("calls"), Reader)


def test_read_then_normalize_yields_a_literal():
    registry = SchemaRegistry(
        [
            Schema("calls", (AGENT, PATIENT)),
            Schema("on", (FIGURE, GROUND)),
        ]
    )
    frames = R("calls").read("Alice calls Bob")
    literals = [lit for f in frames if (lit := registry.normalize(f)) is not None]
    assert [str(x) for x in literals] == ["(calls alice bob)"]

    pp = R().read("The cat is on the mat")
    lits = [lit for f in pp if (lit := registry.normalize(f)) is not None]
    assert [str(x) for x in lits] == ["(on cat mat)"]


def test_normalize_abstains_when_schema_roles_do_not_match():
    registry = SchemaRegistry([Schema("calls", (AGENT,))])  # missing patient role
    frames = R("calls").read("Alice calls Bob")
    assert all(registry.normalize(f) is None for f in frames)