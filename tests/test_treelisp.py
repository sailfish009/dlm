import pytest

from dlm import (Atom, EvalError, atom_to_ir, episode_ir, evaluate_expr, field,
                 learn_round, new_state, rule_to_ir, run)
from dlm.kernel import Rule


def A(pred, *args):
    return Atom(pred, args)


def state():
    episode = episode_ir("s", {A("edge", "a", "b"), A("edge", "b", "c")},
                         {A("reach", "a", "c")})
    return new_state((episode,))


def test_pure_treelisp_let_match_and_select():
    current = state()
    assert evaluate_expr("x", current, {"x": 3}) == 3
    value = evaluate_expr(
        ("let", ("bindings", ("bind", "x", 3)),
         ("if", ("equal?", "x", 3), ("quote", ("ok",)), ("quote", ("bad",)))),
        current)
    assert value == ("ok",)
    selected = evaluate_expr(
        ("select", ("quote", ("root", ("leaf", "a"), ("leaf", "b"))),
         ("quote", ("leaf", "?x"))), current)
    assert len(selected) == 3


def test_treelisp_tests_but_does_not_assert_rule():
    current = state()
    candidate = rule_to_ir(Rule(A("reach", "?x", "?z"),
                                  (A("edge", "?x", "?y"), A("edge", "?y", "?z"))))
    verdict = evaluate_expr(("test-rule", ("quote", candidate)), current)
    assert field(verdict, "formal")[1] is True
    assert not field(field(current, "theory"), "experience")[1:]
    with pytest.raises(EvalError):
        evaluate_expr(("assert-rule", ("quote", candidate)), current)


def test_step_is_validated_and_committed_by_host():
    current = state()
    result = run("(step 64)", current)
    transition = field(result, "value")[1]
    after = field(result, "state")[1]
    assert transition[0] == "transition"
    assert field(after, "round")[1] == 1
    assert field(field(after, "theory"), "experience")[1:]
    proof = evaluate_expr(("prove", ("quote", atom_to_ir(A("reach", "a", "c")))), after)
    assert field(proof, "status")[1] == "proved"


def test_quoted_transition_cannot_forge_authority():
    current = state()
    valid = learn_round(current, budget=64)
    forged = tuple(("events",) if isinstance(x, tuple) and x[0] == "events" else x
                   for x in valid)
    with pytest.raises(ValueError, match="re-verification"):
        run(("quote", forged), current)


def test_fuel_is_bounded():
    with pytest.raises(EvalError, match="fuel-exhausted"):
        evaluate_expr(("begin", 1, 2, 3), state(), fuel=1)
