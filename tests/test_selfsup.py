"""Tests for the verifiable-reward self-supervised loop (dlm/selfsup.py, v0.0024)."""
from __future__ import annotations

from random import Random

from dlm import Atom, Clause, Const, KnowledgeBase, Rule, Theory, Var, closure
from dlm.selfsup import (
    LoopResult,
    StopPolicy,
    Task,
    decide_stop,
    evaluate,
    program_sexp,
    promote,
    propose,
    random_program,
    reweight,
    run_loop,
    scramble_task,
    sloppy_program,
)


# -- a tiny controlled task: chain edges + a distance predicate ------------
def _chain(n: int = 40):
    kb = KnowledgeBase()
    for i in range(n - 1):
        kb.add_fact(Atom("e", (Const(f"n{i}"), Const(f"n{i + 1}"))))
    return kb


def _atom(pred: str, a: int, b: int) -> Atom:
    return Atom(pred, (Const(f"n{a}"), Const(f"n{b}")))


def _pairs(nodes, d):
    ns = set(nodes)
    return {(a, a + d) for a in nodes if a + d in ns}


def _task(kb, r, d, train, test) -> Task:
    pred = f"t{r}"
    pos = sorted((_atom(pred, a, b) for a, b in _pairs(train, d)), key=str)
    hit = _pairs(train, d)
    allp = [(a, b) for a in train for b in train if a != b]
    neg = sorted((_atom(pred, a, b) for a, b in allp if (a, b) not in hit), key=str)
    hp = sorted((_atom(pred, a, b) for a, b in _pairs(test, d)), key=str)
    hn = sorted((_atom(pred, a, b) for a, b in [(a, b) for a in test for b in test if a != b] if abs(a - b) != d), key=str)
    return Task(pred, kb, tuple(pos), tuple(neg), tuple(hp), tuple(hn))


def _tasks(n: int = 32):
    kb = _chain(n)
    half = n // 2
    train, test = list(range(half)), list(range(half, n))
    rounds = 0
    while 2 ** (rounds + 1) <= half - 1:
        rounds += 1
    return kb, [_task(kb, r, 2 ** r, train, test) for r in range(1, rounds + 1)]


# -- the reward is exact and the gate is hard ------------------------------
def test_evaluate_is_a_hard_kernel_gate():
    kb = _chain(6)
    x, y = Var("x"), Var("y")
    sound = Clause(Rule(Atom("p", (x, y)), (Atom("e", (x, y)),), "p_direct"), 0.0)
    good = evaluate(kb, [sound], [_atom("p", 0, 1)], [_atom("p", 1, 0)])
    assert good.proved == 1 and good.false_assert == 0 and good.reward > 0
    # a program that also derives a negative collapses to the hard -1
    bad = evaluate(kb, [sound], [_atom("p", 0, 1)], [_atom("p", 0, 1)])
    assert bad.false_assert == 1 and bad.reward == -1.0 and not bad.sound


def test_evaluate_does_not_mutate_the_base_kb():
    kb = _chain(6)
    x, y, z = Var("x"), Var("y"), Var("z")
    rule = Rule(Atom("p", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y))), "p2")
    before = len(kb.rules())
    evaluate(kb, [Clause(rule, 0.0)], [_atom("p", 0, 2)], [])
    assert len(kb.rules()) == before
    assert not kb.has_rule(rule)


# -- promotion adds structure, never truth-to-weights ----------------------
def test_promote_adds_structure_only_and_dedups():
    t0 = Theory("t", ())
    x, y, z = Var("x"), Var("y"), Var("z")
    a = Clause(Rule(Atom("p", (x, y)), (Atom("e", (x, z)), Atom("e", (z, y))), "p2"), 0.5)
    t1 = promote(t0, [a])
    t2 = promote(t1, [a])  # same name -> not duplicated
    assert t1.params == 1 and t2.params == 1
    kb = t1.to_kb(_chain(6))
    assert kb.has_rule(a.rule)  # structure installed
    assert t1.weights()["p2"] == 0.5  # weight is order, kept out of the kernel


