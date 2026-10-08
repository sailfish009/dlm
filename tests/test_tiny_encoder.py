"""Tests for the vendored tiny encoder (v0.0003, learning branch L2)."""
from __future__ import annotations

import pytest
import torch

from dlm import ByteTokenizer, TinyEncoderConfig, build_encoder
from dlm.tiny_encoder import TinyEncoder


@pytest.fixture()
def tok() -> ByteTokenizer:
    return ByteTokenizer(max_len=64)


def _batch(tok, pairs):
    ids, _ = tok.pad_batch([tok.encode_pair(s, a)[0] for s, a in pairs])
    ids = torch.tensor(ids)
    return ids, ids.ne(0).long()


def _pairs():
    return [
        ("is alice a parent of bob", "parent(alice,bob)"),
        ("is bob a grandparent of dave?", "grandparent(bob,dave)"),
    ]


def test_geometry_matches_meowllm():
    cfg = TinyEncoderConfig()
    assert (cfg.d_model, cfg.n_layers, cfg.n_heads, cfg.ffn_hidden) == (256, 4, 4, 640)
    assert cfg.vocab_size == 260 and cfg.causal is False


def test_encoder_is_tiny_and_sized_to_tokenizer(tok):
    enc = build_encoder(tok)
    assert enc.cfg.vocab_size == tok.vocab_size
    assert enc.cfg.max_seq_len == tok.max_len
    assert 2_500_000 < enc.num_parameters() < 3_500_000


def test_forward_returns_pooled_features(tok):
    enc = build_encoder(tok).eval()
    ids, mask = _batch(tok, _pairs())
    with torch.no_grad():
        feats = enc(ids, mask)
    assert feats.shape == (2, 256)
    assert torch.isfinite(feats).all()


@pytest.mark.parametrize("kw", [
    dict(pool="mean", causal=False),
    dict(pool="last", causal=False),
    dict(pool="last", causal=True),
])
def test_padding_does_not_change_features(tok, kw):
    torch.manual_seed(0)
    enc = build_encoder(tok, **kw).eval()
    ids, mask = _batch(tok, _pairs())
    with torch.no_grad():
        a = enc(ids, mask)
        b = enc(torch.nn.functional.pad(ids, (0, 8), value=0),
                torch.nn.functional.pad(mask, (0, 8), value=0))
    assert (a - b).abs().max().item() < 1e-4


def test_pooling_and_causality_actually_change_output(tok):
    torch.manual_seed(0)
    ids, mask = _batch(tok, _pairs())
    with torch.no_grad():
        mean = build_encoder(tok, pool="mean").eval()(ids, mask)
        last = build_encoder(tok, pool="last").eval()(ids, mask)
        causal = build_encoder(tok, pool="last", causal=True).eval()(ids, mask)
    assert not torch.allclose(mean, last)
    assert not torch.allclose(last, causal)


def test_freeze_stops_gradients_and_unfreeze_restores(tok):
    enc = build_encoder(tok)
    ids, mask = _batch(tok, _pairs())
    enc.freeze()
    assert all(not p.requires_grad for p in enc.parameters())
    feats = enc(ids, mask)
    assert not feats.requires_grad  # nothing to backprop through
    assert all(p.grad is None for p in enc.parameters())
    enc.unfreeze()
    enc(ids, mask).sum().backward()
    assert enc.tok_emb.weight.grad is not None


def test_seq_length_guard(tok):
    enc = build_encoder(tok)
    with pytest.raises(AssertionError):
        enc(torch.zeros(1, tok.max_len + 1, dtype=torch.long))


def test_eval_is_deterministic(tok):
    torch.manual_seed(0)
    enc = build_encoder(tok).eval()
    ids, mask = _batch(tok, _pairs())
    with torch.no_grad():
        assert torch.equal(enc(ids, mask), enc(ids, mask))