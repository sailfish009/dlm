"""Tests for the trusted axiom store (module 18)."""
from __future__ import annotations

import pytest

from dlm.axiom import (
    TIER_CANDIDATE,
    TIER_EXTERNAL,
    TIER_KERNEL,
    Axiom,
    AxiomStore,
    PromoteError,
)
from dlm.engine import prove
from dlm.kb import KnowledgeBase
from dlm.logic import Atom, Const, Rule, Var
from dlm.oracle import Evidence


def A(pred, *names):
    return Atom(pred, tuple(Const(n) for n in names))


def base_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    kb.add_fact(A("parent", "a", "b"))
    kb.add_fact(A("parent", "b", "c"))
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


def test_candidate_never_enters_a_deduction_kb():
    store = AxiomStore(base=base_kb())
    proposed = A("parent", "a", "z")
    store.propose(proposed, source="reader")
    assert proposed in [ax.item for ax in store.candidates()]
    assert proposed not in store.kb().facts()
    assert proposed not in store.certified_kb().facts()
    with pytest.raises(ValueError):
        store.kb(min_tier=TIER_CANDIDATE)


def test_certified_kb_holds_only_seeds():
    store = AxiomStore(base=base_kb())
    store.propose(A("parent", "x", "y"), source="liar")
    kb = store.certified_kb()
    assert A("parent", "a", "b") in kb.facts()
    assert A("parent", "x", "y") not in kb.facts()
    assert len(kb.rules()) == 2


def test_promote_fact_requires_a_valid_proof():
    store = AxiomStore(base=base_kb())
    goal = A("ancestor", "a", "c")
    proof = prove(store.certified_kb(), goal)
    assert proof is not None
    ax = store.promote_fact(goal, proof)
    assert ax.tier == TIER_KERNEL
    assert ax.certificate is not None
    with pytest.raises(PromoteError):
        store.promote_fact(A("ancestor", "a", "z"), proof)  # proof is for another atom


def test_promotion_cannot_rest_on_a_candidate():
    store = AxiomStore(base=base_kb())
    # A candidate fact that would justify a bogus conclusion.
    store.propose(A("parent", "c", "d"), source="liar")
    bogus = A("ancestor", "a", "d")
    # Build a proof from a *tainted* KB to show verify() would accept if we let it...
    tainted = store.certified_kb()
    tainted.add_fact(A("parent", "c", "d"))
    tainted_proof = prove(tainted, bogus)
    assert tainted_proof is not None
    # ...but the store re-checks against the certified KB, which excludes candidates.
    with pytest.raises(PromoteError):
        store.promote_fact(bogus, tainted_proof)


def test_promote_rule_uses_the_verifier():
    store = AxiomStore(base=base_kb())
    good = Rule(
        Atom("ancestor", (Var("x"), Var("z"))),
        (Atom("parent", (Var("x"), Var("y"))), Atom("parent", (Var("y"), Var("z")))),
        name="two-hop",
    )
    store.promote_rule(good, lambda r: True)
    assert store.provenance(good).tier == TIER_KERNEL

    bad = Rule(Atom("parent", (Var("x"), Var("y"))), (Atom("parent", (Var("y"), Var("x"))),), name="rev")
    with pytest.raises(PromoteError):
        store.promote_rule(bad, lambda r: False)


def test_promote_external_needs_two_confirmations_and_no_contradiction():
    store = AxiomStore(base=base_kb())
    fact = A("capital_of", "france", "paris")
    with pytest.raises(PromoteError):
        store.promote_external(fact, Evidence(confirm=1))
    ax = store.promote_external(fact, Evidence(confirm=2, sources=("wikidata", "wikipedia")))
    assert ax.tier == TIER_EXTERNAL
    assert fact in store.kb().facts()
    assert fact not in store.certified_kb().facts()
    with pytest.raises(PromoteError):
        store.promote_external(A("capital_of", "france", "lyon"), Evidence(confirm=5, contradict=1))


def test_axiom_kind_is_validated():
    with pytest.raises(TypeError):
        Axiom("fact", Rule(Atom("p", (Var("x"),)), (Atom("q", (Var("x"),)),)), TIER_KERNEL, "s")
    with pytest.raises(ValueError):
        Axiom("bogus", A("p", "a"), TIER_KERNEL, "s")


def test_provenance_and_summary():
    store = AxiomStore(base=base_kb())
    store.propose(A("parent", "a", "z"), source="reader", detail="guess")
    ax = store.provenance(A("parent", "a", "z"))
    assert ax is not None and ax.source == "reader"
    summary = store.summary()
    assert summary["total"] == 5  # 2 facts + 2 rules + 1 candidate
    assert summary["by_tier"][TIER_CANDIDATE] == 1
    assert summary["by_tier"][TIER_KERNEL] == 4