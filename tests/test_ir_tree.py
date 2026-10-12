"""Tests for the tree-native IR (dlm/ssl.py section 8): the symbol tree is IR."""
from __future__ import annotations

from dlm import Atom, Const, SexpError, Sym, dump, form_to_atom, parse
from dlm.ssl import (
    IR_HEAD,
    Frame,
    IrReader,
    IrSupervisor,
    aligned_examples,
    aligned_tree_examples,
    frame_from_form,
    frame_of,
    frame_sexp,
    ir_children,
    ir_form,
    ir_from_form,
    ir_get,
    ir_of,
    ir_paths,
    is_ir,
    macro_recall_at_1,
    reader_recall_at_1,
    reader_tree_features,
    tree_features,
)


class Fact:
    def __init__(self, pred, subj, obj):
        self.pred, self.subj, self.obj = pred, subj, obj


SENTENCES = [
    "Marie Curie was born in Warsaw and later moved to Paris.",
    "Warsaw is located in Poland.",
    "Paris is part of France.",
]


def _facts():
    return [
        Fact("birthplace", "marie_curie", "warsaw"),
        Fact("located_in", "warsaw", "poland"),
        Fact("part_of", "paris", "france"),
    ]


PREDS = ["birthplace", "located_in", "part_of", "occupation"]


# -- the tree IS the IR ----------------------------------------------------
def test_tree_round_trip_and_shape():
    f = frame_of("Marie Curie was born in Warsaw.", "marie_curie", "warsaw", "obj")
    t = ir_form(f.rel, f.subject, f.obj, f.order, f.name)
    assert is_ir(t)
    assert ir_from_form(t) == f
    assert parse(dump(t))[0] == t
    # frame serialisation and the canonical tree agree
    assert frame_from_form(t) == f


def test_ir_of_builds_the_same_tree_as_frame_sexp():
    t = ir_of("Warsaw is located in Poland.", "warsaw", "poland", "obj")
    assert is_ir(t)
    assert dump(t) == frame_sexp(frame_of("Warsaw is located in Poland.", "warsaw", "poland", "obj"))


def test_decoder_is_head_addressed_and_extensible():
    f = frame_of("Marie Curie was born in Warsaw.", "marie_curie", "warsaw", "obj")
    base = ir_form(f.rel, f.subject, f.obj, f.order, f.name)
    # append a novel head after <order>; decoding and features must not break
    extended = base + ((Sym("dep"), Sym("born")),)
    assert is_ir(extended)
    assert ir_from_form(extended) == f
    assert ir_get(extended, "dep") == (Sym("born"),)
    assert ir_children(extended, "rel") == (base[2],)
    feats = tree_features(extended)
    assert "node=ir/dep" in feats and "leaf=ir/dep=born" in feats


def test_tree_features_are_vocabulary_independent():
    # the walker knows nothing about rel/subj/obj -- it works on any Form tree
    generic = tree_features((Sym("blob"), (Sym("a"), Sym("x")), (Sym("b"), Sym("y"))))
    assert generic == ("node=blob", "node=blob/a", "leaf=blob/a=x", "node=blob/b", "leaf=blob/b=y")
    assert ir_paths((Sym("blob"), (Sym("a"), Sym("x")))) == (("blob",), ("blob", "a"))


def test_ir_tree_is_not_a_logic_form():
    f = frame_of("Marie Curie was born in Warsaw.", "marie_curie", "warsaw", "obj")
    t = ir_form(f.rel, f.subject, f.obj, f.order, f.name)
    # nested heads are not terms, so the kernel path rejects the IR tree
    try:
        form_to_atom(t)
    except SexpError:
        pass
    else:  # pragma: no cover
        raise AssertionError("IR tree must never be read as an atom")
    assert not is_ir((IR_HEAD,))            # bare head is not a frame
    assert not is_ir((IR_HEAD, Sym("-")))   # missing rel/subj/obj


# -- learning reads the tree ----------------------------------------------
def test_reader_learns_on_the_tree():
    examples = aligned_tree_examples(SENTENCES, _facts(), PREDS)
    assert examples and all(is_ir(t) for t, _, _ in examples)
    reader = IrReader(features=reader_tree_features)
    before = reader_recall_at_1(reader, examples)
    IrSupervisor(reader=reader).fit_reader(examples, epochs=30, seed=0)
    after = reader_recall_at_1(reader, examples)
    assert after > before
    assert macro_recall_at_1(reader, examples) == 1.0


def test_tree_and_view_examples_agree():
    trees = aligned_tree_examples(SENTENCES, _facts(), PREDS)
    views = aligned_examples(SENTENCES, _facts(), PREDS)
    assert len(trees) == len(views)
    for (tree, tpos, tcand), (view, vpos, vcand) in zip(trees, views):
        assert ir_from_form(tree) == view
        assert tpos == vpos and tcand == vcand


def test_tree_learning_is_deterministic():
    r1 = IrReader(features=reader_tree_features)
    r2 = IrReader(features=reader_tree_features)
    IrSupervisor(reader=r1).fit_reader(aligned_tree_examples(SENTENCES, _facts(), PREDS), epochs=20, seed=7)
    IrSupervisor(reader=r2).fit_reader(aligned_tree_examples(SENTENCES, _facts(), PREDS), epochs=20, seed=7)
    assert r1.ranker.weights == r2.ranker.weights


def test_tree_scramble_control_does_not_learn_the_map():
    examples = aligned_tree_examples(SENTENCES, _facts(), PREDS)
    reader = IrReader(features=reader_tree_features)
    IrSupervisor(reader=reader).fit_reader(examples, epochs=30, seed=0, scramble=True)
    assert macro_recall_at_1(reader, examples) < 1.0