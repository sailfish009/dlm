"""DLM v0.0052 tests: the integral is measured (equal budget, held-out)."""
from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.effective import (brier, close_with, logloss, map_prediction,
                           marginal_prediction, order_by_credit, path_order,
                           positive_set)
from dlm.integral import evidence

from experiments.effective.run import (PREDS, _subsets, multiplicity_probe,
                                       order_domain, part_b, part_c)


def _A(p, x, y):
    return Atom(p, (Const(x), Const(y)))


def test_close_with_is_the_kernel_closure():
    x, y, z = Var("X"), Var("Y"), Var("Z")
    rule = Rule(Atom("p", (x, z)), (Atom("p", (x, y)), Atom("p", (y, z))), "trans")
    kb = KnowledgeBase({_A("p", "a", "b"), _A("p", "b", "c")})
    got = close_with(kb, (rule,))
    manual = closure((lambda k: (k.add_rule(rule), k)[1])(kb.copy()))
    assert frozenset(manual) == got
    assert _A("p", "a", "c") in got


def test_subsets_always_include_the_point_theory():
    x, y = Var("X"), Var("Y")
    rules = tuple(Rule(Atom("p", (x, y)), (Atom(f"q{i}", (x, y)),), f"r{i}")
                  for i in range(4))
    subs = _subsets(rules, 2)              # cap below the full size
    assert rules in subs                   # the point theory must be a candidate
    assert () in subs


def test_marginal_is_a_probability_and_hedges_between_theories():
    x, y = Var("X"), Var("Y")
    g = Rule(Atom("p", (x, y)), (Atom("q", (x, y)),), "g")
    h = Rule(Atom("p", (x, y)), (Atom("r", (x, y)),), "h")
    kb = KnowledgeBase({_A("q", "a", "b")})
    # a fully ambiguous posterior over two theories
    ev = evidence([("g", (g,)), ("h", (h,))], kb, [_A("p", "a", "b")])
    universe = [_A("p", "a", "b")]
    marg = marginal_prediction(ev, [(g,), (h,)], kb, universe)
    assert 0.0 <= marg[_A("p", "a", "b")] <= 1.0
    # the marginal is exactly the posterior mass of theories that derive the atom
    assert abs(marg[_A("p", "a", "b")] - ev.posterior[0]) < 1e-9


def test_brier_and_logloss_zero_for_a_perfect_predictor():
    universe = [_A("p", "a", "b"), _A("p", "a", "c")]
    truth = {_A("p", "a", "b")}
    pred = {_A("p", "a", "b"): 1.0, _A("p", "a", "c"): 0.0}
    assert brier(pred, universe, truth) == 0.0
    assert logloss(pred, universe, truth) < 1e-6
    assert brier({a: 0.5 for a in universe}, universe, truth) == 0.25


def test_positive_set_commits_at_threshold():
    universe = [_A("p", "a", "b"), _A("p", "a", "c")]
    pred = {universe[0]: 0.5, universe[1]: 0.49}
    assert positive_set(pred, 0.5) == {universe[0]}


def test_multiplicity_probe_strict_win():
    m = multiplicity_probe()
    assert m["verdict"]["multiplicity_energy_tie"]
    assert m["verdict"]["map_commits_to_wrong_theory"]
    assert m["verdict"]["evidence_strictly_beats_map_under_multiplicity"]
    assert all(m["verdict"].values())


def test_order_by_credit_ranks_the_useful_rule_first():
    from dlm.connection import deep_credit
    kb, rules, goals = order_domain(n=8, trap=5)
    cr = deep_credit(kb, rules, goals, budget=5000, max_depth=64)
    prio = order_by_credit(rules, cr)
    assert prio["z_cheap"] > 0
    assert prio["z_cheap"] > max(prio[f"a_trap{j:02d}"] for j in range(1, 6))


def test_path_order_improves_with_equal_test_budget():
    kb, rules, goals = order_domain(n=12, trap=6)
    path = path_order(kb, rules, goals, rounds=3, probe_budget=5000, eval_budget=20)
    assert path.first_proved < len(goals)
    assert path.final_proved == len(goals)
    assert path.final_proved > path.first_proved


def test_part_c_budget_effectiveness():
    c = part_c([0])
    assert all(c["verdict"].values()), c["verdict"]


def test_part_b_evidence_not_worse_than_map():
    b = part_b([0], max_subset=2)
    assert b["verdict"]["candidates_include_point_theory"]
    assert b["verdict"]["evidence_marginal_not_worse_than_map"]
    assert b["verdict"]["evidence_committed_sound"]
    assert PREDS  # the universe covers every domain predicate