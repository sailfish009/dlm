"""PyTorch symbol semantics -- the GIVEN vocabulary for the model's acquisition.

This module is now *vocabulary only*.  The subject that actually reaches the web
-- search the documentation inventory, read the definition paragraph, reduce it
to a concept, cache the record with provenance -- lives in the MODEL
(:mod:`dlm.acquire` + :mod:`dlm.search` + :mod:`dlm.web`).  What stays here is the
GIVEN, domain-specific part: the cue lexicon that maps a verbatim PyTorch
definition onto one of the concepts the bridge rules (``semantics.py``) use, and
the receiver hints that disambiguate a method tail.

Keeping the vocabulary here and the machinery in ``dlm`` is the v0.0054 boundary:
the experiment configures the model, it does not own web search or acquisition.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

from dlm.acquire import (SymbolVocabulary, acquire_symbol_meanings,
                         meaning_facts, symbol_candidates)
from dlm.search import SE_API, extract_definition, reduce_text, resolve_object
from dlm.web import UA

__all__ = [
    "CONCEPT_CUES", "SEARCH_CUES", "RECEIVER_HINTS", "DOCS_BASE", "INVENTORY_URL",
    "KNOWLEDGE_VERSION", "SYMBOL_VOCAB", "symbol_candidates", "resolve",
    "reduce_definition", "extract_definition", "acquire_knowledge",
    "meaning_facts", "load_knowledge", "save_knowledge",
]

DOCS_BASE = "https://docs.pytorch.org/docs/stable/"
INVENTORY_URL = DOCS_BASE + "objects.inv"
KNOWLEDGE_VERSION = 1

# -- the concept vocabulary (the TARGET of the reduction) --------------------
#
# These are the handful of ideas the bridge rules in semantics.py can use.  A
# definition is mapped to at most one concept, by the FIRST concept whose cue
# phrase occurs in the (lower-cased) definition.  Order is the disambiguation
# priority.  The cues are matched against verbatim documentation text.
CONCEPT_CUES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("module_base", ("base class for all neural network", "base class for all neural")),
    ("backpropagation", ("computes the gradient", "compute the gradient",
                         "gradient of current tensor", "backward pass", "backpropagat")),
    ("parameter_update", ("optimization step", "update parameter", "update the parameters",
                          "updates the parameters", "updating the parameters")),
    ("evaluation", ("evaluation mode", "evaluating time")),
    ("gradient_free", ("disables gradient", "disable gradient", "disabling gradient",
                       "no gradient computation", "without tracking gradient",
                       "does not track gradient")),
    ("data_loading", ("data loader", "dataloader", "combines a dataset")),
    ("serialization", ("saves an object", "save and load", "state dict", "serializes")),
    ("layer", ("2d convolution", "convolution", "applies an affine linear",
               "linear transformation", "rectified linear", "max pooling", "pooling",
               "dropout", "zeroes some of the elements", "batch normalization",
               "normalization")),
)

# Free-text cues for the search provider (Stack Exchange titles + answers).  A
# search hit is reduced with the SAME concept vocabulary but looser phrasing,
# because Q&A is not a definition.  Used as a corroborating/fallback signal.
SEARCH_CUES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("module_base", ("base class for all neural network", "inherit from nn.module",
                     "subclass nn.module", "base class of all neural")),
    ("backpropagation", ("backward pass", "backpropagat", "compute the gradient",
                         "computes the gradient", "gradients are stored")),
    ("parameter_update", ("update the parameters", "updates the parameters",
                          "updating the parameters", "single optimization step",
                          "update the weights")),
    ("evaluation", ("evaluation mode", "inference mode", "evaluating time")),
    ("gradient_free", ("disable gradient", "disables gradient", "disabling gradient",
                       "no gradient computation", "without tracking gradient")),
    ("data_loading", ("data loader", "dataloader", "iterable over a dataset",
                      "combines a dataset")),
    ("serialization", ("saves an object", "save and load", "state dict", "serialize")),
    ("layer", ("2d convolution", "convolution", "linear transformation",
               "fully connected", "linear layer")),
)

# Receiver-type hints: a method label ``head.tail`` (e.g. ``loss.backward``) is
# disambiguated toward the documented class that owns it.  This is the small,
# auditable piece of "how variable names map to library types" the resolver
# needs; every resolution it produces is still recorded and reviewable.
RECEIVER_HINTS: Dict[str, str] = {
    "loss": "torch.Tensor",
    "pred": "torch.Tensor",
    "output": "torch.Tensor",
    "data": "torch.Tensor",
    "target": "torch.Tensor",
    "x": "torch.Tensor",
    "model": "torch.nn.Module",
    "optimizer": "torch.optim.Optimizer",
    "scheduler": "torch.optim.lr_scheduler",
}

# The GIVEN vocabulary handed to the model's acquisition subject.
SYMBOL_VOCAB = SymbolVocabulary(
    concept_cues=CONCEPT_CUES,
    search_cues=SEARCH_CUES,
    receiver_hints=RECEIVER_HINTS,
    inventory_url=INVENTORY_URL,
    docs_base=DOCS_BASE,
    inventory_prefixes=("torch.",),
    search_site="stackoverflow",
    search_prefix="pytorch",
    record_name="pytorch_knowledge.json",
)


# -- compatibility shims over the model layers ------------------------------
def resolve(label: str, inventory: Dict[str, str]) -> Tuple[Optional[str], str]:
    return resolve_object(label, inventory, RECEIVER_HINTS)


def reduce_definition(text: str,
                      cues: Tuple[Tuple[str, Tuple[str, ...]], ...] = CONCEPT_CUES
                      ) -> Optional[str]:
    return reduce_text(text, cues)


def _knowledge_path(cache_dir: str) -> str:
    return os.path.join(cache_dir, "pytorch_knowledge.json")


def load_knowledge(cache_dir: str) -> dict:
    path = _knowledge_path(cache_dir)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"version": KNOWLEDGE_VERSION, "source": INVENTORY_URL, "symbols": {}}


def save_knowledge(cache_dir: str, kb: dict) -> None:
    with open(_knowledge_path(cache_dir), "w", encoding="utf-8") as fh:
        json.dump(kb, fh, indent=1, sort_keys=True, ensure_ascii=False)


def acquire_knowledge(facts: List[tuple], labels: Dict[str, str], cache_dir: str,
                      offline: bool = False, search: bool = True,
                      max_new: Optional[int] = None) -> dict:
    """Acquire ``meaning(symbol, concept)`` for the library symbols in ``facts``.

    Delegates to the model's acquisition subject (:func:`dlm.acquire.
    acquire_symbol_meanings`); this function only supplies the GIVEN vocabulary.
    """
    cands = symbol_candidates(facts, labels)
    return acquire_symbol_meanings(cands, labels, cache_dir, SYMBOL_VOCAB,
                                   version=KNOWLEDGE_VERSION, offline=offline,
                                   search=search, max_new=max_new)