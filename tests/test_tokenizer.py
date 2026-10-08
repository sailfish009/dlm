"""Tests for the dependency-free byte tokenizer (v0.0003, learning branch L1)."""
from __future__ import annotations

from dlm import ByteTokenizer
from dlm.byte_tokenizer import BOS, EOS, OFFSET, PAD, SEP, VOCAB_SIZE


def test_vocab_and_special_ids():
    assert VOCAB_SIZE == 260
    assert (PAD, BOS, EOS, SEP) == (0, 1, 2, 3)
    assert OFFSET == 4


def test_encode_frames_and_roundtrips():
    t = ByteTokenizer(max_len=64)
    ids = t.encode("is alice a grandparent of carol")
    assert ids[0] == BOS and ids[-1] == EOS
    assert t.decode(ids) == "is alice a grandparent of carol"


def test_encode_pair_atom_start_is_correct():
    t = ByteTokenizer(max_len=128)
    sentence, atom = "is alice a grandparent of carol", "grandparent(alice,carol)"
    ids, start = t.encode_pair(sentence, atom)
    assert ids[0] == BOS and ids[-1] == EOS
    assert ids[start - 1] == SEP
    assert t.decode(ids[start:-1]) == atom


def test_truncation_keeps_eos_and_clamps():
    t = ByteTokenizer(max_len=8)
    ids = t.encode("x" * 100)
    assert len(ids) == 8 and ids[-1] == EOS


def test_pair_truncation_clamps_atom_start():
    t = ByteTokenizer(max_len=10)
    _, start = t.encode_pair("sentence that is far too long", "atom")
    assert 0 <= start <= 10


def test_pad_batch_shape_and_lengths():
    t = ByteTokenizer(max_len=32)
    ids, mask = t.pad_batch([t.encode("a"), t.encode("abcdef")])
    assert len(ids) == 2 and len(ids[0]) == len(ids[1])
    assert all(v == PAD for v in ids[0][mask[0]:])
    assert mask[0] < mask[1]


def test_collate_pairs_masks_only_the_atom():
    t = ByteTokenizer(max_len=64)
    ids, masks, starts = t.collate_pairs([("is alice a parent of bob", "parent(alice,bob)")])
    assert len(ids) == 1 and len(masks[0]) == len(ids[0])
    # everything before the atom is masked out; the atom span is kept
    assert all(m == 0.0 for m in masks[0][: starts[0]])
    assert all(m == 1.0 for m in masks[0][starts[0]:])


def test_bytes_are_bounded_to_vocab():
    t = ByteTokenizer(max_len=32)
    for s in ["café", "안녕하세요", "a(b,c)"]:
        ids = t.encode(s)
        assert all(0 <= i < VOCAB_SIZE for i in ids)
        assert t.decode(ids) == s