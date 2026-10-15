"""Tests of the v0.0049 connection layer (dlm/connection.py).

The claim: under a bounded search, per-rule credit is ORDER-dependent, so the
credit field has nonzero circulation (a connection), while any scalar's gradient
has exactly zero circulation.  These tests pin both sides plus the heuristics'
trust invariant (the executor never touches the kernel).
"""
import math

from dlm import Atom, Const, KnowledgeBase, Rule, Var
from dlm.connection import (Credit, block_circulation, credit, curl, deep_credit,
                            derivation_loss, execute, gauge_shift, holonomy,
                            integrate_credit, scalar_curl)


def _probe():
    x = Var("x")
    facts = {Atom("p", (Const("a"),))}
    r_p = Rule(Atom("q", (x,)), (Atom("p", (x,)),), "r_p")
    r_d = Rule(Atom("q", (x,)), (Atom("deep", (x,)),), "r_deep")
    chain, prev = [], "deep"
    for name in ("d1", "d2", "d3", "d4", "d5"):
        chain.append(Rule(Atom(prev, (x,)), (Atom(name, (x,)),), f"r_{name}"))
        prev = name
    return KnowledgeBase(set(facts)), (r_p, r_d) + tuple(chain), Atom("q", (Const("a"),))


def _field(kb, rules, goal, budget=5):
    def f(x, y):
        tr = execute(kb, rules, [goal], priority={"r_p": x, "r_deep": y},
                     budget=budget, max_depth=32)
        n = credit(tr).net()
        return (float(n.get("r_p", 0)), float(n.get("r_deep", 0)))
    return f


def test_execute_proves_with_enough_budget():
    kb, rules, goal = _probe()
    tr = execute(kb, rules, [goal], budget=100, max_depth=32)
    assert goal in tr.proved
    assert credit(tr).hits.get("r_p") == 1


def test_order_changes_the_bounded_result():
    kb, rules, goal = _probe()
    shallow = execute(kb, rules, [goal], priority={"r_p": 1, "r_deep": 0},
                      budget=5, max_depth=32)
    deep = execute(kb, rules, [goal], priority={"r_p": 0, "r_deep": 1},
                   budget=5, max_depth=32)
    assert goal in shallow.proved
    assert goal not in deep.proved
    assert deep.exhausted


def test_credit_net_is_hits_minus_waste():
    c = Credit({"a": 3, "b": 1}, {"a": 1, "c": 2})
    assert c.net() == {"a": 2, "b": 1, "c": -2}


def test_deep_credit_differs_from_shallow_on_a_dead_branch():
    x = Var("x")
    kb = KnowledgeBase({Atom("p", (Const("a"),))})
    rules = (Rule(Atom("mid", (x,)), (Atom("p", (x,)),), "r_mid"),
             Rule(Atom("top", (x,)), (Atom("mid", (x,)), Atom("gone", (x,))), "r_top"))
    goal = Atom("top", (Const("a"),))
    shallow = credit(execute(kb, rules, [goal], budget=100, max_depth=16))
    deep = deep_credit(kb, rules, [goal], budget=100, max_depth=16)
    assert shallow.hits.get("r_mid") == 1          # locally successful ...
    assert deep.hits == {}                          # ... but on no complete proof
    assert deep.waste.get("r_top") == 1             # the frontier is blamed
    assert shallow.net() != deep.net()


def test_execute_never_touches_the_kernel():
    kb, rules, goal = _probe()
    facts0, rules0 = set(kb.facts), kb.rules
    execute(kb, rules, [goal], budget=50, max_depth=16)
    assert kb.facts == facts0 and kb.rules == rules0


def test_credit_field_has_nonzero_holonomy():
    kb, rules, goal = _probe()
    f = _field(kb, rules, goal)
    cells = [(a, b) for a in (-1.0, 0.0, 1.0) for b in (-1.0, 0.0, 1.0)]
    assert holonomy(f, cells)                       # at least one nonzero plaquette
    assert block_circulation(f, 0.0, 0.0, n=2) != 0.0


def test_scalar_curl_is_identically_zero():
    cells = [(a, b) for a in (-1.0, 0.0, 1.0) for b in (-1.0, 0.0, 1.0)]
    for (a, b) in cells:
        assert abs(scalar_curl(lambda x, y: x * x + y * y, a, b)) < 1e-12
        assert abs(scalar_curl(lambda x, y: 3.0 * x - 2.0 * y + 7.0, a, b)) < 1e-12


def test_curl_is_gauge_invariant():
    kb, rules, goal = _probe()
    f = _field(kb, rules, goal)

    def fg(x, y):
        p = gauge_shift({"r_p": x, "r_deep": y}, 5.0)
        tr = execute(kb, rules, [goal], priority=p, budget=5, max_depth=32)
        n = credit(tr).net()
        return (float(n.get("r_p", 0)), float(n.get("r_deep", 0)))

    cells = [(a, b) for a in (-1.0, 0.0, 1.0) for b in (-1.0, 0.0, 1.0)]
    assert all(abs(curl(f, a, b) - curl(fg, a, b)) < 1e-12 for (a, b) in cells)


def test_integrate_credit_is_a_running_sum():
    out = integrate_credit([Credit({"a": 1}, {"b": 1}), Credit({"b": 2})])
    assert out[-1] == {"a": 1.0, "b": 1.0}


def test_derivation_loss_is_finite_iff_provable():
    x = Var("x")
    kb = KnowledgeBase({Atom("p", (Const("a"),))})
    rules = (Rule(Atom("q", (x,)), (Atom("p", (x,)),), "r"),)
    assert math.isfinite(derivation_loss(kb, rules, [Atom("q", (Const("a"),))]))
    assert math.isinf(derivation_loss(kb, rules, [Atom("q", (Const("z"),))]))