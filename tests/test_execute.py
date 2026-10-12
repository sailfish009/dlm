"""Tests for the bounded executor + experience-fed proof credit (dlm/execute.py, v0.0027)."""
from __future__ import annotations

from random import Random

from dlm import Atom, Clause, Const, KnowledgeBase, Rule, Theory, Var
from dlm.execute import (
    ControlResult,
    Credit,
    Execution,
    apply_credit,
    check_sound,
    credits,
    execute,
    experience_pairs,
    pairs_from_credit,
    run_control_loop,
)
from dlm.selfsup import Task


# -- a tiny chain + a correct clause and an over-specific decoy ------------
def _chain(n: int = 12) -> KnowledgeBase:
    kb = KnowledgeBase()
    for i in range(n - 1):
        kb.add_fact(Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _t(a: int, b: int, pred: str = "t1") -> Atom:
    return Atom(pred, (Const(f"n{a}"), Const(f"n{b}")))


def _correct() -> Rule:
    x, y, z = Var("x"), Var("y"), Var("z")
    return Rule(Atom("t1", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y))), "zcorrect")


def _decoy() -> Rule:
    x, y, z = Var("x"), Var("y"), Var("z")
    # sound (implies the two real atoms) but unsatisfiable on a path: e(z,z) never holds
    return Rule(Atom("t1", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y)), Atom("e", (z, z))), "adecoy")


def _theory(frozen: bool) -> Theory:
    w = 0.0 if frozen else 2.0
    return Theory("t", (Clause(_decoy(), 1.0), Clause(_correct(), w)))


# -- the executor: bounded, order-sensitive, sound -------------------------
def test_execute_proves_a_composed_goal_with_a_readable_trace():
    kb = _chain(12)
    ex = execute(kb, _theory(frozen=True), [_t(0, 2), _t(3, 5)], budget=64)
    assert isinstance(ex, Execution)
    assert ex.proved == (_t(0, 2), _t(3, 5))
    assert check_sound(kb, _theory(frozen=True), ex)
    # the trace names the clause that closed each proof
    assert any(s.ok and s.clause == "zcorrect" for s in ex.steps)
    assert all(isinstance(line, str) for line in ex.explain())


def test_execute_does_not_mutate_the_base_kb():
    kb = _chain(12)
    before = (len(kb.facts()), len(kb.rules()))
    execute(kb, _theory(frozen=True), [_t(0, 2)], budget=64)
    assert (len(kb.facts()), len(kb.rules())) == before


def test_order_changes_what_is_proved_under_a_tight_budget():
    kb = _chain(12)
    goals = [_t(0, 2), _t(3, 5)]
    frozen = execute(kb, _theory(frozen=True), goals, budget=2)   # decoy first
    learned = execute(kb, _theory(frozen=False), goals, budget=2)  # correct first
    assert len(frozen.proved) == 1          # budgets the decoy, proves one maybe
    assert len(learned.proved) == 2         # correct clause first, both
    assert frozen.exhausted and not learned.exhausted


def test_budget_exhaustion_is_reported():
    kb = _chain(12)
    ex = execute(kb, _theory(frozen=True), [_t(0, 2)], budget=1)
    assert ex.exhausted and ex.spent == 1 and ex.proved == ()


def test_random_order_is_reproducible_with_a_seeded_rng():
    kb = _chain(12)
    goals = [_t(0, 2), _t(3, 5), _t(5, 7)]
    a = execute(kb, _theory(frozen=True), goals, budget=8, order="random", rng=Random(0))
    b = execute(kb, _theory(frozen=True), goals, budget=8, order="random", rng=Random(0))
    assert a.to_dict() == b.to_dict()


# -- credit assignment -----------------------------------------------------
def test_credits_separate_hits_from_waste():
    kb = _chain(12)
    ex = execute(kb, _theory(frozen=True), [_t(0, 2), _t(3, 5)], budget=64)
    credit = credits(ex)
    assert credit.hits.get("zcorrect", 0) >= 1
    assert credit.waste.get("adecoy", 0) >= 1
    assert credit.net()["zcorrect"] > credit.net()["adecoy"]


def test_apply_credit_ranks_the_helpful_clause_above_the_decoy():
    theory = _theory(frozen=True)
    credit = Credit(hits={"zcorrect": 3}, waste={"adecoy": 2})
    updated = apply_credit(theory, credit, lr=1.0)
    w = updated.weights()
    assert w["zcorrect"] == 3.0 and w["adecoy"] == -1.0
    assert w["zcorrect"] > w["adecoy"]


