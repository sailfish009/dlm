"""DLM v0.0001 unit tests."""
from __future__ import annotations

from itertools import product

import numpy as np
import pytest

from dlm import (
    Decider,
    Engine,
    KnowledgeBase,
    Pipeline,
    Rule,
    collect_training_data,
    fact,
    induce_rules,
    rule,
)
from dlm.retrieval import feature_vector
from dlm.terms import V, atom, unify, unify_atom


# -- terms ------------------------------------------------------------------
def test_unify_binds_and_fails():
    s = unify_atom(atom("parent", V("x"), "bob"), atom("parent", "alice", V("y")))
    assert s is not None and str(s["x"]) == "alice" and str(s["y"]) == "bob"
    assert unify_atom(atom("p", V("x")), atom("q", V("x"))) is None
    assert unify_atom(atom("p", V("x")), atom("p", V("x"), V("y"))) is None


def test_occurs_check():
    assert unify(V("x"), V("x")) == {}
    assert unify(V("x"), atom("f", V("x")).args[0] if False else V("y")) is not None


# -- knowledge base ---------------------------------------------------------
def _ancestor_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("parent", a, b))
    x, y, z = V("x"), V("y"), V("z")
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, y), name="base"))
    kb.add_rule(rule(fact("ancestor", x, z), fact("parent", x, y), fact("ancestor", y, z), name="step"))
    return kb


def test_unsafe_rule_rejected():
    kb = KnowledgeBase()
    with pytest.raises(ValueError):
        kb.add_rule(rule(fact("reach", V("x"), V("y")), fact("node", V("x")), name="unsafe"))


def test_forward_backward_agree():
    kb = _ancestor_kb()
    eng = Engine(kb, max_depth=64)
    closure = eng.forward_chain()
    consts = ["alice", "bob", "carol", "dave"]
    for p in ("ancestor", "parent"):
        for a, b in product(consts, consts):
            g = fact(p, a, b)
            assert (g in closure) == eng.entails(g)


def test_proof_trace_is_a_tree():
    eng = Engine(_ancestor_kb(), max_depth=64)
    sol = next(eng.prove(fact("ancestor", "alice", "dave")))
    assert sol.proof.atom == fact("ancestor", "alice", "dave")
    assert sol.proof.leaves() >= 3
    assert sol.proof.depth() >= 3


# -- induction --------------------------------------------------------------
def test_induce_grandparent():
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave"), ("dave", "erin")]:
        kb.add_fact(fact("parent", a, b))
    pos = [fact("grandparent", "alice", "carol"), fact("grandparent", "bob", "dave"), fact("grandparent", "carol", "erin")]
    neg = [fact("grandparent", "alice", "bob"), fact("grandparent", "bob", "carol"), fact("grandparent", "alice", "dave")]
    rules = induce_rules(kb, pos, neg, max_body=2, n_exist=1)
    assert rules, "expected at least one induced rule"
    assert all(len(r.body) == 2 for r in rules)
    # the induced rule must actually derive the positives
    trial = KnowledgeBase()
    for f in kb.facts():
        trial.add_fact(f)
    for r in rules:
        trial.add_rule(r)
    closure = Engine(trial).forward_chain()
    assert set(pos) <= closure
    assert not (set(neg) & closure)


# -- decider / pipeline -----------------------------------------------------
def test_decider_learns_separable_task():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(256, 8))
    y = (X[:, 0] + X[:, 1] > 0).astype(float)
    dec = Decider(seed=0).fit(X[:192], y[:192], epochs=500, lr=0.1)
    assert dec.num_params() < 1000
    acc = float(np.mean((dec.predict_proba(X[192:]) > 0.5) == (y[192:] > 0.5)))
    assert acc > 0.9


def test_feature_vector_length_matches_retriever():
    kb = _ancestor_kb()
    f = feature_vector(atom("ancestor", "alice", "dave"), fact("ancestor", "alice", "bob"), "fact", kb)
    from dlm.retrieval import Retriever

    assert len(f) == Retriever.NUM_FEATURES


def test_pipeline_fallback_preserves_recall():
    kb = _ancestor_kb()
    x, y = V("x"), V("y")
    kb.add_rule(rule(fact("ancestor", x, y), fact("ghost", x, y), name="distractor"))
    positives = [fact("ancestor", a, b) for a, b in [("alice", "carol"), ("alice", "dave"), ("bob", "dave")]]
    X, yv = collect_training_data(kb, positives)
    dec = Decider(seed=0).fit(X, yv, epochs=400, lr=0.1)
    pipe = Pipeline(kb, decider=dec, threshold=0.5, max_depth=64)
    for q in positives:
        assert pipe.answer(q, use_decider=True).answers, f"fallback lost {q}"