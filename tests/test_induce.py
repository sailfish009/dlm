"""Tests for the v0.0018 LGG induction: lgg / variate / space / covers / induce."""
import pytest

from dlm import (
    Atom, Const, KnowledgeBase, Rule, Var,
    Clause, lgg_atoms, variate, literal_space, covers, induce_clauses,
    run_experiment,
)

X, Y, Z = Var("x"), Var("y"), Var("z")


def a(x, y):
    return Atom("ancestor", (Const(x), Const(y)))


def chain(n):
    kb = KnowledgeBase()
    for i in range(n - 1):
        kb.add_fact(Atom("parent", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


# -- lgg / variate --------------------------------------------------------
def test_lgg_shares_equal_columns():
    g = lgg_atoms([a("x", "a"), a("x", "b")])
    assert g.pred == "ancestor" and g.args[0] == Const("x") and isinstance(g.args[1], Var)


def test_lgg_rejects_mixed_predicates():
    with pytest.raises(ValueError):
        lgg_atoms([a("x", "y"), Atom("parent", (Const("x"), Const("y")))])


def test_variate_replaces_constants():
    v = variate(a("x", "y"))
    assert all(isinstance(t, Var) for t in v.args)


# -- literal space --------------------------------------------------------
def test_literal_space_is_deterministic_and_deduped():
    kb = chain(4)
    space = literal_space(kb, a("n0", "n1"), [X, Y], max_arity=2)
    assert space == literal_space(kb, a("n0", "n1"), [X, Y], max_arity=2)
    assert len(space) == len(set(space)) > 0


# -- covers (kernel-checked) ---------------------------------------------
def test_covers_respects_negatives():
    kb = chain(4)
    good = Rule(Atom("ancestor", (X, Y)), (Atom("parent", (X, Y)),), "base")
    pos = [a("n0", "n1"), a("n1", "n2")]
    neg = [a("n1", "n0")]
    assert covers(kb, [good], pos, neg)
    bad = Rule(Atom("ancestor", (X, Y)), (Atom("parent", (Y, X)),), "rev")
    assert not covers(kb, [bad], pos, neg)


# -- induce_clauses -------------------------------------------------------
def test_induce_writes_recursive_and_base_clauses():
    kb = chain(8)
    pos = [a(f"n{i}", f"n{j}") for i in range(6) for j in range(i + 1, 6)]
    neg = [a(f"n{i}", f"n{j}") for i in range(6) for j in range(6) if j <= i]
    clauses = induce_clauses(kb, pos, neg, budget=20000)
    bodies = sorted(len(c.rule.body) for c in clauses)
    assert bodies == [1, 2]
    assert all(isinstance(c, Clause) for c in clauses)
    assert all(0.0 < c.weight <= 1.0 for c in clauses)


def test_induce_is_deterministic():
    kb = chain(8)
    pos = [a(f"n{i}", f"n{j}") for i in range(6) for j in range(i + 1, 6)]
    neg = [a(f"n{i}", f"n{j}") for i in range(6) for j in range(6) if j <= i]
    assert induce_clauses(kb, pos, neg) == induce_clauses(kb, pos, neg)


# -- run_experiment -------------------------------------------------------
def test_run_experiment_reports_ability_and_order():
    r = run_experiment()
    assert r["heldout_positives_proved"] == r["heldout_positives_total"]
    assert r["heldout_negatives_false_assert"] == 0
    assert r["order"]["separated"] is True
    assert r["gate"]["proved"] is True
    assert all(r["theory_roundtrip"].values())


def test_run_experiment_is_deterministic_and_stdlib_only():
    import sys
    assert "torch" not in sys.modules and "numpy" not in sys.modules
    assert run_experiment() == run_experiment()
