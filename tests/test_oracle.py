"""Tests for the external evidence channel (module 17)."""
from __future__ import annotations

import pytest

from dlm.oracle import (
    CANDIDATE,
    CERTIFY,
    REJECT,
    Evidence,
    StaticOracle,
    combine,
    decide,
)


def test_negative_counts_rejected():
    with pytest.raises(ValueError):
        Evidence(confirm=-1)


def test_policy_contradiction_rejects_even_with_confirms():
    e = Evidence(confirm=5, contradict=1)
    assert e.decision() == REJECT
    assert decide(e) == REJECT


def test_policy_needs_min_confirm_to_certify_else_candidate():
    assert Evidence(confirm=1).decision(min_confirm=2) == CANDIDATE
    assert Evidence(confirm=2).decision(min_confirm=2) == CERTIFY
    assert Evidence(confirm=1).decision(min_confirm=1) == CERTIFY


def test_absence_is_candidate_not_falsity():
    assert Evidence(unknown=3).decision() == CANDIDATE
    assert Evidence().decision() == CANDIDATE


def test_addition_is_additive_and_dedups_sources():
    a = Evidence(confirm=1, sources=("wikidata",))
    b = Evidence(confirm=1, contradict=0, sources=("wikipedia", "wikidata"))
    total = a + b
    assert total.confirm == 2
    assert total.sources == ("wikidata", "wikipedia")
    assert total.decision() == CERTIFY


def test_combine_pools_channels():
    channels = [Evidence(confirm=1, sources=("a",)), Evidence(confirm=1, sources=("b",))]
    pooled = combine(channels)
    assert pooled.confirm == 2
    assert pooled.sources == ("a", "b")
    assert pooled.decision() == CERTIFY


def test_static_oracle_true_false_silent():
    from dlm.logic import Atom, Const

    t = Atom("p", (Const("a"),))
    f = Atom("p", (Const("b"),))
    oracle = StaticOracle(true_items=[t], false_items=[f], source="s")
    assert oracle.check(t) == Evidence(1, 0, 0, ("s",))
    assert oracle.check(f) == Evidence(0, 1, 0, ("s",))
    other = oracle.check(Atom("p", (Const("z"),)))
    assert other == Evidence(0, 0, 1, ("s",))
    assert other.decision() == CANDIDATE


def test_static_oracle_can_stay_silent():
    oracle = StaticOracle(silent_is_unknown=False)
    from dlm.logic import Atom, Const

    assert oracle.check(Atom("p", (Const("a"),))) == Evidence(0, 0, 0, ("static",))