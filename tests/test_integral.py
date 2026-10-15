"""Tests of the v0.0049 integral layer (dlm/integral.py).

Two potentials: the forward integral (the closure, path-independent) with its
kernel-decided debt, and the evidence integral over candidate theories (a
measure, not an objective).  The invariant checks here can only fail if the
integral is implemented wrong.
"""
import math

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure, description_length
from dlm.integral import atom_str, energy, evidence, forward, loss_integral


def _kb_rules():
    x = Var("x")
    kb = KnowledgeBase({Atom("p", (Const("a"),)), Atom("p", (Const("b"),))})
    r = Rule(Atom("q", (x,)), (Atom("p", (x,)),), "r")
    return kb, (r,)


def test_atom_str_is_readable():
    assert atom_str(Atom("calls", (Const("a"), Const("b")))) == "calls(a,b)"
    assert atom_str(Atom("p", ())) == "p"


def test_forward_reaches_all_targets_and_is_sound():
    kb, rules = _kb_rules()
    target = [Atom("q", (Const("a"),)), Atom("q", (Const("b"),))]
    f = forward(kb, rules, target)
    assert f.debt == ()
    assert f.false_assert == 0 and f.sound
    assert f.content_loss == 0


def test_forward_debt_without_rules():
    kb, _ = _kb_rules()
    f = forward(kb, (), [Atom("q", (Const("a"),))])
    assert f.debt == ("q(a)",)
    assert f.content_loss == 1


def test_forward_counts_declared_negatives_as_false_asserts():
    kb, rules = _kb_rules()
    f = forward(kb, rules, [], negatives=[Atom("q", (Const("a"),))])
    assert f.false_assert == 1
    assert not f.sound


def test_closure_is_path_independent():
    kb, rules = _kb_rules()
    k1 = kb.copy()
    for r in rules:
        k1.add_rule(r)
    k2 = kb.copy()
    for r in reversed(rules):
        k2.add_rule(r)
    assert closure(k1) == closure(k2)


def test_loss_integral_trapezoid():
    assert loss_integral([]) == 0.0
    assert loss_integral([2.0]) == 0.0
    assert abs(loss_integral([1.0, 1.0]) - 1.0) < 1e-12
    assert abs(loss_integral([0.0, 2.0, 0.0]) - 2.0) < 1e-12
    assert abs(loss_integral([0.0, 0.0, 0.0]) - 0.0) < 1e-12


def test_energy_is_content_plus_mdl():
    kb, rules = _kb_rules()
    target = [Atom("q", (Const("a"),))]
    assert energy(kb, rules, target, cost=0.0) == 0.0
    assert energy(kb, rules, target, cost=1.0) == float(description_length(rules))


def test_evidence_is_normalized_and_free_energy_bounds_map():
    kb, rules = _kb_rules()
    target = [Atom("q", (Const("a"),)), Atom("q", (Const("b"),))]
    ev = evidence([("with", rules), ("without", ())], kb, target, cost=0.0)
    assert abs(sum(ev.posterior) - 1.0) < 1e-9
    assert ev.free_energy <= ev.map_energy + 1e-12
    assert ev.map_name == "with"
    assert ev.multiplicity_reward > 0.0
    assert ev.losses == (0.0, 2.0)


def test_evidence_twin_theories_reward_is_log_two():
    kb, rules = _kb_rules()
    target = [Atom("q", (Const("a"),))]
    ev = evidence([("t1", rules), ("t2", rules)], kb, target, cost=0.0)
    assert abs(ev.multiplicity_reward - math.log(2)) < 1e-9
    assert abs(ev.posterior[0] - 0.5) < 1e-9 and abs(ev.posterior[1] - 0.5) < 1e-9


def test_evidence_requires_candidates():
    kb, _ = _kb_rules()
    try:
        evidence([], kb, [])
    except ValueError:
        return
    raise AssertionError("empty candidate set must be rejected")