"""A GIVEN typed/moded signature for the DLM reduction (D6: types + modes).

This is UNTRUSTED like every other reduction module: it only declares which
theories the kernel may even consider.  It cannot assert a fact.  Two things
become *structural* that were previously only *probabilistic*:

* **types** -- ``has_layer``'s second slot is a ``layer``, ``meaning``'s first is
  a ``symbol``, ``recognizes`` is about an ``entity``.  A variable used at two
  incompatible positions, or a constant placed outside its type, is rejected.
* **modes** -- an ``in`` position must be bound before use.  A rule that needs an
  input no positive literal can produce is rejected rather than silently
  returning nothing.

The payoff is on the OTHER side of the coin from sampling: seed-3-style unsound
rules (a ``calls`` law that mixes a module where a symbol is required, a head
variable bound by no body literal, an unbound negated literal) are now
INEXPRESSIBLE -- they never enter the candidate set.  The typing does not make
any sound rule unsound and asserts nothing on its own.

v0.0053: the ``concept`` type is the GIVEN decoder vocabulary (``GIVEN_CONCEPTS``)
closed under the acquired concepts, not the acquired concepts alone.  A bridge
rule may name a decoder concept (e.g. ``data_loading``) that a tiny program never
acquires, so an under-acquired run must still type-check; an acquired ``meaning``
still cannot invent a concept outside the decoder.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from dlm import Arg, Atom, Const, NegAtom, Rule, Signature, Var

# --- signature slots ---------------------------------------------------------
# ``in`` = must be bound before use, ``out`` = may be produced, ``any`` = both.
SIGNATURE_ARGS: Dict[str, Tuple[Arg, ...]] = {
    # reduction (observed structure) -- modes are permissive: the kernel joins
    # declaratively, so only ``before`` (a fact-only relation) demands inputs.
    "imports": (Arg("fn", "any"), Arg("import", "any")),
    "defines": (Arg("fn", "any"), Arg("fn", "any")),
    "method_of": (Arg("module", "any"), Arg("fn", "any")),
    "inherits": (Arg("module", "any"), Arg("symbol", "any")),
    "creates": (Arg("fn", "any"), Arg("callable", "any")),
    "calls": (Arg("fn", "any"), Arg("callable", "any")),
    "step_of": (Arg("fn", "any"), Arg("step", "any")),
    "before": (Arg("step", "in"), Arg("step", "in")),
    # acquired meaning
    "meaning": (Arg("symbol", "in"), Arg("concept", "any")),
    # bridge-derived understanding
    "is_module": (Arg("module", "in"),),
    "has_layer": (Arg("module", "in"), Arg("layer", "any")),
    "trains": (Arg("fn", "in"),),
    "backpropagates": (Arg("fn", "in"),),
    "optimizes": (Arg("fn", "in"),),
    "evaluates": (Arg("fn", "in"),),
    "uses_grad_free": (Arg("fn", "in"),),
    "loads_data": (Arg("fn", "in"),),
    "saves_model": (Arg("fn", "in"),),
    "builds_model": (Arg("fn", "in"),),
    "orchestrates": (Arg("fn", "in"),),
    # gist
    "trains_model": (Arg("fn", "in"),),
    "recognizes": (Arg("fn", "in"), Arg("entity", "any")),
    "is_supervised": (Arg("fn", "in"),),
    # acquired domain knowledge
    "dataset_of": (Arg("dataset", "in"), Arg("entity", "any")),
    "task_of": (Arg("dataset", "in"), Arg("entity", "any")),
    # closed-world (D5) universe
    "candidate_layer": (Arg("callable", "any"),),
    "absent": (Arg("module", "in"), Arg("layer", "any")),
    # equality / congruence (D7a): same_kind is the finite alias relation,
    # uses_layer lifts it from definition/call evidence to the layer kind.
    "same_kind": (Arg("callable", "any"), Arg("callable", "any")),
    "uses_layer": (Arg("module", "in"), Arg("callable", "any")),
}

# A small, acyclic type lattice.  Disjoint branches never unify.
TYPE_PARENTS: Dict[str, Tuple[str, ...]] = {
    "callable": ("name",),
    "fn": ("callable",),
    "module": ("fn",),
    "symbol": ("callable",),
    "layer": ("symbol",),
    "dataset": ("symbol",),
    "concept": ("name",),
    "entity": ("name",),
    "import": ("name",),
    "step": ("name",),
}


# The GIVEN decoder vocabulary: every concept constant the bridge/gist rules may
# name.  Acquired ``meaning`` facts extend this set, but a rule may only use a
# concept from the fixed decoder, and an acquired meaning cannot invent one.
GIVEN_CONCEPTS = frozenset({
    "module_base", "layer", "backpropagation", "parameter_update",
    "evaluation", "gradient_free", "data_loading", "serialization",
})


def build_signature(meanings: Dict[str, str],
                    dfacts: List[Tuple[str, str, str]]) -> Signature:
    """Populate the closed constant sets from what was actually acquired.

    ``layer`` comes from the acquired ``meaning`` table; ``dataset`` / ``entity``
    from the searched domain facts; ``concept`` is the GIVEN decoder vocabulary
    closed under the acquired concepts (a bridge rule may name only a decoder
    concept, so an under-acquired run -- e.g. a tiny program that uses no
    ``DataLoader`` -- still type-checks).  Every other type is left open (only the
    subtype relation is checked), so the signature constrains without over-claiming
    an enumeration we do not have.
    """
    types = {
        "concept": GIVEN_CONCEPTS | frozenset(meanings.values()),
        "layer": frozenset(s for s, c in meanings.items() if c == "layer"),
        "dataset": frozenset(d for (p, d, _a) in dfacts if p == "dataset_of"),
        "entity": frozenset(a for (p, _d, a) in dfacts if p == "dataset_of"),
    }
    return Signature(args=dict(SIGNATURE_ARGS), types=types, parents=dict(TYPE_PARENTS))


def absence_rule_typed() -> Rule:
    """The D5 closed-world rule -- now also statically mode-anable and typed."""
    m, l = Var("m"), Var("l")
    return Rule(
        Atom("absent", (m, l)),
        (Atom("is_module", (m,)), Atom("candidate_layer", (l,)),
         NegAtom(Atom("has_layer", (m, l)))),
        name="absent_by_closed_world",
    )


def adversarial() -> List[Tuple[str, Rule, str]]:
    """``(name, rule, expected_error_substring)`` -- each MUST be rejected.

    Every one of these would previously slip past arity checking and either
    derive something unsound or be silently pruned at run time.
    """
    x, y, z, c, m, l, e, d = (Var(n) for n in "?x ?y ?z ?c ?m ?l ?e ?d".split())
    return [
        ("unknown_predicate",
         Rule(Atom("flies", (x,)), (Atom("calls", (x, y)),), "flies"),
         "unknown predicate"),
        ("arity_mismatch",
         Rule(Atom("calls", (x,)), (Atom("calls", (x, y)),), "bad_arity"),
         "arity"),
        ("type_clash",
         Rule(Atom("has_layer", (c, z)),
              (Atom("is_module", (c,)), Atom("meaning", (z, Const("layer"))),
               Atom("meaning", (c, Const("layer")))), "clash"),
         "type clash"),
        ("constant_outside_type",
         Rule(Atom("has_layer", (c, Const("handwritten_digit"))),
              (Atom("is_module", (c,)),), "bad_const"),
         "not of type layer"),
        ("unsafe_head_variable",
         Rule(Atom("calls", (x, y)), (Atom("calls", (x, z)),), "unsafe_head"),
         "unsafe: head variable"),
        ("unbound_negated_variable",
         Rule(Atom("is_module", (c,)),
              (Atom("method_of", (c, m)), NegAtom(Atom("has_layer", (m, l)))),
              "unsafe_neg"),
         "unsafe: negated variable"),
        ("input_never_produced",
         Rule(Atom("orchestrates", (m,)),
              (Atom("calls", (m, c)), Atom("before", (e, d))), "bad_mode"),
         "mode: input"),
    ]