"""Tests for the IR-SSL layer (dlm/ssl.py): frames, features, learning."""
from __future__ import annotations

from dlm import Atom, Const
from dlm.ssl import (
    FRAMES,
    MASK,
    Frame,
    IrReader,
    IrRealizer,
    IrSupervisor,
    aligned_examples,
    frame_from_sexp,
    frame_of,
    frame_sexp,
    majority_baseline,
    macro_recall_at_1,
    reader_recall_at_1,
    render,
    roundtrip_rate,
    supporting_sentence,
)


class Fact:
    def __init__(self, pred, subj, obj):
        self.pred, self.subj, self.obj = pred, subj, obj


SENTENCES = [
    "Marie Curie was born in Warsaw and later moved to Paris.",
    "Warsaw is located in Poland.",
    "Paris is part of France.",
]


def _examples(mask: str = "obj"):
    facts = [
        Fact("birthplace", "marie_curie", "warsaw"),
        Fact("located_in", "warsaw", "poland"),
        Fact("part_of", "paris", "france"),
    ]
    preds = ["birthplace", "located_in", "part_of", "occupation"]
    return aligned_examples(SENTENCES, facts, preds, mask=mask), preds


# -- IR --------------------------------------------------------------------
def test_frame_is_predicate_agnostic_and_drops_arguments():
    f = frame_of("Marie Curie was born in Warsaw.", "marie_curie", "warsaw", "obj")
    assert f.rel == ("born",)
    assert f.subject == ("marie", "curie")
    assert f.obj == (MASK,)
    assert "warsaw" not in f.rel and "marie" not in f.rel


def test_frame_masks_and_deidentifies():
    f = frame_of("Marie Curie was born in Warsaw.", "marie_curie", "warsaw", "")
    assert f.subject_seen and f.object_seen
    assert f.mask_object().obj == (MASK,)
    assert not f.mask_object().object_seen
    d = f.deidentify()
    assert d.subject == (MASK,) and d.obj == (MASK,)
    assert not d.subject_seen and not d.object_seen


def test_frame_order_records_mention_order():
    f = frame_of("Warsaw is the birthplace of Marie Curie.", "marie_curie", "warsaw", "obj")
    assert f.order == 1  # object mentioned before subject


def test_frame_form_round_trip():
    for f in (
        Frame(("born",), ("marie", "curie"), (MASK,), 0),
        Frame(("located", "in"), (), (), 1, "located_in"),
        FRAMES[0],
    ):
        assert frame_from_sexp(frame_sexp(f)) == f


def test_render_uses_frame_cue_phrase():
    a = Atom("birthplace", (Const("marie_curie"), Const("warsaw")))
    assert render(FRAMES[4], a) == "marie curie born in warsaw"


# -- alignment -------------------------------------------------------------
def test_supporting_sentence_prefers_mentioning_sentence():
    assert supporting_sentence(SENTENCES, "marie_curie", "warsaw").startswith("Marie Curie")
    assert supporting_sentence(SENTENCES, "paris", "france").startswith("Paris")
    assert supporting_sentence(["nothing here"], "marie_curie", "warsaw") is None


def test_aligned_examples_are_masked_and_candidate_complete():
    examples, preds = _examples()
    assert examples
    for frame, positives, candidates in examples:
        assert len(positives) == 1
        assert len(candidates) == len(preds)
        assert frame.obj == (MASK,)  # object identity removed from the IR
        assert positives[0] in candidates


# -- learning --------------------------------------------------------------
def test_reader_learns_cue_to_predicate():
    examples, _ = _examples()
    reader = IrReader()
    before = reader_recall_at_1(reader, examples)
    IrSupervisor(reader=reader).fit_reader(examples, epochs=30, seed=0)
    assert reader_recall_at_1(reader, examples) > before
    assert macro_recall_at_1(reader, examples) == 1.0
    feats = dict(reader.top_features(12))
    assert feats.get("pred=birthplace&cue=born", 0.0) > 0


def test_scramble_control_does_not_learn_the_map():
    examples, _ = _examples()
    reader = IrReader()
    IrSupervisor(reader=reader).fit_reader(examples, epochs=30, seed=0, scramble=True)
    # A shuffled-label arm must not reach the true per-predicate recall.
    assert macro_recall_at_1(reader, examples) < 1.0


def test_majority_baseline_and_deidentified_view():
    examples, _ = _examples()
    assert 0.0 < majority_baseline(examples) <= 1.0
    deid, _ = _examples(mask="all")
    reader = IrReader()
    IrSupervisor(reader=reader).fit_reader(deid, epochs=30, seed=0)
    assert macro_recall_at_1(reader, deid) == 1.0


def test_determinism():
    a, _ = _examples()
    b, _ = _examples()
    r1, r2 = IrReader(), IrReader()
    IrSupervisor(reader=r1).fit_reader(a, epochs=20, seed=7)
    IrSupervisor(reader=r2).fit_reader(b, epochs=20, seed=7)
    assert r1.ranker.weights == r2.ranker.weights


def test_realizer_roundtrip_after_reading_learns():
    examples, preds = _examples()
    reader = IrReader()
    IrSupervisor(reader=reader).fit_reader(examples, epochs=40, seed=0)
    realizer = IrRealizer()
    IrSupervisor(reader=reader, realizer=realizer).fit_realizer(
        [Atom("birthplace", (Const("marie_curie"), Const("warsaw")))], predicates=preds, epochs=20
    )
    assert roundtrip_rate(realizer, reader, [examples[0][1][0]], preds, k=len(realizer.frames)) == 1.0