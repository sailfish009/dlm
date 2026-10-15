"""Domain knowledge about *what code means* -- now split into two layers.

The v0.0039 slice hard-wired the PyTorch semantics: a rule said literally
``trains(?f) :- calls(?f, loss_backward)``.  That mixed two very different things:
the *structure* of "understanding code" (given, a tiny interpreter) and the
*meaning of PyTorch* (which is not in the code and must be acquired).

v0.0040 separates them:

* ``BRIDGE_FORMS`` -- the GIVEN semantics: how a generic ``meaning(symbol,
  concept)`` statement makes a structural predicate true.  These rules mention no
  PyTorch symbol; they are the interpreter, still supplied by hand.
* the ``meaning`` FACTS -- the ACQUIRED semantics: which concept each library
  symbol denotes.  They come from ``knowledge.py`` (a web lookup of the library's
  documentation) and are injected as Ground facts.  The kernel treats them like
  any other fact; a symbol with no acquired meaning simply derives nothing.

So ``build_ground_forms(meanings)`` is the Ground the reader reasons over, and
the hand-written part no longer names any PyTorch object.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

Form = tuple

# GIVEN bridge rules: structure only, no library symbol appears.
BRIDGE_FORMS: List[Form] = [
    ("rule", ("is_module", "?c"), ("inherits", "?c", "?b"), ("meaning", "?b", "module_base")),
    ("rule", ("has_layer", "?c", "?l"), ("method_of", "?c", "?m"),
     ("creates", "?m", "?l"), ("meaning", "?l", "layer")),
    ("rule", ("trains", "?f"), ("calls", "?f", "?c"), ("meaning", "?c", "backpropagation")),
    ("rule", ("backpropagates", "?f"), ("calls", "?f", "?c"), ("meaning", "?c", "backpropagation")),
    ("rule", ("optimizes", "?f"), ("calls", "?f", "?c"), ("meaning", "?c", "parameter_update")),
    ("rule", ("evaluates", "?f"), ("calls", "?f", "?c"), ("meaning", "?c", "evaluation")),
    ("rule", ("uses_grad_free", "?f"), ("calls", "?f", "?c"), ("meaning", "?c", "gradient_free")),
    ("rule", ("loads_data", "?f"), ("creates", "?f", "?c"), ("meaning", "?c", "data_loading")),
    ("rule", ("saves_model", "?f"), ("calls", "?f", "?c"), ("meaning", "?c", "serialization")),
    ("rule", ("builds_model", "?f"), ("creates", "?f", "?c"), ("is_module", "?c")),
    # purely structural: the entry point reaches both the train and test routines
    ("rule", ("orchestrates", "?m"), ("calls", "?m", "train"), ("calls", "?m", "test")),
]

# Predicates whose derived atoms are part of the "understanding" narrative,
# in the order they should be told.
UNDERSTANDING = [
    "is_module", "inherits", "has_layer", "trains", "backpropagates", "optimizes",
    "evaluates", "uses_grad_free", "loads_data", "builds_model", "orchestrates",
    "saves_model",
]


def bridge_forms() -> List[Form]:
    """The given interpreter (Ground rules).  No PyTorch symbol appears here."""
    return list(BRIDGE_FORMS)


def meaning_forms(meanings: Dict[str, str]) -> List[Form]:
    """The ACQUIRED ``meaning`` facts (``{slug: concept}``) -- base facts, not rules."""
    return [("meaning", slug, concept) for slug, concept in sorted(meanings.items())]