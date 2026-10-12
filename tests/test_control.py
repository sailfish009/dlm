"""Tests for goal-conditioned execution control (dlm/control.py, v0.0028)."""
from __future__ import annotations

from dlm import Atom, Clause, Const, KnowledgeBase, Rule, Theory, Var
from dlm.control import (
    ControlScorer,
    EpisodicMemory,
    context_features,
    control_execute,
    examples_from_execution,
    goal_signature,
    rank_clauses,
    train_control,
)
from dlm.execute import check_sound, execute


# -- a routing fixture: even edges are `a`, odd edges are `b` --------------
def _kb(n: int = 10) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(n - 1):
        kb.add_fact(Atom("a" if i % 2 == 0 else "b", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _theory() -> Theory:
    x, y = Var("x"), Var("y")
    c_a = Clause(Rule(Atom("t", (x, y)), (Atom("a", (x, y)),), "c_a"), 0.0)
    c_b = Clause(Rule(Atom("t", (x, y)), (Atom("b", (x, y)),), "c_b"), 0.0)
    return Theory("routing", (c_a, c_b))


def _t(i: int) -> Atom:
    return Atom("t", (Const(f"n{i}"), Const(f"n{i + 1}")))


# -- context features ------------------------------------------------------
def test_goal_signature_is_constant_free():
    assert goal_signature(_t(0)) == "t/2/c.c"
    x = Var("x")
    assert "s0" in goal_signature(Atom("t", (x, x)))  # shared variable is recorded
    assert goal_signature(Atom("t", (x, Const("c")))).endswith("s0.c")


def test_context_features_are_goal_conditioned_and_deterministic():
    kb = _kb()
    theory = _theory()
    c_a, c_b = theory.clauses
    f_even = context_features(kb, _t(0), c_a)  # n0-n1 is an `a` fact
    f_even_other = context_features(kb, _t(0), c_b)
    f_odd = context_features(kb, _t(1), c_a)  # n1-n2 is a `b` fact
    assert "sup:a" in f_even and "unsup:b" in f_even_other
    assert "unsup:a" in f_odd
    # the SAME clause has different features for different goals -> goal conditioning
    assert f_even != f_odd
    assert context_features(kb, _t(0), c_a) == f_even  # deterministic
    assert list(f_even) == sorted(f_even)  # sorted


def test_zero_scorer_equals_the_frozen_name_order():
    kb = _kb()
    theory = _theory()
    goals = [_t(0), _t(1), _t(2)]
    frozen = execute(kb, theory, goals, budget=100, order="name")
    control = control_execute(kb, theory, goals, ControlScorer(), budget=100, order="name")
    assert control.proved == frozen.proved
    assert control.spent == frozen.spent


# -- the scorer only orders -------------------------------------------------
def test_control_execute_is_sound_and_does_not_mutate_the_theory():
    kb = _kb()
    theory = _theory()
    before = theory.weights()
    model = ControlScorer({"nsup=1": 1.0, "nsup=0": -1.0})
    ex = control_execute(kb, theory, [_t(0), _t(1)], model, budget=100)
    assert check_sound(kb, theory, ex)
    assert theory.weights() == before  # ordering never edits the model
    assert ex.proved == (_t(0), _t(1))


def test_rank_clauses_is_descending_and_tie_breaks_by_name():
    kb = _kb()
    theory = _theory()
    ranked = rank_clauses(kb, _t(0), theory, ControlScorer())
    assert ranked == (("c_a", 0.0), ("c_b", 0.0))  # tie -> name
    ranked2 = rank_clauses(kb, _t(0), theory, ControlScorer({"sup:a": 2.0}))
    assert ranked2[0] == ("c_a", 2.0)


# -- learning the routing ---------------------------------------------------
def test_train_control_learns_a_goal_conditioned_scorer():
    kb = _kb()
    theory = _theory()
    train = [_t(0), _t(1), _t(2), _t(3)]
    trace = execute(kb, theory, train, budget=10 ** 6, order="name")
    examples = examples_from_execution(kb, theory, trace)
    assert any(label == 1 for _, _, label in examples)
    assert any(label == -1 for _, _, label in examples)
    model, updates = train_control(ControlScorer(), examples, kb=kb, epochs=8, lr=0.1)
    assert updates > 0
    assert model.weights.get("sup:a", 0.0) > 0
    assert model.weights.get("unsup:a", 0.0) < 0


def test_goal_conditioned_beats_every_global_order_under_a_tight_budget():
    kb = _kb()
    theory = _theory()
    train = [_t(0), _t(1), _t(2), _t(3)]
    held = [_t(4), _t(5)]
    trace = execute(kb, theory, train, budget=10 ** 6, order="name")
    model, _ = train_control(
        ControlScorer(), examples_from_execution(kb, theory, trace), kb=kb, epochs=8, lr=0.1
    )
    budget = len(held)  # one wrong clause attempt already exhausts it
    global_fixed = execute(kb, theory, held, budget=budget, order="name")
    control = control_execute(kb, theory, held, model, budget=budget)
    assert global_fixed.coverage < control.coverage
    assert control.coverage == 1.0


# -- episodic memory --------------------------------------------------------
def test_episodic_memory_records_and_replays_credit():
    kb = _kb()
    theory = _theory()
    # all-odd goals: one regime, so the coarse signature is unambiguous
    ex = execute(kb, theory, [_t(1), _t(3)], budget=100, order="name")
    memory = EpisodicMemory().observe(ex)
    assert memory.size >= 2
    assert memory.recall(_t(1), "c_b") > 0  # c_b closed the proof
    assert memory.recall(_t(1), "c_a") < 0  # c_a only spent budget
    merged = EpisodicMemory().merge(memory)
    assert merged.recall(_t(1), "c_b") == memory.recall(_t(1), "c_b")


def test_memory_feature_appears_in_context_features():
    kb = _kb()
    theory = _theory()
    ex = execute(kb, theory, [_t(0), _t(1)], budget=100, order="name")
    memory = EpisodicMemory().observe(ex)
    feats = context_features(kb, _t(1), theory.clauses[0], memory)
    assert any(f.startswith("memo=") for f in feats)
    assert "memo=pos" in context_features(kb, _t(1), theory.clauses[1], memory)


def test_memory_routes_across_new_constants_one_regime():
    # a decoy problem: one predicate, one true clause and one silent decoy.
    # memory keyed by the constant-free signature transfers to NEW constants.
    x, y, z = Var("x"), Var("y"), Var("z")
    kb = KnowledgeBase()
    for i in range(20):
        kb.add_fact(Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    true = Clause(Rule(Atom("t", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y))), "ztrue"), 0.0)
    decoy = Clause(
        Rule(Atom("t", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y)), Atom("e", (z, z))), "adecoy"),
        0.0,
    )
    theory = Theory("mem", (true, decoy))
    first = [Atom("t", (Const(f"n{i}"), Const(f"n{i + 2}"))) for i in range(0, 8, 2)]
    ex = execute(kb, theory, first, budget=100, order="name")
    memory = EpisodicMemory().observe(ex)
    scorer = ControlScorer({"memo=pos": 1.0, "memo=neg": -1.0})
    fresh = [Atom("t", (Const(f"n{i}"), Const(f"n{i + 2}"))) for i in range(10, 16, 2)]
    ex2 = control_execute(kb, theory, fresh, scorer, memory=memory, budget=100, order="score")
    assert check_sound(kb, theory, ex2)
    assert ex2.spent == len(fresh)  # one attempt per goal: memory routes it


def test_control_scorer_and_memory_are_deterministic():
    kb = _kb()
    theory = _theory()
    train = [_t(i) for i in range(4)]
    trace = execute(kb, theory, train, budget=10 ** 6, order="name")
    examples = examples_from_execution(kb, theory, trace)
    m1, u1 = train_control(ControlScorer(), examples, kb=kb, epochs=8, lr=0.1)
    m2, u2 = train_control(ControlScorer(), examples, kb=kb, epochs=8, lr=0.1)
    assert m1 == m2 and u1 == u2
    mem = EpisodicMemory().observe(trace)
    assert mem.to_dict() == EpisodicMemory().observe(
        execute(kb, theory, train, budget=10 ** 6, order="name")
    ).to_dict()
