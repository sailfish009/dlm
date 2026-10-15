"""Tests for recursive self-supervised learning (dlm.recursive, v0.0055)."""
from __future__ import annotations

from dlm.recursive import (edges_of, level_rules, one_shot, reachability,
                           recurse)


CHAIN = [(f"n{i}", f"n{i + 1}") for i in range(10)]


def test_reachability_matches_chain_transitive_closure():
    truth = reachability(CHAIN)
    assert (("n0", "n5") in truth) and (("n5", "n0") not in truth)
    assert len(truth) == 55  # 11 nodes (n0..n10), all forward pairs


def test_recurse_is_sound_and_complete():
    r = recurse(CHAIN)
    truth = reachability(CHAIN)
    assert r.relation <= truth
    assert r.relation == truth
    assert r.fixed


def test_recurse_grows_then_reaches_fixpoint():
    r = recurse(CHAIN)
    assert r.depth > 1
    assert r.rounds[-1].new == 0
    assert all(rd.new > 0 for rd in r.rounds[:-1])


def test_one_shot_is_insufficient():
    assert one_shot(CHAIN) != reachability(CHAIN)


def test_depth_is_logarithmic():
    n = 64
    chain = [(f"x{i}", f"x{i + 1}") for i in range(n)]
    r = recurse(chain)
    # diameter n; Covers 2^k each round, so depth ~ log2(n)+1
    assert r.depth <= (n.bit_length() + 1)


def test_level_rules_shape():
    rules = level_rules("a", "b")
    assert len(rules) == 2
    assert any(len(rule.body) == 1 for rule in rules)   # inherit
    assert any(len(rule.body) == 2 for rule in rules)   # compose


def test_deterministic():
    assert recurse(CHAIN).to_dict() == recurse(CHAIN).to_dict()


def test_experiment_verdicts_all_true():
    from experiments.recursive.run import make_chain, make_dag, run
    for edges in (make_chain(24), make_dag(16)):
        res = run(edges)
        assert res["false_pairs"] == 0
        assert res["verdict_ok"], res["verdict"]