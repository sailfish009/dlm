"""Tests for ability self-evaluation (dlm.ability, v0.0056)."""
from __future__ import annotations

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.ability import (ability_profile, improvement, rule_heads,
                         target_predicates, weak_spots)


def fact(pred, *args):
    return Atom(pred, tuple(Const(a) for a in args))


def rule(head, *body):
    return Rule(Atom(head, (Var("?x"),)), tuple(Atom(b, (Var("?x"),)) for b in body))


R_A = rule("a", "b")                       # a :- b
R_C = rule("c", "a", "d")                  # c :- a, d
RULES = (R_A, R_C)


def closed_with(*extra):
    kb = KnowledgeBase({fact("b", "1")})
    for r in RULES:
        kb.add_rule(r)
    for f in extra:
        kb.add_facts({f})
    return closure(kb)


def profile(closed, external=("d",), facts=None, targets=None, evidence=None):
    return ability_profile(RULES, closed, facts=facts or {fact("b", "1")},
                           external=external, targets=targets, evidence=evidence)


def test_rule_heads_and_target_predicates():
    assert rule_heads(RULES) == ("a", "c")
    assert target_predicates(RULES, [fact("b", "1")]) == ("a", "b", "c")


def test_proved_target_from_closure_only():
    ab = profile(closed_with())
    assert ab.is_proved("a")           # a :- b, b given
    assert not ab.is_proved("c")
    assert "c" in ab.open


def test_blocked_and_external_premise():
    ab = profile(closed_with())
    assert ab.blocked["c"] == ("d",)
    assert ab.external["c"] == ("d",)
    assert ab.actionable == ("c",)


def test_weak_spots_order_actionable_first():
    ab = profile(closed_with(), targets=("c", "ghost"))
    spots = weak_spots(ab)
    assert spots[0].target == "c" and spots[0].actionable
    ghost = [s for s in spots if s.target == "ghost"][0]
    assert ghost.kind == "absent" and not ghost.actionable


def test_improvement_gained_and_deepened():
    before = profile(closed_with())
    after = profile(closed_with(fact("d", "1")))
    imp = improvement(before, after)
    assert imp["gained"] == ("c",)
    assert imp["improved"]


def test_scrambled_fact_is_not_improvement():
    before = profile(closed_with())
    after = profile(closed_with(fact("d", "2")))   # wrong entity, c never fires
    imp = improvement(before, after)
    assert imp["gained"] == ()
    assert not imp["improved"]


def test_evidence_recall_and_false_asserts():
    ab = profile(closed_with(),
                 evidence={"positives": {fact("c", "1")},
                           "negatives": {fact("c", "2")}})
    assert ab.evidence["recall"] == 0.0
    assert ab.evidence["false_negatives"] == [str(fact("c", "1"))]
    assert ab.evidence["false_asserts"] == []


def test_deterministic():
    a = profile(closed_with(fact("d", "1"))).to_dict()
    b = profile(closed_with(fact("d", "1"))).to_dict()
    assert a == b