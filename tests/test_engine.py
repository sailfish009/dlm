"""Tests for the deduction engine (module 5)."""
from __future__ import annotations

from dlm.engine import closure, entails, holds, prove
from dlm.kb import KnowledgeBase
from dlm.kernel import Proof, verify
from dlm.logic import Atom, Const, Literal, Rule, Var


def A(pred, *names):
    return Atom(pred, tuple(Const(n) for n in names))


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("a", "b"), ("b", "c"), ("c", "d")]:
        kb.add_fact(A("parent", a, b))
    kb.add_rule(Rule(
        Atom("ancestor", (Var("x"), Var("y"))),
        (Atom("parent", (Var("x"), Var("y"))),),
        name="anc-base",
    ))
    kb.add_rule(Rule(
        Atom("ancestor", (Var("x"), Var("z"))),
        (Atom("parent", (Var("x"), Var("y"))), Atom("ancestor", (Var("y"), Var("z")))),
        name="anc-step",
    ))
    return kb


def test_closure_derives_transitive_ancestors():
    got = closure(build_kb())
    assert A("parent", "a", "b") in got
    assert A("ancestor", "a", "b") in got
    assert A("ancestor", "a", "c") in got
    assert A("ancestor", "a", "d") in got
    assert A("ancestor", "b", "d") in got
    # no spurious reverse edge
    assert A("ancestor", "d", "a") not in got


def test_entails_uses_closure():
    kb = build_kb()
    assert entails(kb, A("ancestor", "a", "d"))
    assert not entails(kb, A("ancestor", "d", "a"))


def test_prove_returns_a_verifiable_certificate():
    kb = build_kb()
    proof = prove(kb, A("ancestor", "a", "d"))
    assert isinstance(proof, Proof)
    assert proof.atom == A("ancestor", "a", "d")
    assert verify(proof, kb)
    assert "anc-step" in str(proof)


def test_prove_unknown_returns_none():
    assert prove(build_kb(), A("ancestor", "d", "a")) is None


def test_holds_positive_and_negative():
    kb = build_kb()
    kb.add_negation(A("parent", "d", "a"))
    assert holds(kb, Literal(A("ancestor", "a", "d")))
    assert not holds(kb, Literal(A("ancestor", "d", "a")))
    # a negative literal is only ever checked in the side table
    assert holds(kb, Literal(A("parent", "d", "a"), negated=True))
    assert not holds(kb, Literal(A("parent", "a", "b"), negated=True))


def test_closure_terminates_on_a_recursive_rule():
    kb = KnowledgeBase().add_fact(A("p", "a"))
    kb.add_rule(Rule(Atom("p", (Var("x"),)), (Atom("p", (Var("x"),)),)))
    assert closure(kb) == {A("p", "a")}


# -- prove completeness (regression: a loop check used to miss valid proofs) --
def test_prove_handles_repeated_derived_conjunct():
    kb = KnowledgeBase().add_fact(A("s", "a"))
    kb.add_rule(Rule(Atom("r", (Var("x"),)), (Atom("s", (Var("x"),)),)))
    kb.add_rule(
        Rule(
            Atom("h", ()),
            (Atom("r", (Const("a"),)), Atom("r", (Const("a"),))),
        )
    )
    assert entails(kb, Atom("h", ()))
    proof = prove(kb, Atom("h", ()))
    assert proof is not None and verify(proof, kb)


def test_prove_is_complete_on_cyclic_data():
    # A path-based loop check rejects ancestor(a,a) here; support-based proof
    # must find it (the least fixpoint contains it).
    kb = KnowledgeBase()
    kb.add_fact(A("parent", "a", "b"))
    kb.add_fact(A("parent", "b", "a"))
    kb.add_rule(Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("x"), Var("y"))),)))
    kb.add_rule(
        Rule(
            Atom("ancestor", (Var("x"), Var("z"))),
            (Atom("parent", (Var("x"), Var("y"))), Atom("ancestor", (Var("y"), Var("z")))),
        )
    )
    assert entails(kb, A("ancestor", "a", "a"))
    proof = prove(kb, A("ancestor", "a", "a"))
    assert proof is not None and verify(proof, kb)


def test_prove_agrees_with_entails_on_every_derived_atom():
    kb = build_kb()
    for atom in closure(kb):
        proof = prove(kb, atom)
        assert proof is not None and verify(proof, kb)


def test_prove_non_ground_abstains():
    assert prove(build_kb(), Atom("ancestor", (Const("a"), Var("y")))) is None