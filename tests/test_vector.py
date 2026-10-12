"""Tests for dlm.vector -- the grounded representation vector (v0.0026)."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

import dlm
from dlm import SexpError
from dlm.ssl import ir_form, tree_features
from dlm.vector import (
    ROLES,
    Basis,
    Symbol,
    SymbolVector,
    bundle,
    decode,
    encode,
    restrict,
    tree_vector,
    vector_features,
    vector_form,
    vector_from_form,
    vector_from_sexp,
    vector_sexp,
    vector_symbols,
    vector_tree,
)

ROOT = Path(__file__).resolve().parents[1]

TREES = [
    ir_form(("based", "at"), ("alan", "turing"), ("london",), 0, "f1"),
    ir_form(("worked", "as"), ("alan", "turing"), ("mathematician",), 1, "f2"),
    ir_form((), (), (), 0, ""),
    ir_form(("born", "in"), ("ada",), ("london",), 0, "f3") + ((dlm.Sym("dep"), dlm.Sym("nsubj")),),
]


def test_symbol_is_named_and_grounded():
    s = Symbol("rel", 0, "born")
    assert s.key() == "rel[0]=born" and str(s) == "rel[0]=born"
    assert Symbol("name", 0, "f1").key() == "name=f1"
    assert Symbol("order", 0, "1").key() == "order=1"


def test_symbol_rejects_bad_role_index_token():
    with pytest.raises(ValueError):
        Symbol("nope", 0, "x")
    with pytest.raises(ValueError):
        Symbol("rel", -1, "x")
    with pytest.raises(TypeError):
        Symbol("rel", 0, 5)  # type: ignore[arg-type]


def test_vector_is_sorted_and_readable():
    v = tree_vector(TREES[0])
    assert vector_symbols(v) == (
        "name=f1", "rel[0]=based", "rel[1]=at",
        "subj[0]=alan", "subj[1]=turing", "obj[0]=london", "order=0",
    )
    assert v.roles() == ("name", "rel", "subj", "obj", "order")
    assert v.tokens("rel") == ("based", "at")


def test_roundtrip_is_exact_for_every_tree():
    for t in TREES:
        assert vector_tree(tree_vector(t)) == t


def test_roundtrip_preserves_model_features():
    for t in TREES:
        assert tree_features(vector_tree(tree_vector(t))) == tree_features(t)


def test_distinct_trees_give_distinct_vectors():
    vs = [tree_vector(t) for t in TREES]
    assert len({v.explain() for v in vs}) == len(TREES)


def test_vector_features_are_grounded_and_have_lengths():
    feats = set(vector_features(tree_vector(TREES[1])))
    assert "rel=worked" in feats and "subj=alan" in feats
    assert "rel_len=2" in feats and "obj_len=1" in feats


def test_bundle_superposes_and_restrict_unbinds():
    a, b = tree_vector(TREES[0]), tree_vector(TREES[1])
    both = bundle(a, b)
    assert len(both) == len(a) + len(b) - 2  # name differs, rel[0] differs; but alan shared
    assert set(restrict(a, "rel").tokens()) == {"based", "at"}
    # shared symbols merge and their weights add
    sub = both.restrict("subj")
    assert sub.tokens() == ("alan", "turing")
    assert sub.weights == (2.0, 2.0)


def test_sexp_roundtrip_and_bad_form():
    v = tree_vector(TREES[3])
    assert vector_from_sexp(vector_sexp(v)) == v
    assert vector_from_form(vector_form(v)) == v
    with pytest.raises(SexpError):
        vector_from_form((dlm.Sym("bogus"),))
    with pytest.raises(SexpError):
        vector_from_sexp("(vec) (vec)")
    with pytest.raises(SexpError):
        tree_vector(("not-an-ir",))


def test_basis_encode_decode_roundtrip_and_contains():
    vs = [tree_vector(t) for t in TREES]
    basis = Basis.of(vs)
    assert len(basis) <= sum(len(v) for v in vs)
    assert all(isinstance(s, Symbol) for s in basis.symbols)
    for v in vs:
        assert decode(encode(v, basis), basis) == v
    outside = tree_vector(ir_form(("never", "seen"), ("zoe",), ("x",), 0, "zz"))
    with pytest.raises(SexpError):
        encode(outside, basis)
    with pytest.raises(SexpError):
        decode((1.0,), basis)


def test_symbol_vector_rejects_bad_weight_length():
    with pytest.raises(ValueError):
        SymbolVector((Symbol("order", 0, "0"),), (1.0, 2.0))


def test_trust_boundary_core_never_imports_vector():
    src = (ROOT / "dlm" / "__init__.py").read_text()
    tree = ast.parse(src)
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods.append(node.module or "")
    assert not any("vector" in (m or "") for m in mods), mods
    assert not hasattr(dlm, "SymbolVector")
    assert not hasattr(dlm, "tree_vector")
