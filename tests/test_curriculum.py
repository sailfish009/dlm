"""Tests for the weakness-targeted curriculum loop (dlm.curriculum, v0.0056)."""
from __future__ import annotations

from dlm import Atom, Const, Rule, Var
from dlm.curriculum import close_with_rules, pick_actionable, run_curriculum


def fact(pred, *args):
    return Atom(pred, tuple(Const(a) for a in args))


def joined_rules(n):
    return tuple(
        Rule(Atom(f"p{i}", (Var("?x"),)),
             (Atom(f"e{i}", (Var("?x"),)), Atom("seed", (Var("?x"),))))
        for i in range(n))


def supply(spot):
    return {"facts": [fact(spot.external[0], "s")], "provenance": {"t": 1}}


BODY = {fact("seed", "s")}


def test_close_with_rules_is_the_kernel_closure():
    closed = close_with_rules(BODY, joined_rules(1))
    assert fact("seed", "s") in closed
    assert fact("p0", "s") not in closed   # e0 missing


def test_loop_resolves_a_weak_spot_from_scratch():
    r = run_curriculum(BODY, joined_rules(1), acquire=supply, external={"e0"})
    assert r.stop == "saturated"
    assert r.ability_after.is_proved("p0")
    assert len(r.rounds) == 1
    assert r.rounds[0].gained == ("p0",)
    assert r.rounds[0].improved


def test_loop_iterates_over_several_weak_spots():
    r = run_curriculum(BODY, joined_rules(3), acquire=supply,
                       external={"e0", "e1", "e2"}, max_rounds=8)
    assert r.stop == "saturated"
    assert [rd.target for rd in r.rounds] == ["p0", "p1", "p2"]
    assert all(r.ability_after.is_proved(f"p{i}") for i in range(3))


def test_abstaining_acquisition_stops_with_named_reason():
    r = run_curriculum(BODY, joined_rules(1), acquire=lambda s: {}, external={"e0"})
    assert r.stop == "acquire_empty"
    assert not r.ability_after.is_proved("p0")
    assert r.rounds[0].stop == "acquire_empty"


def test_no_actionable_when_nothing_external():
    r = run_curriculum(BODY, joined_rules(1), acquire=supply, external=set())
    assert r.stop == "no_actionable"
    assert not r.ability_after.is_proved("p0")


def test_scrambled_content_is_no_progress():
    r = run_curriculum(BODY, joined_rules(1),
                       acquire=lambda s: {"facts": [fact("e0", "WRONG")]},
                       external={"e0"})
    assert r.stop == "no_progress"
    assert not r.ability_after.is_proved("p0")
    assert not r.rounds[0].improved


def test_max_rounds_cap():
    r = run_curriculum(BODY, joined_rules(5), acquire=supply,
                       external={f"e{i}" for i in range(5)}, max_rounds=2)
    assert r.stop == "max_rounds"
    assert len(r.rounds) == 2


def test_min_gain_threshold():
    r = run_curriculum(BODY, joined_rules(1), acquire=supply, external={"e0"},
                       min_gain=2)
    assert r.stop == "no_progress"


def test_custom_query_builder():
    r = run_curriculum(BODY, joined_rules(1), acquire=supply, external={"e0"},
                       query_builder=lambda s: f"ask:{s.target}")
    assert r.rounds[0].query == "ask:p0"


def test_deterministic():
    a = run_curriculum(BODY, joined_rules(3), acquire=supply,
                       external={"e0", "e1", "e2"}).to_dict()
    b = run_curriculum(BODY, joined_rules(3), acquire=supply,
                       external={"e0", "e1", "e2"}).to_dict()
    assert a == b


def test_pick_actionable_skips_non_external():
    r = run_curriculum(BODY, joined_rules(2), acquire=supply, external={"e1"},
                       max_rounds=4)
    # only p1 is actionable; the loop skips the non-external p0 and stops when
    # nothing acquirable is left (p0 remains open, but it is not a web question)
    assert [rd.target for rd in r.rounds] == ["p1"]
    assert r.stop == "no_actionable"