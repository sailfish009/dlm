"""Dependency-free byte-level tokenizer for the DLM NL front-end.

MeowLLM ships an HF ``tokenizers`` BPE file, but ``tokenizers`` is not installed
on this host. To stay self-contained we use a byte-level tokenizer: the vocab is
4 special tokens plus the 256 bytes. It needs no training, is reversible, and is
identical for sentences and predicate atoms (both are ASCII here).

    PAD=0  BOS=1  EOS=2  SEP=3  ; byte b -> 4 + b  (vocab_size = 260)

Messages are framed as ``<bos> sentence <sep> atom <eos>`` so a single encoder
can consume either side of the contrastive pair.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

PAD, BOS, EOS, SEP = 0, 1, 2, 3
OFFSET = 4
VOCAB_SIZE = OFFSET + 256

__all__ = ["ByteTokenizer", "PAD", "BOS", "EOS", "SEP", "OFFSET", "VOCAB_SIZE"]


@dataclass
class ByteTokenizer:
    """Reversible UTF-8 byte tokenizer with fixed special ids."""

    max_len: int = 256
    pad_id: int = PAD
    bos_id: int = BOS
    eos_id: int = EOS
    sep_id: int = SEP

    @property
    def vocab_size(self) -> int:
        return VOCAB_SIZE

    # -- single sequence ---------------------------------------------------
    def encode(self, text: str, *, add_special: bool = True) -> List[int]:
        ids = [b + OFFSET for b in text.encode("utf-8", errors="replace")]
        if add_special:
            ids = [self.bos_id, *ids, self.eos_id]
        if len(ids) > self.max_len:
            ids = ids[: self.max_len - 1] + [self.eos_id]
        return ids

    def encode_pair(self, sentence: str, atom: str, *, add_special: bool = True) -> List[int]:
        """Frame ``<bos> sentence <sep> atom <eos>``; returns (ids, atom_start).

        ``atom_start`` is the index of the first atom token, for loss masking.
        """
        left = [b + OFFSET for b in sentence.encode("utf-8", errors="replace")]
        right = [b + OFFSET for b in atom.encode("utf-8", errors="replace")]
        ids = ([] if not add_special else [self.bos_id]) + left + [self.sep_id] + right + [self.eos_id]
        atom_start = (0 if not add_special else 1) + len(left) + 1
        if len(ids) > self.max_len:
            cut = len(ids) - self.max_len
            ids = ids[cut:]
            atom_start = max(0, atom_start - cut)
        return ids, atom_start

    def decode(self, ids: Sequence[int], *, skip_special: bool = True) -> str:
        special = {self.pad_id, self.bos_id, self.eos_id, self.sep_id}
        raw = bytes(
            (i - OFFSET) & 0xFF
            for i in ids
            if not (skip_special and i in special) and i >= OFFSET
        )
        return raw.decode("utf-8", errors="replace")

    # -- batches ----------------------------------------------------------
    def pad_batch(self, sequences: Iterable[Sequence[int]]) -> tuple[List[List[int]], List[int]]:
        seqs = [list(s) for s in sequences]
        width = min(self.max_len, max((len(s) for s in seqs), default=1))
        ids = [s[:width] + [self.pad_id] * (width - len(s[:width])) for s in seqs]
        mask = [min(len(s), width) for s in seqs]
        return ids, mask

    def collate_pairs(self, pairs: Iterable[tuple[str, str]]):
        """Batch (sentence, atom) -> (ids, loss_mask, atom_start)."""
        rows, starts = [], []
        for sentence, atom in pairs:
            ids, start = self.encode_pair(sentence, atom)
            rows.append(ids)
            starts.append(start)
        ids, _ = self.pad_batch(rows)
        masks = [
            [1.0 if j >= starts[i] else 0.0 for j in range(len(ids[i]))]
            for i in range(len(ids))
        ]
        return ids, masks, starts