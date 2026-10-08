"""Learned NL grounding (branch L3): tiny encoder + CLM-style contrastive head.

This is DLM's T2 grounder. It instantiates CLM's recipe at 3.5M scale:

  * a transformer body (``tiny_encoder``, vendored from MeowLLM, MIT);
  * a projection head trained with a **bidirectional in-batch InfoNCE** and a
    learnable ``logit_scale`` — the same loss shape as CLM's ``_clm_loss``;
  * **group masking**: two sentences that map to the same atom are never
    treated as mutual negatives.

It is a *retrieval* grounder, not a generator: it returns the nearest atom or
abstains. Nothing is generated, so there is no free text in the answer path.

Differences from CLM, stated honestly: CLM freezes a *pretrained* 8B encoder and
trains heads only. Here there are no pretrained weights, so by default the
3.5M encoder is trained end to end (``trainable_encoder=True``); the
frozen-encoder arm is kept as a matched control.

Training data is bootstrapped by the T1 ``GrammarGrounder``: a set of phrase
patterns per relation is split, T2 learns the train phrases, and evaluation
asks whether it generalizes to HELD-OUT paraphrases of the same relations
(where T1 abstains by construction).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from itertools import product
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .byte_tokenizer import ByteTokenizer
from .grounding import Grounding, Pattern
from .interpreter import ParseError, parse_atom
from .terms import Atom
from .tiny_encoder import TinyEncoder, TinyEncoderConfig, build_encoder

__all__ = [
    "ProjectionHead",
    "AtomIndex",
    "synthesize_pairs",
    "pattern_split",
    "CharNgramGrounder",
    "LearnedGrounder",
    "DEFAULT_ENTITIES",
]

DEFAULT_ENTITIES = ("alice", "bob", "carol", "dave", "erin", "frank")


# ---------------------------------------------------------------------------
# Head (CLM-shaped)
# ---------------------------------------------------------------------------

class ProjectionHead(nn.Module):
    """Linear projection + L2 norm + learnable temperature (CLM ``heads.py``)."""

    def __init__(self, d_model: int, proj_dim: int = 128, init_temp: float = 0.07):
        super().__init__()
        self.proj = nn.Linear(d_model, proj_dim, bias=False)
        self.logit_scale = nn.Parameter(torch.tensor(math.log(1.0 / init_temp)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.normalize(self.proj(x), dim=-1)

    def scale(self) -> torch.Tensor:
        return self.logit_scale.exp().clamp(max=100.0)


# ---------------------------------------------------------------------------
# Candidate atom set
# ---------------------------------------------------------------------------

class AtomIndex:
    """Ordered set of candidate atoms, parsed once."""

    def __init__(self, atoms: Iterable[Atom | str]):
        self._atoms: List[Atom] = []
        self._id: Dict[str, int] = {}
        for a in atoms:
            self.add(a)

    def add(self, atom: Atom | str) -> int:
        key = self._key(atom)
        if key not in self._id:
            self._id[key] = len(self._atoms)
            self._atoms.append(parse_atom(key))
        return self._id[key]

    @staticmethod
    def _key(atom: Atom | str) -> str:
        """Canonical key: parse strings so spacing/casing never diverge."""
        return str(parse_atom(atom) if isinstance(atom, str) else atom)

    def id_of(self, atom: Atom | str) -> int:
        key = self._key(atom)
        if key not in self._id:
            raise KeyError(f"atom not in index: {key}")
        return self._id[key]

    def __len__(self) -> int:
        return len(self._atoms)

    def __iter__(self):
        return iter(self._atoms)

    def atoms(self) -> List[Atom]:
        return list(self._atoms)

    def strings(self) -> List[str]:
        return [str(a) for a in self._atoms]


# ---------------------------------------------------------------------------
# Data bootstrap from the T1 grammar
# ---------------------------------------------------------------------------

def _placeholders(text: str) -> List[str]:
    import re

    seen, out = set(), []
    for name in re.findall(r"\{(\w+)\}", text):
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def synthesize_pairs(
    patterns: Sequence[Pattern],
    entities: Sequence[str] = DEFAULT_ENTITIES,
    *,
    per_pattern: Optional[int] = None,
    seed: int = 0,
    shuffle: bool = True,
) -> List[Tuple[str, str]]:
    """Render (sentence, atom) pairs from patterns by substituting entities.

    Sentences carry the kind's punctuation (``?`` for query, ``.`` for assert)
    so training text resembles real user input.

    To evaluate paraphrase generalization, call this with the SAME ``entities``
    (and ``per_pattern``) for the train and held-out pattern sets so both share
    one candidate atom set; otherwise held-out atoms simply do not exist in the
    index and every held-out sentence is unwinnable.
    """
    rng = random.Random(seed)
    pairs: List[Tuple[str, str]] = []
    for p in patterns:
        names = _placeholders(p.template) or _placeholders(p.phrase)
        if not names:
            pairs.append((p.phrase, p.template))
            continue
        combos = list(product(entities, repeat=len(names)))
        rng.shuffle(combos)
        if per_pattern is not None:
            combos = combos[:per_pattern]
        for combo in combos:
            binding = dict(zip(names, combo))
            try:
                atom = p.template.format(**binding)
                parse_atom(atom)  # validate now, not at training time
            except (KeyError, ParseError):
                continue
            sentence = p.phrase.format(**binding)
            if p.kind == "assert":
                sentence = sentence + "."
            else:
                sentence = sentence + "?"
            pairs.append((sentence, atom))
    if shuffle:
        rng.shuffle(pairs)
    return pairs


def pattern_split(
    patterns: Sequence[Pattern],
    *,
    heldout_frac: float = 0.34,
    seed: int = 0,
) -> Tuple[List[Pattern], List[Pattern]]:
    """Split *phrases* while keeping every relation's template in both halves.

    Holding out phrase variants (not relations) means both halves share the
    candidate atom set: T1 abstains on held-out phrasing, T2 must generalize.
    """
    rng = random.Random(seed)
    by_template: Dict[str, List[Pattern]] = {}
    for p in patterns:
        by_template.setdefault(p.template, []).append(p)

    train, heldout = [], []
    for template, group in by_template.items():
        group = list(group)
        rng.shuffle(group)
        n_out = 0 if len(group) < 2 else max(1, int(round(len(group) * heldout_frac)))
        n_out = min(n_out, len(group) - 1)  # always leave >=1 train phrase
        heldout.extend(group[:n_out])
        train.extend(group[n_out:])
    return train, heldout


# ---------------------------------------------------------------------------
# Lexical control (no torch, no learning)
# ---------------------------------------------------------------------------

def _ngrams(text: str, n: int = 3) -> Dict[str, float]:
    s = f"  {text.lower()}  "
    grams = [s[i:i + n] for i in range(len(s) - n + 1)]
    return {g: 1.0 for g in grams}


class CharNgramGrounder:
    """Character-3gram cosine nearest-prototype. Deterministic, untrained.

    A strong non-neural baseline: it tests whether the tiny transformer adds
    anything over surface lexical overlap.
    """

    def __init__(self, pairs: Iterable[Tuple[str, str]]):
        sums: Dict[str, Dict[str, float]] = {}
        counts: Dict[str, int] = {}
        for sentence, atom in pairs:
            acc = sums.setdefault(atom, {})
            for g in _ngrams(sentence):
                acc[g] = acc.get(g, 0.0) + 1.0
            counts[atom] = counts.get(atom, 0) + 1
        self.prototypes: Dict[str, Dict[str, float]] = {}
        for atom, acc in sums.items():
            c = counts[atom]
            self.prototypes[atom] = {g: v / c for g, v in acc.items()}
        self.atoms: List[str] = sorted(self.prototypes)

    @staticmethod
    def _cos(a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(v * b.get(g, 0.0) for g, v in a.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def ground(self, sentence: str, *, threshold: float = 0.5) -> Grounding:
        if not self.atoms:
            return Grounding(False, reason="empty index", raw=sentence)
        q = _ngrams(sentence)
        best_atom, best = None, -1.0
        for atom in self.atoms:
            sim = self._cos(q, self.prototypes[atom])
            if sim > best:
                best_atom, best = atom, sim
        if best < threshold:
            return Grounding(False, reason=f"below threshold ({best:.3f})", raw=sentence)
        return Grounding(
            ok=True, atom=parse_atom(best_atom), source="char_ngram",
            confidence=float(best), raw=sentence,
        )


# ---------------------------------------------------------------------------
# Learned grounder
# ---------------------------------------------------------------------------

@dataclass
class TrainReport:
    epochs: int = 0
    final_loss: float = 0.0
    history: List[float] = field(default_factory=list)
    n_pairs: int = 0
    n_atoms: int = 0
    n_trainable_params: int = 0
    final_logit_scale: float = 0.0


class LearnedGrounder(nn.Module):
    """T2: tiny encoder + contrastive head; retrieve nearest atom or abstain."""

    def __init__(
        self,
        tokenizer: Optional[ByteTokenizer] = None,
        *,
        proj_dim: int = 128,
        init_temp: float = 0.07,
        trainable_encoder: bool = True,
        seed: int = 0,
        default_threshold: float = 0.5,
        **encoder_kwargs,
    ):
        super().__init__()
        torch.manual_seed(seed)
        self.tokenizer = tokenizer or ByteTokenizer()
        self.encoder: TinyEncoder = build_encoder(self.tokenizer, **encoder_kwargs)
        if not trainable_encoder:
            self.encoder.freeze()
        self.trainable_encoder = trainable_encoder
        self.default_threshold = default_threshold
        self.head = ProjectionHead(self.encoder.cfg.d_model, proj_dim, init_temp)
        self.index = AtomIndex([])
        self.register_buffer("_atom_emb", torch.zeros(0, proj_dim), persistent=False)

    # -- embedding --------------------------------------------------------
    def _encode_texts(self, texts: Sequence[str]) -> torch.Tensor:
        ids, _ = self.tokenizer.pad_batch([self.tokenizer.encode(t) for t in texts])
        ids_t = torch.tensor(ids, dtype=torch.long)
        mask = ids_t.ne(self.tokenizer.pad_id).long()
        return self.head(self.encoder(ids_t, mask))

    def embed_sentences(self, sentences: Sequence[str]) -> torch.Tensor:
        return self._encode_texts(list(sentences))

    def embed_atoms(self, atoms: Sequence[str]) -> torch.Tensor:
        return self._encode_texts(list(atoms))

    # -- loss (CLM _clm_loss shape) ---------------------------------------
    def info_nce(self, z_s: torch.Tensor, z_a: torch.Tensor, atom_ids=None) -> torch.Tensor:
        logits = self.head.scale() * (z_s @ z_a.t())
        n = logits.size(0)
        labels = torch.arange(n, device=logits.device)
        if atom_ids is not None:
            same = atom_ids[:, None] == atom_ids[None, :]
            off_diag = same & ~torch.eye(n, dtype=torch.bool, device=logits.device)
            logits = logits.masked_fill(off_diag, float("-inf"))
        return 0.5 * (
            F.cross_entropy(logits, labels) + F.cross_entropy(logits.t(), labels)
        )

    # -- training ---------------------------------------------------------
    def fit(
        self,
        pairs: Sequence[Tuple[str, str]],
        *,
        epochs: int = 200,
        lr: float = 3e-3,
        batch_size: Optional[int] = None,
        seed: int = 0,
        verbose: bool = False,
    ) -> TrainReport:
        if not pairs:
            raise ValueError("fit() needs at least one (sentence, atom) pair")
        index = AtomIndex([atom for _, atom in pairs])
        sentences = [s for s, _ in pairs]
        atoms = [a for _, a in pairs]
        atom_ids = torch.tensor([index.id_of(a) for a in atoms], dtype=torch.long)

        params = [p for p in self.parameters() if p.requires_grad]
        opt = torch.optim.AdamW(params, lr=lr, weight_decay=0.01)
        bs = batch_size or len(pairs)
        gen = torch.Generator().manual_seed(seed)
        history: List[float] = []

        self.train()
        for ep in range(epochs):
            perm = torch.randperm(len(pairs), generator=gen)
            ep_losses = []
            for start in range(0, len(pairs), bs):
                idx = perm[start:start + bs]
                bs_sent = [sentences[i] for i in idx.tolist()]
                bs_atom = [atoms[i] for i in idx.tolist()]
                z_s = self.embed_sentences(bs_sent)
                z_a = self.embed_atoms(bs_atom)
                loss = self.info_nce(z_s, z_a, atom_ids[idx])
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                opt.step()
                ep_losses.append(float(loss.detach()))
            history.append(sum(ep_losses) / len(ep_losses))
            if verbose and (ep % 20 == 0 or ep == epochs - 1):
                print(f"  epoch {ep:4d}  loss {history[-1]:.4f}")
        self.eval()

        self.index = index
        with torch.no_grad():
            self._atom_emb = self.embed_atoms(index.strings())
        return TrainReport(
            epochs=epochs,
            final_loss=history[-1],
            history=history,
            n_pairs=len(pairs),
            n_atoms=len(index),
            n_trainable_params=sum(p.numel() for p in params),
            final_logit_scale=float(self.head.scale().detach()),
        )

    # -- inference: retrieve or abstain -----------------------------------
    @torch.no_grad()
    def similarities(self, sentences: Sequence[str]) -> torch.Tensor:
        z = self.embed_sentences(sentences)
        if self._atom_emb.numel() == 0:
            return torch.zeros(len(sentences), 0)
        return z @ self._atom_emb.t()

    def ground(self, sentence: str, *, threshold: Optional[float] = None) -> Grounding:
        return self.ground_batch([sentence], threshold=threshold)[0]

    @torch.no_grad()
    def ground_batch(self, sentences: Sequence[str], *, threshold: Optional[float] = None) -> List[Grounding]:
        if threshold is None:
            threshold = self.default_threshold
        sentences = list(sentences)
        if not sentences:
            return []
        if len(self.index) == 0:
            return [Grounding(False, reason="empty index", raw=s) for s in sentences]
        self.eval()
        sims = self.similarities(sentences)
        best_vals, best_idx = sims.max(dim=1)
        strings = self.index.strings()
        out: List[Grounding] = []
        for s, v, j in zip(sentences, best_vals.tolist(), best_idx.tolist()):
            if v < threshold:
                out.append(Grounding(False, reason=f"below threshold ({v:.3f})", raw=s))
            else:
                out.append(Grounding(
                    ok=True, atom=parse_atom(strings[j]), source="learned",
                    confidence=float(v), raw=s,
                ))
        return out

    # -- persistence ------------------------------------------------------
    def save(self, path: str) -> None:
        torch.save({
            "state": self.state_dict(),
            "encoder_cfg": vars(self.encoder.cfg),
            "tokenizer": vars(self.tokenizer),
            "index": self.index.strings(),
            "proj_dim": self.head.proj.out_features,
            "default_threshold": self.default_threshold,
            "trainable_encoder": self.trainable_encoder,
        }, path)

    @classmethod
    def load(cls, path: str) -> "LearnedGrounder":
        blob = torch.load(path, weights_only=False)
        tok = ByteTokenizer(**blob["tokenizer"])
        obj = cls(tok, trainable_encoder=blob["trainable_encoder"],
                  proj_dim=blob.get("proj_dim", 128),
                  default_threshold=blob.get("default_threshold", 0.5),
                  **{k: v for k, v in blob["encoder_cfg"].items()
                     if k in TinyEncoderConfig.__dataclass_fields__ and k not in ("vocab_size", "max_seq_len", "pad_token_id")})
        obj.load_state_dict(blob["state"])
        obj.index = AtomIndex(blob["index"])
        obj.eval()
        if obj._atom_emb.numel() == 0 and len(obj.index):
            with torch.no_grad():
                obj._atom_emb = obj.embed_atoms(obj.index.strings())
        return obj