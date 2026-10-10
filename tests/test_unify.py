"""Tests for unification (shared by the engine and the kernel)."""
from __future__ import annotations

from dlm.logic import Atom, Const, Var
from dlm.unify import apply_atom, unify, walk


def test_unify_ground_atoms_identical():
    a = Atom("p", (Const("a"), Const("b")))
    assert unify(a, a) == {}


def test_unify_binds_a_variable():
    pat = Atom("p", (Var("x"), Const("b")))
    got = Atom("p", (Const("a"), Const("b")))
    s = unify(pat, got)
    assert s is not None
    assert s[Var("x")] == Const("a")


def test_unify_mismatched_predicate_and_arity():
    assert unify(Atom("p", (Const("a"),)), Atom("q", (Const("a"),))) is None
    assert unify(Atom("p", (Const("a"),)), Atom("p", (Const("a"), Const("b")))) is None


def test_unify_conflicting_constants_fails():
    assert unify(Atom("p", (Var("x"),)), Atom("p", (Const("a"),)), {Var("x"): Const("b")}) is None


def test_apply_atom_substitutes_and_chains():
    s = {Var("x"): Var("y"), Var("y"): Const("a")}
    assert walk(Var("x"), s) == Const("a")
    assert apply_atom(Atom("p", (Var("x"), Const("b"))), s) == Atom("p", (Const("a"), Const("b")))