"""M2 set ranker with utility score and admission head (research adapter)."""
from __future__ import annotations

import torch
import torch.nn as nn


class SetRankerM2(nn.Module):
    def __init__(self, state_dim: int, cand_dim: int, d: int = 32, layers: int = 2, heads: int = 4):
        super().__init__()
        self.state_proj = nn.Linear(state_dim, d)
        self.cand_proj = nn.Linear(cand_dim, d)
        self.type_emb = nn.Parameter(torch.zeros(2, d))
        enc = nn.TransformerEncoderLayer(
            d_model=d, nhead=heads, dim_feedforward=64, dropout=0.0,
            batch_first=True, norm_first=False,
        )
        self.encoder = nn.TransformerEncoder(enc, num_layers=layers, enable_nested_tensor=False)
        self.score = nn.Linear(d, 1)
        self.admit = nn.Linear(d, 1)

    def forward(self, state, cands, mask):
        h = torch.cat([self.state_proj(state).unsqueeze(1), self.cand_proj(cands)], dim=1)
        n = cands.shape[1]
        type_emb = torch.cat([
            self.type_emb[0:1].expand(state.shape[0], 1, -1),
            self.type_emb[1:2].expand(state.shape[0], n, -1),
        ], dim=1)
        h = self.encoder(h + type_emb, src_key_padding_mask=mask)
        score = self.score(h[:, 1:, :]).squeeze(-1).masked_fill(mask[:, 1:], -1e9)
        admit = self.admit(h[:, 1:, :]).squeeze(-1).masked_fill(mask[:, 1:], -1e9)
        return score, admit