# -- the loop composes programs a single pass cannot ------------------------
def test_loop_composes_beyond_single_shot():
    kb, tasks = _tasks(32)
    result = run_loop(tasks, mode="learn", policy=StopPolicy(max_rounds=len(tasks)), seed=0, budget=5000)
    assert isinstance(result, LoopResult)
    assert result.mean_held_coverage == 1.0
    assert result.false_assert == 0
    assert result.theory.params == len(tasks)
    # the later clauses reuse the earlier predicate -- that is the composition
    text = program_sexp(result.theory)
    assert "(t2 ?G0 ?G1) (t1 " in text
    assert "(t3 ?G0 ?G1) (t2 " in text


def test_single_shot_cannot_find_the_composition():
    # with no promoted theory, body length 2 on predicate e cannot express
    # distance 8: the proposer finds nothing for the third task.
    _, tasks = _tasks(32)
    program = propose(tasks[2].kb, tasks[2].positives, tasks[2].negatives, max_body=2, budget=20000)
    assert program == ()


def test_loop_is_deterministic():
    _, tasks = _tasks(32)
    policy = StopPolicy(max_rounds=len(tasks))
    a = run_loop(tasks, mode="learn", policy=policy, seed=0, budget=5000).to_dict()
    b = run_loop(tasks, mode="learn", policy=policy, seed=0, budget=5000).to_dict()
    assert a == b


# -- the controls fail, and removing the gate fabricates -------------------
def test_controls_stay_at_the_floor_and_gate_off_fabricates():
    _, tasks = _tasks(32)
    policy = StopPolicy(max_rounds=len(tasks), stop_on_no_proposal=False)
    for mode in ("no_promote", "scramble", "random"):
        r = run_loop(tasks, mode=mode, policy=policy, seed=0, budget=5000)
        assert r.mean_held_coverage <= 0.05, mode
        assert r.false_assert == 0, mode
    hack = run_loop(tasks, mode="reward_hacking", policy=policy, seed=0, budget=5000)
    assert hack.false_assert > 0  # no hard gate -> held-out negatives asserted


def test_scramble_task_preserves_sizes():
    _, tasks = _tasks(32)
    scrambled = scramble_task(tasks[0], Random(0))
    assert len(scrambled.positives) == len(tasks[0].positives)
    assert len(scrambled.negatives) == len(tasks[0].negatives)
    assert set(scrambled.positives) | set(scrambled.negatives) == set(tasks[0].positives) | set(tasks[0].negatives)


# -- proposers only propose; they never assert ------------------------------
def test_proposers_are_only_proposals():
    kb, tasks = _tasks(32)
    assert propose(kb, (), ()) == ()
    rng_prog = random_program(kb, tasks[0].positives, rng=Random(0))
    sloppy = sloppy_program(kb, tasks[1].positives)
    for program in (rng_prog, sloppy):
        assert all(isinstance(c, Clause) for c in program)
    # neither proposer has changed the base KB
    assert kb.rules() == ()
    # the base facts alone prove none of the target predicates
    closed = closure(kb)
    assert not any(a.pred == "t1" for a in closed)


# -- the stopping rule -----------------------------------------------------
def test_stop_policy_flags():
    kb, tasks = _tasks(32)
    policy = StopPolicy(max_rounds=2, stop_on_no_proposal=True)
    result = run_loop(tasks, mode="learn", policy=policy, seed=0, budget=5000)
    assert result.rounds == 2
    assert result.stats[-1].stopped_reason == "round_budget"
    policy2 = StopPolicy(max_rounds=len(tasks), stop_on_no_proposal=True)
    empty = run_loop(tasks, mode="no_promote", policy=policy2, seed=0, budget=5000)
    # no_promote still proposes (round-1 shape) so it runs on; the empty-proposal
    # stop is exercised directly here:
    assert decide_stop(empty.stats[:1], StopPolicy(max_rounds=9, stop_on_no_proposal=True)) is None


# -- reweight is the fused learner over the grown program -------------------
def test_reweight_orders_the_grown_clauses():
    _, tasks = _tasks(32)
    result = run_loop(tasks, mode="learn", policy=StopPolicy(max_rounds=len(tasks)), seed=0, budget=5000)
    grown, updates = reweight(result.theory, [])
    assert grown.params == result.theory.params
    assert updates == 0
