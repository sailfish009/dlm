"""Tests for the IR-TREE as ONE medium for deduction and Lisp (dlm.irlearn, v0.0058)."""
from __future__ import annotations

import os

from dlm.ir import is_form, pattern_key
from dlm.irlearn import (IRTree, canon, forms_of_env, induce_law, ir_patterns,
                         lisp_env, lisp_kernel_agreement, lisp_writes_ir,
                         perceive_ir, recurse, roundtrip, self_learn_ir)
from dlm.lisp import dump, parse

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dlm")
CHAIN = [(f"n{i}", f"n{i + 1}") for i in range(12)]
DAG = [("a", "b"), ("b", "c"), ("c", "d"), ("a", "c"), ("b", "d"),
       ("d", "e"), ("a", "e"), ("e", "f")]


def calls_tree(edges):
    return IRTree(canon(("calls", a, b) for a, b in edges))


def test_ir_tree_is_canonical_and_walkable():
    t = IRTree(canon([("calls", "a", "b"), ("calls", "a", "b"), ("defined", "a")]))
    assert len(t) == 2                      # the duplicate is dropped
    assert t.where("calls") == (("calls", "a", "b"),)
    assert t.heads() == {"calls": 1, "defined": 1}
    assert all(is_form(f) for f in t.forms)
    assert t.feature_set()                      # non-empty vocabulary


def test_perceive_ir_projects_source_to_forms(tmp_path):
    (tmp_path / "m.py").write_text(
        "def helper(x):\n    return x\n\n"
        "def user():\n    return helper(1)\n",
        encoding="utf-8")
    tree = perceive_ir(str(tmp_path))
    assert len(tree) > 0 and all(is_form(f) for f in tree.forms)
    assert {"defined", "calls"} <= set(tree.heads())
    assert tree.where("calls")             # the composable relation is present


def test_induce_law_on_the_tree():
    for edges in (CHAIN, DAG):
        law = induce_law(calls_tree(edges))
        assert law.shape == "compose"
        assert law.false_pos == 0
        assert is_form(law.rule_form) and law.rule_form[0] == "rule"
        best_other = max(tp - fp for s, tp, fp in law.candidates if s != "compose")
        assert (law.true_pos - law.false_pos) > best_other


def test_recursion_improves_and_reaches_closure():
    for edges in (CHAIN, DAG):
        tree = calls_tree(edges)
        law = induce_law(tree)
        rec = recurse(tree, law)
        assert rec.recall >= 0.999 and rec.fixed
        assert all(r.false == 0 for r in rec.rounds)
        assert rec.recall > rec.to_dict()["one_shot_recall"] + 0.1
        assert len(rec.level_trees[-1]) > len(tree)   # the medium grew


def test_lisp_reads_the_same_tree():
    tree = calls_tree(DAG)
    base = forms_of_env(lisp_env(tree), derived=False)
    assert tuple(base.forms) == tuple(tree.forms)


def test_lisp_findall_matches_kernel():
    tree = calls_tree(DAG)
    law = induce_law(tree)
    rec = recurse(tree, law)
    env = lisp_env(tree)
    agree = lisp_kernel_agreement(tree, law, rec, env=env)
    assert agree["one_shot_match"]
    assert agree["final_match"]
    assert agree["kernel_match"]
    assert agree["lisp_levels"] == len(rec.rounds)


def test_roundtrip_exact():
    tree = calls_tree(CHAIN)
    law = induce_law(tree)
    mixed = IRTree(canon(list(tree.forms) + [law.rule_form]))
    rt = roundtrip(mixed)
    assert rt["read_dump_exact"] and rt["projection_exact"]
    for f in mixed.forms:
        assert parse(dump(f))[0] == f


def test_pattern_key_is_alpha_invariant():
    a = ("rule", ("r1", "?a", "?b"), ("calls", "?a", "?c"), ("calls", "?c", "?b"))
    b = ("rule", ("r1", "?x", "?y"), ("calls", "?x", "?z"), ("calls", "?z", "?y"))
    c = ("rule", ("r1", "?a", "?b"), ("calls", "?a", "?b"))
    assert pattern_key(a) == pattern_key(b)
    assert pattern_key(a) != pattern_key(c)
    assert ir_patterns(calls_tree(DAG))


def _make_pkg(tmp_path):
    (tmp_path / "pkg.py").write_text(
        "def a():\n    return b()\n\n"
        "def b():\n    return c()\n\n"
        "def c():\n    return d()\n\n"
        "def d():\n    return 1\n",
        encoding="utf-8")
    return str(tmp_path)


def test_lisp_writes_one_form_into_another():
    env = lisp_env(calls_tree(CHAIN))
    written = lisp_writes_ir(env)
    assert written == ("r1", "probe_a", "probe_b")
    assert is_form(written)
    assert written in forms_of_env(env).forms      # the written form entered the tree


def test_experiment_pipeline_all_ok(tmp_path):
    from experiments.irlearn.run import run
    rep = run(_make_pkg(tmp_path))
    assert rep["all_ok"], rep["verdicts"]
    assert rep["law"]["shape"] == "compose"
    assert rep["recursion"]["recursive_recall"] >= 0.999
    assert rep["lisp"]["final_match"] and rep["lisp"]["kernel_match"]
    assert rep["verdicts"]["medium_grows"]


def test_self_learn_ir_on_real_source_deduction():
    tree = perceive_ir(ROOT)
    law = induce_law(tree)
    rec = recurse(tree, law)
    assert law.shape == "compose" and law.false_pos == 0
    assert rec.recall >= 0.999 and rec.fixed
    assert all(r.false == 0 for r in rec.rounds)
    assert len(rec.level_trees[-1]) > len(tree)


def test_self_learn_ir_deterministic(tmp_path):
    root = _make_pkg(tmp_path)
    a = self_learn_ir(root).to_dict()
    b = self_learn_ir(root).to_dict()
    assert a == b