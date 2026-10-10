"""Tests for the semantic normal form (module 1)."""
from __future__ import annotations

import pytest

from dlm.logic import (
    Atom,
    Const,
    Frame,
    Literal,
    Rule,
    Schema,
    SchemaRegistry,
    Var,
)


# -- terms -----------------------------------------------------------------
def test_const_str():
    assert str(Const("alice")) == "alice"


def test_var_str_marks_the_variable():
    assert str(Var("x")) == "?x"


# -- atom ------------------------------------------------------------------
def test_atom_str_and_arity():
    a = Atom("parent", (Const("alice"), Const("bob")))
    assert str(a) == "(parent alice bob)"
    assert a.arity == 2


def test_nullary_atom_str():
    a = Atom("rains")
    assert a.arity == 0
    assert str(a) == "(rains)"


def test_atom_is_ground_and_variables():
    g = Atom("parent", (Const("a"), Const("b")))
    open_ = Atom("parent", (Const("a"), Var("x")))
    assert g.is_ground() and not open_.is_ground()
    assert open_.variables() == (Var("x"),)
    assert g.variables() == ()


def test_atom_is_function_free():
    with pytest.raises(TypeError):
        Atom("p", (Atom("q", (Const("x"),)),))  # type: ignore[arg-type]


# -- literal ---------------------------------------------------------------
def test_literal_sign_and_str():
    a = Atom("parent", (Const("a"), Const("b")))
    assert str(Literal(a)) == "(parent a b)"
    assert Literal(a).sign == 1
    neg = Literal(a, negated=True)
    assert str(neg) == "(not (parent a b))"
    assert neg.sign == -1
    assert neg.is_ground()


# -- schema ----------------------------------------------------------------
def test_schema_arity_and_role_index():
    s = Schema("calls", ("agent", "patient"))
    assert s.arity == 2
    assert s.index_of("agent") == 0
    assert s.index_of("patient") == 1
    assert s.index_of("missing") == -1


def test_schema_rejects_duplicate_roles():
    with pytest.raises(ValueError):
        Schema("p", ("x", "x"))


# -- frame -----------------------------------------------------------------
def test_frame_roles_and_str():
    f = Frame("calls", (("agent", Const("a")), ("patient", Const("b"))))
    assert f.roles() == {"agent", "patient"}
    assert str(f) == "calls(agent=a, patient=b)"


def test_frame_rejects_duplicate_roles():
    with pytest.raises(ValueError):
        Frame("p", (("x", Const("a")), ("x", Const("b"))))


def test_frame_is_function_free():
    with pytest.raises(TypeError):
        Frame("p", (("x", Atom("q")),))  # type: ignore[arg-type]


# -- normalization: the core operation -------------------------------------
def _registry() -> SchemaRegistry:
    return SchemaRegistry([
        Schema("calls", ("agent", "patient")),
        Schema("charges", ("biller", "payer")),
    ])


def test_normalize_orders_args_by_schema_role_order():
    # slots are given in reverse order; the schema must fix the atom's order.
    f = Frame("calls", (("patient", Const("b")), ("agent", Const("a"))))
    lit = _registry().normalize(f)
    assert lit is not None
    assert lit.atom == Atom("calls", (Const("a"), Const("b")))
    assert str(lit.atom) == "(calls a b)"


def test_normalize_is_role_based_not_surface_order():
    # same words, different roles -> different atoms.
    f1 = Frame("calls", (("agent", Const("a")), ("patient", Const("b"))))
    f2 = Frame("calls", (("agent", Const("b")), ("patient", Const("a"))))
    reg = _registry()
    assert reg.normalize(f1).atom != reg.normalize(f2).atom


def test_normalize_unknown_predicate_abstains():
    assert _registry().normalize(Frame("sings", (("agent", Const("a")),))) is None


def test_normalize_missing_role_abstains():
    # a frame missing the patient cannot be completed by guessing.
    assert _registry().normalize(Frame("calls", (("agent", Const("a")),))) is None


def test_normalize_extra_role_abstains():
    f = Frame("calls", (("agent", Const("a")), ("patient", Const("b")), ("time", Const("t"))))
    assert _registry().normalize(f) is None


def test_normalize_carries_negation_and_variables():
    f = Frame("charges", (("biller", Var("x")), ("payer", Const("c1"))), negated=True)
    lit = _registry().normalize(f)
    assert lit is not None
    assert lit.negated is True
    assert lit.atom == Atom("charges", (Var("x"), Const("c1")))
    assert not lit.is_ground()


def test_registry_membership_and_len():
    reg = _registry()
    assert "calls" in reg and "sings" not in reg
    assert len(reg) == 2
    assert reg.known() == ("calls", "charges")


# -- rules -----------------------------------------------------------------
def test_rule_str_is_sexp():
    r = Rule(
        Atom("ancestor", (Var("x"), Var("y"))),
        (Atom("parent", (Var("x"), Var("y"))),),
    )
    assert str(r) == "(rule (ancestor ?x ?y) (parent ?x ?y))"


def test_named_rule_str():
    r = Rule(
        Atom("ancestor", (Var("x"), Var("y"))),
        (Atom("parent", (Var("x"), Var("y"))),),
        name="anc",
    )
    assert str(r) == "(rule anc (ancestor ?x ?y) (parent ?x ?y))"


def test_rule_variables_union_head_and_body():
    r = Rule(
        Atom("p", (Var("x"),)),
        (Atom("q", (Var("x"), Var("y"))),),
    )
    assert set(r.variables()) == {Var("x"), Var("y")}


def test_rule_rejects_unsafe_head_variable():
    with pytest.raises(ValueError):
        Rule(Atom("p", (Var("x"),)), (Atom("q", (Const("a"),)),))


def test_rule_rejects_empty_body():
    with pytest.raises(ValueError):
        Rule(Atom("p", (Const("a"),)))


def test_rule_rejects_non_atom_body():
    with pytest.raises(TypeError):
        Rule(Atom("p", (Const("a"),)), (Literal(Atom("q", (Const("a"),))),))  # type: ignore[arg-type]