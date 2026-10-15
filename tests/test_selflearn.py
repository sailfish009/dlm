"""Tests for self-supervised learning on the model's own source (dlm.selflearn, v0.0057)."""
from __future__ import annotations

import os

from dlm import Atom, Const, KnowledgeBase, closure
from dlm.selflearn import (call_graph, ground_reach, grow_vocabulary,
                           induce_composition, perceive_facts, self_learn)

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dlm")
CHAIN = [(f"n{i}", f"n{i + 1}") for i in range(12)]
DAG = [("a", "b"), ("b", "c"), ("c", "d"), ("a", "c"), ("b", "d"),
       ("d", "e"), ("a", "e"), ("e", "f")]


def test_call_graph_is_intrapackage_and_consistent():
    g = call_graph(ROOT)
    assert g.nodes and g.edges
    for a, b in g.edges:
        assert a in g.nodes and b in g.nodes
        assert a != b


def test_induction_recovers_composition_not_distractors():
    for edges in (CHAIN, DAG):
        ind = induce_composition(edges)
        assert ind.shape == "compose"
        assert ind.false_pos == 0
        # the correct law must strictly beat every distractor on tp - fp
        best_other = max(tp - fp for s, tp, fp in ind.candidates if s != "compose")
        assert (ind.true_pos - ind.false_pos) > best_other


def test_self_learn_is_sound_and_complete():
    for edges in (CHAIN, DAG):
        res = self_learn(edges)
        assert res.shape == "compose"
        assert res.relation <= ground_reach(edges)
        assert res.relation == ground_reach(edges)
        assert res.fixed
        assert all(r.false == 0 for r in res.rounds)


def test_recursion_strictly_beats_one_shot():
    for edges in (CHAIN, DAG):
        res = self_learn(edges)
        one = res.one_shot_size / res.ground_size
        assert one < 1.0
        assert res.recall > one + 0.1


def test_grow_vocabulary_grows_the_feature_alphabet():
    facts = set()
    # pairs of features whose intersection is a proper, irredundant concept
    feats = {
        "a": {"s0", "s1", "s2"}, "b": {"s0", "s1", "s3"},
        "c": {"s4", "s5", "s6"}, "d": {"s4", "s5", "s7"},
        "e": {"s2", "s3", "s6"}, "f": {"s2", "s3", "s7"},
    }
    for pred, subs in feats.items():
        for s in subs:
            facts.add(Atom(pred, (Const(s),)))
    res = grow_vocabulary(facts, rounds=3, max_body=2)
    assert res.library
    assert res.rounds[-1].features > res.base_features
    # every invented atom must be kernel-derivable from facts + library
    kb = KnowledgeBase(set(facts))
    for rule in res.library:
        kb.add_rule(rule)
    invented = {a for a in closure(kb) if a.pred.startswith("c")}
    assert invented <= res.facts


def test_vocabulary_is_a_conservative_extension():
    """Invented predicates must not change the closure over the ORIGINAL alphabet."""
    facts = {Atom("p", (Const(s),)) for s in "abcd"}
    facts |= {Atom("q", (Const(s),)) for s in "abef"}
    res = grow_vocabulary(facts, rounds=3, max_body=2)
    base = closure(KnowledgeBase(set(facts), ()))
    kb = KnowledgeBase(set(facts))
    for rule in res.library:
        kb.add_rule(rule)
    original = {a for a in closure(kb) if not a.pred.startswith("c")}
    assert original == base


def test_perceive_facts_is_generic(tmp_path):
    src = tmp_path / "m.py"
    src.write_text(
        "def helper(x):\n    return x\n\n"
        "class K:\n    def method(self):\n        return helper(1)\n\n"
        "def _private():\n    '''doc'''\n    return 1\n",
        encoding="utf-8",
    )
    facts = perceive_facts(str(tmp_path))
    preds = {a.pred for a in facts}
    assert {"defined", "calls", "method", "private", "documented"} <= preds


def test_self_learn_deterministic():
    a = self_learn(CHAIN).to_dict()
    b = self_learn(CHAIN).to_dict()
    assert a == b


def test_experiment_on_own_source_all_ok():
    from experiments.selflearn.run import run
    rep = run(ROOT, rounds=24, max_body=2)
    assert rep["all_ok"], rep["verdicts"]
    assert rep["self_evaluation"]["ability_gain"] > 0.1
    assert rep["self_learn"]["recursive_recall"] >= 0.999