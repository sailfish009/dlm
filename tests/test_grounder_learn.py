"""Tests for learned grounding (v0.0003, learning branch L3)."""
from __future__ import annotations

import torch
import pytest

from dlm import ByteTokenizer
from dlm.grounding import GrammarGrounder, Pattern
from dlm.grounder_learn import (
    AtomIndex,
    CharNgramGrounder,
    LearnedGrounder,
    ProjectionHead,
    pattern_split,
    synthesize_pairs,
)
from dlm.interpreter import parse_atom

canon = lambda s: str(parse_atom(s))  # noqa: E731


# ---------------------------------------------------------------------------
# head + index
# ---------------------------------------------------------------------------

def test_projection_head_is_unit_norm_with_positive_scale():
    h = ProjectionHead(d_model=16, proj_dim=8)
    z = h(torch.randn(5, 16))
    assert z.shape == (5, 8)
    assert torch.allclose(z.norm(dim=-1), torch.ones(5), atol=1e-5)
    assert h.scale().item() > 0


def test_info_nce_group_masking_removes_same_atom_negatives():
    torch.manual_seed(0)
    g = LearnedGrounder(ByteTokenizer(max_len=32), proj_dim=8, seed=0)
    z_s = g.head(torch.randn(4, g.encoder.cfg.d_model))
    z_a = g.head(torch.randn(4, g.encoder.cfg.d_model))
    ids = torch.tensor([0, 0, 1, 1])
    plain = g.info_nce(z_s, z_a)
    masked = g.info_nce(z_s, z_a, ids)
    assert torch.isfinite(plain) and torch.isfinite(masked)
    assert not torch.allclose(plain, masked)


def test_atom_index_canonicalises_spacing():
    idx = AtomIndex(["parent(alice,bob)", "parent(bob,carol)"])
    assert len(idx) == 2
    assert idx.id_of("parent(alice, bob)") == idx.id_of("parent(alice,bob)")
    assert idx.id_of(parse_atom("parent(bob,carol)")) == 1
    with pytest.raises(KeyError):
        idx.id_of("nope(alice,bob)")


# ---------------------------------------------------------------------------
# data bootstrap
# ---------------------------------------------------------------------------

PHRASES = [
    Pattern("is {x} a parent of {y}", "parent({x},{y})"),
    Pattern("{x} is a parent of {y}", "parent({x},{y})"),
    Pattern("does {x} parent {y}", "parent({x},{y})"),
    Pattern("is {x} an ancestor of {y}", "ancestor({x},{y})"),
    Pattern("{x} is an ancestor of {y}", "ancestor({x},{y})"),
]


def test_synthesize_pairs_are_valid_and_punctuated():
    pairs = synthesize_pairs(PHRASES, ("alice", "bob"), seed=0)
    assert len(pairs) == 5 * 4  # 5 phrases x 2^2 combinations
    for sentence, atom in pairs:
        assert parse_atom(atom)
        assert sentence.endswith("?") or sentence.endswith(".")


def test_pattern_split_keeps_every_relation_in_both_halves():
    train, held = pattern_split(PHRASES, heldout_frac=0.5, seed=0)
    assert {p.template for p in train} == {p.template for p in held}
    assert {p.phrase for p in train}.isdisjoint({p.phrase for p in held})
    assert all(len([p for p in held if p.template == t]) >= 1 for t in {p.template for p in held})


# ---------------------------------------------------------------------------
# lexical control
# ---------------------------------------------------------------------------

def test_char_ngram_grounder_memorises_and_abstains():
    pairs = synthesize_pairs(PHRASES, ("alice", "bob"), seed=0)
    g = CharNgramGrounder(pairs)
    s, a = pairs[0]
    out = g.ground(s, threshold=0.5)
    assert out.ok and canon(str(out.atom)) == canon(a)
    assert not g.ground("is berlin the capital of germany", threshold=0.9).ok


# ---------------------------------------------------------------------------
# learned grounder: memorisation + abstain + persistence
# ---------------------------------------------------------------------------

TRAIN_PHRASES = PHRASES[:2] + PHRASES[3:5]  # 2 phrases per relation


@pytest.fixture(scope="module")
def trained():
    torch.manual_seed(0)
    pairs = synthesize_pairs(TRAIN_PHRASES, ("alice", "bob"), seed=0)
    g = LearnedGrounder(ByteTokenizer(max_len=40), proj_dim=16, seed=0)
    report = g.fit(pairs, epochs=400, lr=8e-3, seed=0)
    return g, pairs, report


def test_fit_populates_index_and_lowers_loss(trained):
    _, pairs, report = trained
    assert report.n_pairs == len(pairs) == 16
    assert report.n_atoms == 8  # 2 relations x 4 ordered entity pairs
    assert report.history[-1] < report.history[0]
    assert report.n_trainable_params > 0


def test_grounder_memorises_training_pairs(trained):
    g, pairs, _ = trained
    out = g.ground_batch([s for s, _ in pairs], threshold=0.5)
    correct = sum(o.ok and canon(str(o.atom)) == canon(a) for o, (_, a) in zip(out, pairs))
    assert correct == len(pairs)


def test_grounder_abstains_above_reachable_threshold(trained):
    g, pairs, _ = trained
    out = g.ground(pairs[0][0], threshold=1.5)  # cosine <= 1 always
    assert not out.ok and "threshold" in out.reason


def test_grounder_similarities_shape(trained):
    g, pairs, _ = trained
    sims = g.similarities([s for s, _ in pairs[:3]])
    assert sims.shape == (3, len(g.index))


def test_save_load_roundtrip(trained, tmp_path):
    g, pairs, _ = trained
    path = str(tmp_path / "grounder.pt")
    g.save(path)
    g2 = LearnedGrounder.load(path)
    a = g.ground(pairs[0][0], threshold=0.5)
    b = g2.ground(pairs[0][0], threshold=0.5)
    assert a.ok and b.ok and canon(str(a.atom)) == canon(str(b.atom))