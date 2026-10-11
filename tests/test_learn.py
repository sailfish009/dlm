"""Tests for the trainable reader (dlm.learn) -- the seam-B trainability probe."""
from __future__ import annotations

import pytest

from dlm.learn import (
    NEG,
    OTHER,
    PRED,
    AveragedPerceptron,
    LearnedReader,
    ReaderExample,
    build_pred_lexicon,
    token_features,
    train_reader,
    train_tagger,
)
from dlm.logic import Const, Frame, Schema, SchemaRegistry
from dlm.reader import AGENT, PATIENT, SUBJECT


# -- features ---------------------------------------------------------------
def test_token_features_has_identity_and_context():
    toks = ("alice", "calls", "bob")
    feats = token_features(toks, 1)
    assert "w=calls" in feats
    assert "w-1=alice" in feats
    assert "w+1=bob" in feats
    assert "pos=1" in feats
    assert "bias" in feats


def test_token_features_are_position_aware():
    toks = ("alice", "calls", "bob")
    assert token_features(toks, 0) != token_features(toks, 2)


# -- the perceptron ---------------------------------------------------------
def test_perceptron_learns_a_separable_toy():
    model = AveragedPerceptron(("x", "y"))
    data = [(("a",), "x"), (("b",), "y")]
    for _ in range(5):
        for feats, gold in data:
            pred = model.predict(feats)
            if pred != gold:
                model.update(feats, gold, pred)
            model.tick()
    model.finalize()
    assert model.predict(("a",)) == "x"
    assert model.predict(("b",)) == "y"


def test_finalize_is_idempotent_for_predictions():
    model = AveragedPerceptron(("x", "y"))
    for _ in range(5):
        for feats, gold in [(("a",), "x"), (("b",), "y")]:
            pred = model.predict(feats)
            if pred != gold:
                model.update(feats, gold, pred)
            model.tick()
    model.finalize()
    before = (model.predict(("a",)), model.predict(("b",)))
    model.finalize()
    assert (model.predict(("a",)), model.predict(("b",))) == before


# -- Lexicon ----------------------------------------------------------------
def test_build_pred_lexicon_maps_surface_to_canonical():
    ex = ReaderExample(
        "alice calls bob",
        Frame("call", ((AGENT, Const("alice")), (PATIENT, Const("bob")))),
        (AGENT, PRED, PATIENT),
    )
    assert build_pred_lexicon([ex]) == {"calls": "call"}


# -- LearnedReader decode: abstention paths ---------------------------------
class _StubTagger:
    def __init__(self, tags):
        self._tags = tags

    def predict_all(self, tokens):
        return tuple(self._tags[: len(tokens)])


def _reader(tags, lexicon):
    return LearnedReader(tagger=_StubTagger(tags), lexicon=lexicon)


def test_one_pred_token_builds_a_frame():
    r = _reader([AGENT, PRED, PATIENT], {"calls": "call"})
    frames = r.read("alice calls bob")
    assert len(frames) == 1
    assert frames[0].pred == "call"


def test_no_pred_token_abstains():
    r = _reader([AGENT, OTHER, PATIENT], {"calls": "call"})
    assert r.read("alice calls bob") == ()


def test_two_pred_tokens_abstain():
    r = _reader([PRED, PRED, PATIENT], {"calls": "call", "alice": "alice"})
    assert r.read("alice calls bob") == ()


def test_unknown_predicate_surface_abstains():
    r = _reader([AGENT, PRED, PATIENT], {"calls": "call"})
    assert r.read("alice hurks bob") == ()


def test_duplicate_role_abstains():
    r = _reader([AGENT, PRED, AGENT], {"calls": "call"})
    assert r.read("alice calls bob") == ()


def test_negation_is_carried_into_the_frame():
    r = _reader([SUBJECT, NEG, PRED], {"happy": "happy"})
    frames = r.read("alice not happy")
    assert frames and frames[0].negated is True


def test_empty_sentence_abstains():
    r = _reader([], {})
    assert r.read("") == ()


# -- end-to-end training + the trust boundary -------------------------------
def _corpus():
    return [
        ReaderExample(
            "alice calls bob",
            Frame("call", ((AGENT, Const("alice")), (PATIENT, Const("bob")))),
            (AGENT, PRED, PATIENT),
        ),
        ReaderExample(
            "bob calls carol",
            Frame("call", ((AGENT, Const("bob")), (PATIENT, Const("carol")))),
            (AGENT, PRED, PATIENT),
        ),
        ReaderExample(
            "carol likes dave",
            Frame("like", ((AGENT, Const("carol")), (PATIENT, Const("dave")))),
            (AGENT, PRED, PATIENT),
        ),
        ReaderExample(
            "alice is happy",
            Frame("happy", ((SUBJECT, Const("alice")),)),
            (SUBJECT, OTHER, PRED),
        ),
        ReaderExample(
            "bob is happy",
            Frame("happy", ((SUBJECT, Const("bob")),)),
            (SUBJECT, OTHER, PRED),
        ),
        ReaderExample(
            "carol is clever",
            Frame("clever", ((SUBJECT, Const("carol")),)),
            (SUBJECT, OTHER, PRED),
        ),
    ]


def test_learned_reader_reads_training_patterns_through_normalize():
    reg = SchemaRegistry()
    reg.add(Schema("call", (AGENT, PATIENT)))
    reg.add(Schema("like", (AGENT, PATIENT)))
    reg.add(Schema("happy", (SUBJECT,)))
    reg.add(Schema("clever", (SUBJECT,)))

    reader = train_reader(_corpus(), epochs=20, seed=0)
    assert reg.normalize(reader.read("alice calls bob")[0]) is not None
    assert reg.normalize(reader.read("carol is clever")[0]) is not None


def test_train_reader_generalizes_to_unseen_entities():
    reg = SchemaRegistry()
    reg.add(Schema("call", (AGENT, PATIENT)))
    reg.add(Schema("happy", (SUBJECT,)))

    reader = train_reader(_corpus(), epochs=20, seed=0)
    got = reader.read("dave calls erin")
    assert len(got) == 1
    lit = reg.normalize(got[0])
    assert lit is not None
    assert str(lit) == "(call dave erin)"


def test_train_reader_abstains_on_unseen_predicate_word():
    reg = SchemaRegistry()
    reg.add(Schema("call", (AGENT, PATIENT)))
    reader = train_reader(_corpus(), epochs=20, seed=0)
    # "hurks" was never seen, so the predicate lexicon has no entry.
    assert reader.read("alice hurks bob") == ()


def test_train_tagger_output_is_a_tagger():
    tagger = train_tagger(_corpus(), epochs=5, seed=0)
    tags = tagger.predict_all(("alice", "calls", "bob"))
    assert len(tags) == 3
    assert tags[1] == PRED