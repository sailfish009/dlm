"""Variant set-ranker family for structure discovery (research adapter, CPU).

`base` is module-for-module identical to m1_proof_state/model.py SetRanker
(same registration order, same shapes) so that seed-11 training reproduces the
committed M1 result — the harness parity control.

Axes:
  a1_cross   — train-time intervention: candidates attend to state + self only
               (no candidate<->candidate interaction). Tests whether inter-
               candidate comparison is recruited for utility ranking.
  a2_pe      — learned positional embeddings added to tokens. Null control:
               the candidate set is permutation-invariant, so PE should not
               help (if it does, the task has positional artifacts).
  a3_tied2   — one shared block applied twice (DT-1 style weight tying).
  a3_indep1  — one independent block. Param-matched init-identical control for
               a3_tied2 (same params, half the compute): separates recurrent
               depth from capacity.
"""
from __future__ import annotations

import torch
import torch.nn as nn


def _tokens(state_proj, cand_proj, type_emb, state, cands):
    h = torch.cat([state_proj(state).unsqueeze(1), cand_proj(cands)], dim=1)
    n = cands.shape[1]
    te = torch.cat([
        type_emb[0:1].expand(state.shape[0], 1, -1),
        type_emb[1:2].expand(state.shape[0], n, -1),
    ], dim=1)
    return h + te


def _head(score, h, mask):
    logits = score(h[:, 1:, :]).squeeze(-1)
    return logits.masked_fill(mask[:, 1:], -1e9)


def _layer(d, heads):
    return nn.TransformerEncoderLayer(
        d_model=d, nhead=heads, dim_feedforward=64,
        dropout=0.0, batch_first=True, norm_first=False)


class SetRanker(nn.Module):
    """base — identical architecture and module order to M1 SetRanker."""

    def __init__(self, state_dim: int, cand_dim: int, d: int = 32, layers: int = 2, heads: int = 4):
        super().__init__()
        self.state_proj = nn.Linear(state_dim, d)
        self.cand_proj = nn.Linear(cand_dim, d)
        self.type_emb = nn.Parameter(torch.zeros(2, d))
        self.encoder = nn.TransformerEncoder(_layer(d, heads), num_layers=layers)
        self.score = nn.Linear(d, 1)

    def forward(self, state, cands, mask):
        h = _tokens(self.state_proj, self.cand_proj, self.type_emb, state, cands)
        h = self.encoder(h, src_key_padding_mask=mask)
        return _head(self.score, h, mask)


class CrossOnlyRanker(SetRanker):
    """A1 — candidate<->candidate attention blocked during training AND eval."""

    def forward(self, state, cands, mask):
        h = _tokens(self.state_proj, self.cand_proj, self.type_emb, state, cands)
        L = h.shape[1]
        attn = torch.zeros(L, L, device=h.device)
        if L > 2:
            blk = torch.full((L - 1, L - 1), float("-inf"), device=h.device)
            blk.fill_diagonal_(0.0)
            attn[1:, 1:] = blk
        h = self.encoder(h, mask=attn, src_key_padding_mask=mask)
        return _head(self.score, h, mask)


class PositionalRanker(SetRanker):
    """A2 — learned positional embeddings (zero-init; null control)."""

    def __init__(self, state_dim, cand_dim, d=32, layers=2, heads=4, max_len=65):
        super().__init__(state_dim, cand_dim, d, layers, heads)
        self.pe = nn.Parameter(torch.zeros(max_len, d))

    def forward(self, state, cands, mask):
        h = _tokens(self.state_proj, self.cand_proj, self.type_emb, state, cands)
        h = h + self.pe[: h.shape[1]].unsqueeze(0)
        h = self.encoder(h, src_key_padding_mask=mask)
        return _head(self.score, h, mask)


class TiedRanker(nn.Module):
    """A3 — one shared block applied `loops` times (weight-tied depth)."""

    def __init__(self, state_dim, cand_dim, d=32, loops=2, heads=4):
        super().__init__()
        self.state_proj = nn.Linear(state_dim, d)
        self.cand_proj = nn.Linear(cand_dim, d)
        self.type_emb = nn.Parameter(torch.zeros(2, d))
        self.block = _layer(d, heads)
        self.loops = loops
        self.score = nn.Linear(d, 1)

    def forward(self, state, cands, mask):
        h = _tokens(self.state_proj, self.cand_proj, self.type_emb, state, cands)
        for _ in range(self.loops):
            h = self.block(h, src_key_padding_mask=mask)
        return _head(self.score, h, mask)


VARIANTS = ("base", "a1_cross", "a2_pe", "a3_tied2", "a3_indep1")


def build(variant: str, state_dim: int, cand_dim: int) -> nn.Module:
    if variant == "base":
        return SetRanker(state_dim, cand_dim)
    if variant == "a1_cross":
        return CrossOnlyRanker(state_dim, cand_dim)
    if variant == "a2_pe":
        return PositionalRanker(state_dim, cand_dim)
    if variant == "a3_tied2":
        return TiedRanker(state_dim, cand_dim, loops=2)
    if variant == "a3_indep1":
        return SetRanker(state_dim, cand_dim, layers=1)
    raise ValueError(variant)