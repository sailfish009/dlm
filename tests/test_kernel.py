"""Tests for the re-checkable certificate / trusted kernel (module 6)."""
from __future__ import annotations

from dlm.engine import prove
from dlm.kb import KnowledgeBase
from dlm.kernel import Proof, verify
from dlm.logic import Atom, Const, Rule, Var


def A(pred, *names):
    return Atom(pred, tuple(Const(n) for n in names))


def base_kb() -> KnowledgeBase:
    kb = KnowledgeBase().add_fact(A("parent", "a", "b"))
    kb.add_rule(Rule(
        Atom("ancestor", (Var("x"), Var("y"))),
        (Atom("parent", (Var("x"), Var("y"))),),
        name="anc-base",
    ))
    return kb


def test_verify_accepts_a_fact_leaf():
    kb = base_kb()
    assert verify(Proof(A("parent", "a", "b")), kb)


def test_verify_rejects_unknown_fact():
    assert not verify(Proof(A("parent", "a", "z")), base_kb())


def test_verify_accepts_a_rule_node():
    kb = base_kb()
    proof = Proof(
        A("ancestor", "a", "b"),
        kb.rules()[0],
        (Proof(A("parent", "a", "b")),),
    )
    assert verify(proof, kb)


def test_verify_rejects_rule_not_in_kb():
    kb = base_kb()
    foreign = Rule(
        Atom("ancestor", (Var("x"), Var("y"))),
        (Atom("parent", (Var("y"), Var("x"))),),
        name="foreign",
    )
    proof = Proof(
        A("ancestor", "b", "a"),
        foreign,
        (Proof(A("parent", "a", "b")),),
    )
    assert not verify(proof, kb)


def test_verify_rejects_wrong_premise():
    kb = base_kb()
    kb.add_fact(A("parent", "b", "c"))
    # conclusion ancestor(a,b) but the premise is a different, real fact.
    proof = Proof(
        A("ancestor", "a", "b"),
        kb.rules()[0],
        (Proof(A("parent", "b", "c")),),
    )
    assert not verify(proof, kb)


def test_verify_rejects_wrong_arity_of_premises():
    kb = base_kb()
    proof = Proof(A("ancestor", "a", "b"), kb.rules()[0], ())
    assert not verify(proof, kb)


def test_verify_rejects_a_non_ground_conclusion():
    kb = base_kb()
    proof = Proof(Atom("ancestor", (Const("a"), Var("y"))), None, ())
    assert not verify(proof, kb)


def test_engine_proof_roundtrips_through_verify():
    kb = base_kb()
    assert verify(prove(kb, A("ancestor", "a", "b")), kb)