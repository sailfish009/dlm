"""Tests for dlm.generalize -- corpus-level concept induction + deductive transfer."""
from __future__ import annotations

from dlm import Atom, Const, KnowledgeBase, Var, closure
from dlm.generalize import (
    concept_instances,
    induce_concepts,
    subject_features,
    transfer,
)


def A(pred, *args):
    return Atom(pred, tuple(Const(a) for a in args))


def facts(*atoms):
    return set(atoms)


def test_subject_features_groups_by_arg0():
    f = facts(A("p", "a", "x"), A("q", "a"), A("p", "b", "y"))
    sf = subject_features(f)
    assert set(sf) == {"a", "b"}
    assert ("p", ("x",)) in sf["a"] and ("q", ()) in sf["a"]
    assert ("q", ()) not in sf["b"]


def test_induce_finds_nondegenerate_irredundant_concept():
    # p1={a,b,c}  p2={a,b,d}  p3={b,c}
    f = facts(A("p1", "a"), A("p1", "b"), A("p1", "c"),
              A("p2", "a"), A("p2", "b"), A("p2", "d"),
              A("p3", "b"), A("p3", "c"))
    rep = induce_concepts(f, min_support=2, max_body=2, max_concepts=9)
    bodies = {tuple(sorted(c.body)) for c in rep.concepts}
    assert ((("p1", ()), ("p2", ()))) in bodies
    # the degenerate p1&p3 == p3 must NOT be invented
    assert all(len(c.body) >= 2 for c in rep.concepts)
    c0 = [c for c in rep.concepts if set(c.body) == {("p1", ()), ("p2", ())}][0]
    assert c0.support == 2
    assert concept_instances(c0, f) == ["a", "b"]


def test_single_program_is_degenerate():
    # on one subject, every conjunction that holds is implied by a single feature
    f = facts(A("trains", "main"), A("backprops", "main"), A("optimizes", "main"))
    rep = induce_concepts(f, min_support=1, max_body=3, max_concepts=9)
    assert rep.concepts == ()


def test_redundant_feature_is_excluded():
    # p and q have identical extensions -> any conjunction equals a single one
    f = facts(A("p", "a"), A("p", "b"), A("q", "a"), A("q", "b"))
    rep = induce_concepts(f, min_support=2, max_body=2, max_concepts=9)
    assert rep.concepts == ()


def test_transfer_derives_on_held_out_by_deduction():
    f = facts(A("p1", "a"), A("p1", "b"), A("p1", "c"),
              A("p2", "a"), A("p2", "b"), A("p2", "d"),
              A("p3", "b"), A("p3", "c"))
    rep = induce_concepts(f, min_support=2, max_body=2, max_concepts=9)
    held = facts(A("p1", "z"), A("p2", "z"), A("p1", "w"))
    tr = transfer(rep.concepts, held)
    concept = [c for c in rep.concepts if set(c.body) == {("p1", ()), ("p2", ())}][0]
    assert tr[concept.name]["hits"] == 1
    assert tr[concept.name]["subjects"] == ["z"]


def test_invented_rule_is_definitional_over_original_vocabulary():
    f = facts(A("p1", "a"), A("p1", "b"), A("p1", "c"),
              A("p2", "a"), A("p2", "b"), A("p2", "d"),
              A("p3", "b"), A("p3", "c"))
    rep = induce_concepts(f, min_support=2, max_body=2, max_concepts=9)
    vocab = {"p1", "p2", "p3"}
    base = KnowledgeBase(set(f))
    with_rules = KnowledgeBase(set(f))
    for c in rep.concepts:
        with_rules.add_rule(c.rule)
    before = {a for a in closure(base) if a.pred in vocab}
    after = {a for a in closure(with_rules) if a.pred in vocab}
    assert before == after


def test_induce_is_deterministic():
    f = facts(A("p1", "a"), A("p1", "b"), A("p1", "c"),
              A("p2", "a"), A("p2", "b"), A("p2", "d"),
              A("p3", "b"), A("p3", "c"))
    r1 = induce_concepts(f, min_support=2, max_body=2, max_concepts=9)
    r2 = induce_concepts(f, min_support=2, max_body=2, max_concepts=9)
    assert r1.to_dict() == r2.to_dict()