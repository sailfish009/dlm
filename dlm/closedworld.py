"""DLM v0.0047 -- closed-world absence over a GIVEN candidate universe (untrusted).

Negation is only sound over a finite, explicitly given domain.  This layer builds

    absent(?m, ?l) :- is_module(?m), candidate_layer(?l), not has_layer(?m, ?l)

from a GIVEN candidate set.  The closed-world assumption is scoped to
``candidate_layer`` (the only universe we claim to have enumerated), and the
result is NON-MONOTONIC: adding one ``has_layer`` fact retracts the matching
``absent`` fact -- which pure Horn deduction can never do.  The kernel stratifies
and evaluates; this layer only proposes.
"""
from __future__ import annotations

from typing import Iterable, List, Tuple

from . import Atom, Const, NegAtom, Rule, Var

# The GIVEN universe of layer kinds we close the world over.
CANDIDATE_LAYERS: Tuple[str, ...] = (
    "conv2d", "linear", "dropout", "maxpool2d", "batchnorm2d",
    "layernorm", "gru", "lstm", "attention",
)


def absence_rule() -> Rule:
    m, l = Var("m"), Var("l")
    return Rule(
        Atom("absent", (m, l)),
        (Atom("is_module", (m,)), Atom("candidate_layer", (l,)),
         NegAtom(Atom("has_layer", (m, l)))),
        name="absent_by_closed_world",
    )


def candidate_facts(layers: Iterable[str] = CANDIDATE_LAYERS):
    return [Atom("candidate_layer", (Const(l),)) for l in layers]


def absent_kinds(closed: set, module: str) -> List[str]:
    return sorted(a.args[1].name for a in closed
                  if a.pred == "absent" and a.args[0].name == module)


def unsound_self_negation() -> Rule:
    """A negative self-dependency; ``closure`` must refuse it (ValueError)."""
    x = Var("x")
    return Rule(Atom("p", (x,)), (Atom("q", (x,)), NegAtom(Atom("p", (x,)))))