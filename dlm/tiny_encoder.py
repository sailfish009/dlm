"""A small transformer encoder vendored for the DLM NL front-end (branch L2).

Adapted from **MeowLLM** — MIT License, Copyright (c) 2026 phanii9
(``/research/MeowLLM/meow/model.py``). The original is a causal decoder-only
persona LM; we reuse its blocks (RMSNorm, RoPE, SDPA attention, SwiGLU, tied
embeddings, pre-norm residuals) and expose it as a *frozen-or-trainable
encoder* that returns one pooled vector per input, matching the CLM contract
(``last-token`` pooling of a causal LM; ``mean`` pooling with bidirectional
attention is also supported).

Deviations from the original, all in service of encoding rather than generation:
  * vocab defaults to the DLM byte tokenizer (260), not the Meow BPE (2048);
  * attention can be bidirectional and honours a key-padding mask;
  * ``forward`` returns pooled features (B, D) instead of logits.

No pretrained weights are used: MeowLLM ships none, so this module is trained
from scratch (3.5M params, trainable on CPU / in the 6GB budget).
"""
from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

from .byte_tokenizer import VOCAB_SIZE

__all__ = ["TinyEncoderConfig", "TinyEncoder", "build_encoder"]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class TinyEncoderConfig:
    """MeowLLM geometry by default; vocab/pooling adjusted for the encoder."""

    vocab_size: int = VOCAB_SIZE
    d_model: int = 256
    n_layers: int = 4
    n_heads: int = 4
    ffn_hidden: int = 640
    max_seq_len: int = 256
    dropout: float = 0.0
    rope_base: float = 10000.0
    pad_token_id: int = 0
    causal: bool = False          # bidirectional by default
    pool: str = "mean"            # "mean" | "last"

    @property
    def head_dim(self) -> int:
        assert self.d_model % self.n_heads == 0, (
            f"d_model {self.d_model} must be divisible by n_heads {self.n_heads}"
        )
        return self.d_model // self.n_heads


# ---------------------------------------------------------------------------
# Vendored blocks (MeowLLM, MIT)
# ---------------------------------------------------------------------------

class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        rms = x.pow(2).mean(dim=-1, keepdim=True).add(self.eps).rsqrt()
        return x * rms * self.weight


def build_rope_cache(seq_len, head_dim, base, device="cpu", dtype=torch.float32):
    """Precompute RoPE cos/sin tables. Shape: (seq_len, head_dim/2)."""
    assert head_dim % 2 == 0, "head_dim must be even for RoPE"
    half = head_dim // 2
    freqs = 1.0 / (base ** (torch.arange(0, half, device=device).float() / half))
    angles = torch.outer(torch.arange(seq_len, device=device).float(), freqs)
    return angles.cos().to(dtype), angles.sin().to(dtype)


def apply_rope(x, cos, sin):
    """Apply rotary embeddings to x of shape (B, H, T, head_dim)."""
    x1, x2 = x[..., 0::2], x[..., 1::2]
    cos, sin = cos[None, None], sin[None, None]
    rotated = torch.stack([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)
    return rotated.flatten(-2)


class SelfAttention(nn.Module):
    """SDPA attention with optional causality and a key-padding mask."""

    def __init__(self, cfg: TinyEncoderConfig):
        super().__init__()
        self.cfg = cfg
        self.qkv = nn.Linear(cfg.d_model, 3 * cfg.d_model, bias=False)
        self.out = nn.Linear(cfg.d_model, cfg.d_model, bias=False)
        self.dropout = cfg.dropout

    def forward(self, x, cos, sin, key_mask=None):
        B, T, C = x.shape
        H, D = self.cfg.n_heads, self.cfg.head_dim

        q, k, v = self.qkv(x).chunk(3, dim=-1)
        q = q.view(B, T, H, D).transpose(1, 2)
        k = k.view(B, T, H, D).transpose(1, 2)
        v = v.view(B, T, H, D).transpose(1, 2)

        q = apply_rope(q, cos[:T], sin[:T])
        k = apply_rope(k, cos[:T], sin[:T])

        attn_mask = key_mask
        if self.cfg.causal:
            neg = torch.finfo(x.dtype).min
            tri = torch.triu(
                torch.ones(T, T, device=x.device, dtype=torch.bool), diagonal=1
            )[None, None]
            bias = torch.zeros(1, 1, T, T, device=x.device, dtype=x.dtype).masked_fill(tri, neg)
            attn_mask = bias if attn_mask is None else attn_mask + bias

        y = F.scaled_dot_product_attention(
            q, k, v,
            attn_mask=attn_mask,
            dropout_p=self.dropout if self.training else 0.0,
        )
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.out(y)


class SwiGLU(nn.Module):
    def __init__(self, cfg: TinyEncoderConfig):
        super().__init__()
        self.w_gate = nn.Linear(cfg.d_model, cfg.ffn_hidden, bias=False)
        self.w_up = nn.Linear(cfg.d_model, cfg.ffn_hidden, bias=False)
        self.w_down = nn.Linear(cfg.ffn_hidden, cfg.d_model, bias=False)

    def forward(self, x):
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))


