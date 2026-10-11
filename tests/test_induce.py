"""Tests for rule induction and lemma extraction (module 19)."""
from __future__ import annotations

from dlm.engine import prove
from dlm.kb import KnowledgeBase
from dlm.logic import Atom, Const, Rule, Var
from dlm.induce import (
    InducedRule,
    _index,
    candidate_rules,
    extract_lemmas,
    ground_substitutions,
    induce_rules,
    lemma_from_proof,
    measure_rule,
    verify_rule,
)


def A(pred, *names):
    return Atom(pred, tuple(Const(n) for n in names))


def V(pred, *terms):
    return Atom(pred, tuple(terms))


X, Y, Z = Var("x"), Var("y"), Var("z")


def transitive_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("a", "b"), ("b", "c"), ("c", "d"), ("a", "c"), ("b", "d"), ("a", "d")]:
        kb.add_fact(A("anc", a, b))
    return kb


def test_ground_substitutions_and_budget():
    kb = transitive_kb()
    index = _index(kb.facts())
    subs = ground_substitutions((V("anc", X, Y), V("anc", Y, Z)), index)
    assert subs is not None and len(subs) == 4
    assert ground_substitutions((V("missing", X, Y),), index) == []
    assert ground_substitutions((V("anc", X, Y), V("anc", Y, Z)), index, limit=1) is None


def test_measure_rule_transitive_is_entailed_inverse_is_refuted():
    kb = transitive_kb()
    trans = measure_rule(kb, Rule(V("anc", X, Z), (V("anc", X, Y), V("anc", Y, Z)), "trans"))
    assert trans.complete and trans.valid and trans.support == 4 and trans.counterexamples == 0
    inv = measure_rule(kb, Rule(V("anc", X, Y), (V("anc", Y, X),), "inv"))
    assert inv.complete and not inv.valid and inv.counterexamples == 6


def test_verify_rule_distinguishes_false_from_indeterminate():
    kb = transitive_kb()
    trans = Rule(V("anc", X, Z), (V("anc", X, Y), V("anc", Y, Z)), "trans")
    assert verify_rule(kb, trans) is True
    assert verify_rule(kb, Rule(V("anc", X, Y), (V("anc", Y, X),), "inv")) is False
    # Budget too small -> indeterminate, which is neither True nor False.
    assert verify_rule(kb, trans, max_instances=1) is None


def test_candidate_rules_are_bounded_by_vocabulary():
    kb = transitive_kb()
    rules = candidate_rules(kb)
    names = {r.name for r in rules}
    assert "anc_trans" in names
    assert "anc_inv" in names
    # a predicate absent from the facts never appears
    assert not any("missing" in n for n in names)
    assert len(rules) == len(set(rules))


def test_induce_rules_keeps_supported_candidates_and_ranks_them():
    kb = KnowledgeBase()
    for a, b in [("a", "b"), ("b", "c"), ("c", "d"), ("a", "c")]:
        kb.add_fact(A("p", a, b))
    # p(a,b)&p(b,c) -> p(a,c) holds; p(b,c)&p(c,d) -> p(b,d) and
    # p(a,c)&p(c,d) -> p(a,d) do not.
    found = induce_rules(kb)
    trans = [ir for ir in found if ir.rule.name == "p_trans"]
    assert len(trans) == 1
    assert isinstance(trans[0], InducedRule)
    assert trans[0].support == 1 and trans[0].counterexamples == 2
    assert not trans[0].sound
    # With a zero-counterexample cap the refuted rule disappears.
    assert all(ir.sound for ir in induce_rules(kb, max_counterexamples=0))


def test_lemma_from_proof_and_extract_lemmas():
    kb = KnowledgeBase()
    kb.add_fact(A("parent", "a", "b"))
    kb.add_fact(A("parent", "b", "c"))
    kb.add_rule(Rule(V("ancestor", X, Y), (V("parent", X, Y),), name="anc-base"))
    kb.add_rule(
        Rule(
            V("ancestor", X, Z),
            (V("parent", X, Y), V("ancestor", Y, Z)),
            name="anc-step",
        )
    )
    proof = prove(kb, A("ancestor", "a", "c"))
    assert proof is not None
    lemma = lemma_from_proof(proof, kb)
    assert isinstance(lemma, Rule)
    assert lemma not in kb.rules()
    assert verify_rule(kb, lemma) is True

    lemmas = extract_lemmas(kb)
    assert lemmas and all(verify_rule(kb, r) is True for r in lemmas)
    assert all(r not in kb.rules() for r in lemmas)


def test_lemma_from_fact_proof_is_none():
    kb = KnowledgeBase()
    kb.add_fact(A("p", "a", "b"))
    proof = prove(kb, A("p", "a", "b"))
    assert proof is not None
    assert lemma_from_proof(proof, kb) is None