def test_experience_pairs_mark_hits_positive_and_waste_negative():
    kb = _chain(12)
    ex = execute(kb, _theory(frozen=True), [_t(0, 2), _t(3, 5)], budget=64)
    pairs = experience_pairs(_theory(frozen=True), ex)
    assert pairs  # at least one (helpful, wasteful) pair
    assert all(isinstance(p, Rule) and isinstance(n, Rule) for p, n in pairs)
    names = {(p.name, n.name) for p, n in pairs}
    assert ("zcorrect", "adecoy") in names
    # direct-from-credit variant agrees
    assert pairs_from_credit(_theory(frozen=True), credits(ex)) == pairs


# -- the experience-fed loop ----------------------------------------------
def _benchmark(nodes: int = 64):
    kb = _chain(nodes)
    x, y, z = Var("x"), Var("y"), Var("z")
    train, test = list(range(nodes // 2)), list(range(nodes // 2, nodes))
    tasks = []
    rounds = 0
    while 2 ** (rounds + 1) <= nodes // 2 - 1:
        rounds += 1
    for r in range(1, rounds + 1):
        pred, d = f"t{r}", 2 ** r
        keep = {(a, a + d) for a in train if a + d < nodes}
        pos = sorted(
            (Atom(pred, (Const(f"n{a}"), Const(f"n{a + d}"))) for a in train if a + d < nodes),
            key=str,
        )
        held = sorted(
            (Atom(pred, (Const(f"n{a}"), Const(f"n{a + d}"))) for a in test if a + d < nodes),
            key=str,
        )
        allp = [(a, b) for a in train for b in train if a != b]
        neg = sorted(
            (Atom(pred, (Const(f"n{a}"), Const(f"n{b}"))) for a, b in allp if (a, b) not in keep),
            key=str,
        )
        tasks.append(Task(pred, kb, tuple(pos), tuple(neg), tuple(held), ()))
    decoys = tuple(
        Clause(
            Rule(
                Atom(f"t{r}", (x, y)),
                (
                    Atom("e" if r == 1 else f"t{r - 1}", (x, z)),
                    Atom("e" if r == 1 else f"t{r - 1}", (z, y)),
                    Atom("e", (z, z)),
                ),
                f"adecoy_r{r}",
            ),
            1.0,
        )
        for r in range(1, rounds + 1)
    )
    return kb, tasks, decoys


def test_control_loop_feedback_beats_frozen_and_stays_sound():
    _, tasks, decoys = _benchmark(40)
    frozen = run_control_loop(tasks, feedback=False, executor_budget=200, seed=0, decoys=decoys)
    learned = run_control_loop(tasks, feedback=True, executor_budget=200, seed=0, decoys=decoys)
    assert isinstance(learned, ControlResult)
    assert learned.mean_coverage > frozen.mean_coverage
    assert learned.mean_coverage == 1.0
    assert learned.false_assert == 0 and learned.sound
    assert learned.total_updates > 0


def test_control_loop_scramble_does_not_help():
    _, tasks, decoys = _benchmark(40)
    frozen = run_control_loop(tasks, feedback=False, executor_budget=200, seed=0, decoys=decoys)
    scrambled = run_control_loop(
        tasks, feedback=True, scramble=True, executor_budget=200, seed=0, decoys=decoys
    )
    assert scrambled.mean_coverage <= frozen.mean_coverage + 1e-9
    assert scrambled.false_assert == 0 and scrambled.sound


def test_control_loop_is_deterministic():
    _, tasks, decoys = _benchmark(40)
    a = run_control_loop(tasks, feedback=True, executor_budget=200, seed=0, decoys=decoys).to_dict()
    b = run_control_loop(tasks, feedback=True, executor_budget=200, seed=0, decoys=decoys).to_dict()
    assert a == b


def test_control_loop_feedback_does_not_hurt_without_decoys():
    _, tasks, _ = _benchmark(40)
    frozen = run_control_loop(tasks, feedback=False, executor_budget=200, seed=0, decoys=())
    learned = run_control_loop(tasks, feedback=True, executor_budget=200, seed=0, decoys=())
    assert learned.mean_coverage >= frozen.mean_coverage


def test_decoys_never_reach_the_induction_kb():
    # Decoys are sound but the loop must never let them seed the proposer: the
    # grown theory is identical with and without them.
    _, tasks, decoys = _benchmark(40)
    with_decoys = run_control_loop(tasks, feedback=True, executor_budget=200, seed=0, decoys=decoys)
    without = run_control_loop(tasks, feedback=True, executor_budget=200, seed=0, decoys=())
    assert all(not name.startswith("adecoy") for name in with_decoys.theory.names())
    assert with_decoys.theory.names() == without.theory.names()