class Block(nn.Module):
    def __init__(self, cfg: TinyEncoderConfig):
        super().__init__()
        self.norm1 = RMSNorm(cfg.d_model)
        self.attn = SelfAttention(cfg)
        self.norm2 = RMSNorm(cfg.d_model)
        self.ffn = SwiGLU(cfg)

    def forward(self, x, cos, sin, key_mask=None):
        x = x + self.attn(self.norm1(x), cos, sin, key_mask)
        x = x + self.ffn(self.norm2(x))
        return x


# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------

class TinyEncoder(nn.Module):
    """Stack of Meow blocks returning pooled features ``(B, d_model)``."""

    def __init__(self, cfg: TinyEncoderConfig | None = None):
        super().__init__()
        self.cfg = cfg or TinyEncoderConfig()
        assert self.cfg.pool in ("mean", "last"), self.cfg.pool
        self.tok_emb = nn.Embedding(self.cfg.vocab_size, self.cfg.d_model)
        self.blocks = nn.ModuleList([Block(self.cfg) for _ in range(self.cfg.n_layers)])
        self.norm_f = RMSNorm(self.cfg.d_model)
        cos, sin = build_rope_cache(self.cfg.max_seq_len, self.cfg.head_dim, self.cfg.rope_base)
        self.register_buffer("rope_cos", cos, persistent=False)
        self.register_buffer("rope_sin", sin, persistent=False)
        self.apply(self._init_weights)

    def _init_weights(self, m: nn.Module):
        std = 0.02
        if isinstance(m, nn.Linear):
            if hasattr(m, "_is_residual"):
                std = std / (2 * self.cfg.n_layers) ** 0.5
            nn.init.trunc_normal_(m.weight, mean=0.0, std=std)
        elif isinstance(m, nn.Embedding):
            nn.init.trunc_normal_(m.weight, mean=0.0, std=std)

    # -- introspection ----------------------------------------------------
    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def freeze(self) -> "TinyEncoder":
        for p in self.parameters():
            p.requires_grad_(False)
        return self.eval()

    def unfreeze(self) -> "TinyEncoder":
        for p in self.parameters():
            p.requires_grad_(True)
        return self

    # -- forward ----------------------------------------------------------
    def encode_hidden(self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None):
        """Return per-token hidden states ``(B, T, d_model)``."""
        if input_ids.dim() == 1:
            input_ids = input_ids[None]
        B, T = input_ids.shape
        assert T <= self.cfg.max_seq_len, (
            f"seq length {T} exceeds max {self.cfg.max_seq_len}"
        )
        if attention_mask is None:
            attention_mask = input_ids.ne(self.cfg.pad_token_id).long()
        key_mask = None
        if attention_mask is not None:
            # additive float mask: 0.0 keeps a key, -inf blocks it (unambiguous
            # SDPA semantics, unlike the bool-mask convention)
            neg = torch.finfo(self.tok_emb.weight.dtype).min
            pad = attention_mask[:, None, None, :] == 0
            key_mask = torch.zeros(
                1, 1, 1, attention_mask.size(1),
                device=input_ids.device, dtype=self.tok_emb.weight.dtype,
            ).masked_fill(pad, neg)

        x = self.tok_emb(input_ids)
        for block in self.blocks:
            x = block(x, self.rope_cos, self.rope_sin, key_mask)
        return self.norm_f(x), attention_mask

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None):
        """Pooled features ``(B, d_model)``."""
        hidden, mask = self.encode_hidden(input_ids, attention_mask)
        if self.cfg.pool == "mean":
            m = mask.to(hidden.dtype)[:, :, None]
            return (hidden * m).sum(1) / m.sum(1).clamp(min=1.0)
        # "last": hidden state at the final valid position
        idx = mask.long().sum(1).clamp(min=1) - 1
        return hidden[torch.arange(hidden.size(0), device=hidden.device), idx]


def build_encoder(tokenizer=None, **overrides) -> TinyEncoder:
    """Build an encoder sized to ``tokenizer`` (if given)."""
    cfg = TinyEncoderConfig()
    if tokenizer is not None:
        cfg.vocab_size = tokenizer.vocab_size
        cfg.max_seq_len = tokenizer.max_len
        cfg.pad_token_id = tokenizer.pad_id
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return TinyEncoder(cfg)