"""Tests for the knowledge base (module 4)."""
from __future__ import annotations

import pytest

from dlm.kb import KnowledgeBase
from dlm.logic import Atom, Const, Rule, Var


def P(a, b):
    return Atom("parent", (Const(a), Const(b)))


def test_add_and_query_facts():
    kb = KnowledgeBase().add_fact(P("a", "b")).add_fact(P("b", "c"))
    assert len(kb) == 2
    assert kb.has_fact(P("a", "b"))
    assert not kb.has_fact(P("a", "c"))
    assert set(kb.facts_by_pred("parent")) == {P("a", "b"), P("b", "c")}


def test_facts_must_be_ground():
    kb = KnowledgeBase()
    with pytest.raises(ValueError):
        kb.add_fact(Atom("parent", (Const("a"), Var("x"))))


def test_add_rule_and_index_by_head():
    r = Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("x"), Var("y"))),))
    kb = KnowledgeBase().add_rule(r)
    assert kb.has_rule(r)
    assert kb.rules_by_head("ancestor") == (r,)
    assert kb.rules_by_head("parent") == ()
    assert kb.add_rule(r) is kb and len(kb.rules()) == 1  # idempotent


def test_negation_side_table():
    kb = KnowledgeBase().add_negation(P("a", "b"))
    assert kb.is_negated(P("a", "b"))
    assert not kb.is_negated(P("b", "c"))
    with pytest.raises(ValueError):
        kb.add_negation(Atom("parent", (Const("a"), Var("x"))))


def test_predicates_lists_facts_and_rule_heads():
    kb = KnowledgeBase().add_fact(P("a", "b"))
    rule = Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("x"), Var("y"))),))
    kb.add_rule(rule)
    assert kb.predicates() == ("ancestor", "parent")