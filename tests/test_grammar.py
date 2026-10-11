"""Tests for the data-driven rewrite grammar (module 20)."""
from __future__ import annotations

import pytest

from dlm.grammar import (
    DEFAULT_RULES,
    Derivation,
    GrammarReader,
    Reading,
    RewriteRule,
    verify_reading,
)
from dlm.logic import Const
from dlm.reader import LexicalReader

PREDS = {"calls", "likes", "sleeps", "president", "knows"}

BATTERY = [
    "alice calls bob",
    "alice calls",
    "alice is president",
    "alice is in tokyo",
    "alice is not in tokyo",
    "alice may call bob",
    "the cat sleeps",
    "zzz qqq",
    "",
]


def test_default_grammar_matches_lexical_reader():
    grammar = GrammarReader(PREDS)
    lexical = LexicalReader(PREDS)
    for sentence in BATTERY:
        assert grammar.read(sentence) == lexical.read(sentence), sentence


def test_unknown_word_abstains():
    grammar = GrammarReader(PREDS)
    assert grammar.read("zzz qqq") == ()
    assert grammar.read("alice flurbs bob") == ()


def test_read_with_proof_replays():
    grammar = GrammarReader(PREDS)
    readings = grammar.read_with_proof("alice calls bob")
    assert len(readings) == 1
    reading = readings[0]
    assert isinstance(reading, Reading) and isinstance(reading.derivation, Derivation)
    assert reading.frame.pred == "calls"
    assert verify_reading(grammar, "alice calls bob", reading) is True
    # A tampered frame is rejected: the derivation no longer reproduces it.
    from dlm.logic import Frame

    tampered = Reading(Frame("likes", reading.frame.slots), reading.derivation)
    assert verify_reading(grammar, "alice calls bob", tampered) is False
    assert verify_reading(grammar, "bob calls alice", reading) is False


def test_negation_is_a_flag_not_a_predicate():
    grammar = GrammarReader(PREDS)
    (frame,) = grammar.read("alice is not in tokyo")
    assert frame.negated is True
    assert frame.pred == "in"
    assert dict(frame.slots)["figure"] == Const("alice")


def test_grammar_is_data_so_coverage_is_extension():
    grammar = GrammarReader(PREDS)
    assert grammar.read("alice knows in tokyo") == ()
    grammar.add_rule(
        RewriteRule(
            "verb_prep",
            ("?e0:ent", "?v:pred", "?p:prep", "?e1:ent"),
            "?v",
            (("agent", "?e0"), ("patient", "?e1")),
        )
    )
    (frame,) = grammar.read("alice knows in tokyo")
    assert frame.pred == "knows"
    assert dict(frame.slots)["patient"] == Const("tokyo")


def test_ambiguity_is_preserved_not_resolved():
    rules = DEFAULT_RULES + (
        RewriteRule(
            "transitive_swapped",
            ("?e0:ent", "?v:pred", "?e1:ent"),
            "?v",
            (("agent", "?e1"), ("patient", "?e0")),
        ),
    )
    grammar = GrammarReader(PREDS, rules=rules)
    frames = grammar.read("alice calls bob")
    assert len(frames) == 2
    preds = {f.pred for f in frames}
    assert preds == {"calls"}


def test_rule_validation():
    with pytest.raises(ValueError):
        RewriteRule("empty", (), "?v", (("agent", "?e0"),))
    with pytest.raises(ValueError):
        RewriteRule("badcat", ("?e0:widget", "?v:pred"), "?v", (("agent", "?e0"),))
    with pytest.raises(ValueError):
        RewriteRule("literalhead", ("?e0:ent", "?v:pred"), "calls", (("agent", "?e0"),))
    with pytest.raises(ValueError):
        RewriteRule("unbound", ("?e0:ent", "?v:pred"), "?v", (("agent", "?other"),))
    with pytest.raises(ValueError):
        RewriteRule("noroles", ("?e0:ent", "?v:pred"), "?v", ())