"""DLM v0.0039 tests: label-free abstraction is conservative and compresses."""
from dlm import Atom, Rule, Var, closure, KnowledgeBase
from dlm.abstract import (theory_dl, closure_preserved, closure_budget,
                          common_body_patterns, mined_subforms, abstract_theory)
from dlm.lisp import rule_to_form
from experiments.abstract.run import build


def test_abstraction_compresses_and_preserves_closure():
    rules, facts = build(6, 4)
    res = abstract_theory(rules, facts, min_support=2, max_pattern=4)
    assert res.compression_gain > 0
    assert theory_dl(res.theory) == res.dl_after < res.dl_before
    assert closure_preserved(facts, rules, res.theory)
    assert res.abstractions and any(a.support >= 2 and a.uses >= 2
                                    for a in res.abstractions)


def test_interface_bug_would_break_closure():
    # a non-conservative "abstraction" must be rejected by the kernel check
    rules, facts = build(4, 4)
    weak = Rule(Atom("h0", (Var("?x"), Var("?z"))),
                (Atom("edge", (Var("?x"), Var("?z"))),))
    assert not closure_preserved(facts, rules, tuple(rules) + (weak,))


def test_common_body_patterns_finds_shared_core():
    rules, _ = build(6, 4)
    groups = common_body_patterns(rules, min_support=2, max_pattern=4)
    assert groups
    full = [v for v in groups.values() if len(v[0][2]) == 4]
    assert full and len({ri for ri, *_ in full[0]}) == 6


def test_mined_subforms_library():
    rules, _ = build(4, 3)
    subs = mined_subforms([rule_to_form(r) for r in rules], min_support=2)
    assert subs and subs[0][1] >= 2


def test_abstraction_is_deterministic_and_budget_helps():
    rules, facts = build(6, 4)
    res = abstract_theory(rules, facts)
    assert res == abstract_theory(rules, facts)
    target = closure(KnowledgeBase(set(facts), tuple(rules)))
    base = closure_budget(KnowledgeBase(set(facts), tuple(rules)), 800) & target
    abst = closure_budget(KnowledgeBase(set(facts), res.theory), 800) & target
    assert len(abst) > len(base)                 # shorter theory covers more first