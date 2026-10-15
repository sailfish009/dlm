"""Acquired API-effect facts (untrusted knowledge source).

The *given* interpreter (``semantics.py``) names no library symbol: it only knows
that a ``meaning(symbol, concept)`` statement makes a structural predicate true.
The *effect* of a symbol -- "calling ``zero_grad`` prevents gradient
accumulation" -- is a fact about the library, exactly like the ``meaning`` facts,
so it lives here (untrusted, with provenance) rather than in the kernel or in the
given bridge.  ``explains(F, S, E) :- calls(F, S), api_effect(S, E)`` then turns
an observed call into a "why" sentence.  Nothing here is asserted by the kernel;
the atoms are consumed like any other fact and the resulting sentence is
re-checked with ``prove``/``verify``.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

# symbol -> effect.  Provenance: PyTorch API semantics (documented behaviour).
API_EFFECTS: Tuple[Tuple[str, str], ...] = (
    ("optimizer_zero_grad", "prevents_gradient_accumulation"),
    ("loss_backward", "computes_gradients"),
    ("optimizer_step", "applies_parameter_update"),
    ("model_eval", "disables_dropout_and_batchnorm"),
    ("torch_save", "persists_model_state"),
)
API_PROVENANCE = "pytorch-api-semantics (acquired, not derived from the program)"

# The one GIVEN rule that turns an effect fact + an observed call into "why".
# Names no library symbol; the symbol facts stay in API_EFFECTS.
EXPLAINS_FORM: tuple = ("rule", ("explains", "?f", "?s", "?e"),
                        ("calls", "?f", "?s"), ("api_effect", "?s", "?e"))

EFFECT_PHRASES: Dict[str, str] = {
    "prevents_gradient_accumulation": "prevent gradient accumulation",
    "computes_gradients": "compute the gradients",
    "applies_parameter_update": "apply the parameter update",
    "disables_dropout_and_batchnorm": "disable dropout and batch-norm during inference",
    "persists_model_state": "persist the trained model",
}


def effect_phrase(effect: str) -> str:
    return EFFECT_PHRASES.get(effect, effect.replace("_", " "))


def api_effect_facts() -> List[Tuple[str, str, str]]:
    return [("api_effect", s, e) for s, e in API_EFFECTS]


def direct_explains(direct_calls: Iterable[Tuple[str, str]]) -> List[Tuple[str, str, str, str]]:
    """``explains(F, S, E)`` for DIRECT calls only (transitive attribution is
    misleading: the entry point does not itself reset the gradients)."""
    eff = dict(API_EFFECTS)
    out = []
    for f, s in sorted(set(direct_calls)):
        e = eff.get(s)
        if e:
            out.append(("explains", f, s, e))
    return out