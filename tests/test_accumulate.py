"""Tests for the accumulating learner: merge, retraction, compression, resume."""
import os
import tempfile

from dlm import Atom, Const, Var
from dlm.accumulate import Learner, rule_key
from dlm.abstract import theory_dl
from dlm.ground import Experience, Ground
from dlm.theory import load_theory, save_theory


def A(p, *xs):
    return Atom(p, tuple(Const(x) for x in xs))


def test_facts_merge_without_duplicates():
    L = Learner(Ground())
    L = L.observe(facts={A("r", "a")})
    L = L.observe(facts={A("r", "a"), A("r", "b")})
    assert L.facts == {A("r", "a"), A("r", "b")}
    assert L.memory[-1]["facts"] == 2


def test_retraction_drops_a_later_falsified_rule():
    L = Learner(Ground())
    L = L.observe(facts={A("r", "a")}, positives={A("q", "a")})
    assert len(L.experience.rules) == 1
    assert L.memory[-1]["false_final"] == 0

    # the counterexample arrives: r(b) now holds but q(b) must NOT
    L2 = L.observe(facts={A("r", "b")}, negatives={A("q", "b")})
    assert L2.memory[-1]["retracted"], "the falsified rule must be retracted"
    assert L2.experience.rules == ()
    assert L2.memory[-1]["false_final"] == 0
    # honest outcome: the positive is now uncovered, the learner abstains
    assert L2.memory[-1]["uncovered"] == 1


def test_without_retraction_the_unsound_rule_persists():
    L = Learner(Ground())
    L = L.observe(facts={A("r", "a")}, positives={A("q", "a")})
    bad = L.observe(facts={A("r", "b")}, negatives={A("q", "b")}, retract=False)
    assert bad.memory[-1]["false_final"] == 1
    assert bad.memory[-1]["false_atoms"] == ["(q b)"]


def test_compression_shrinks_dl_and_stays_sound():
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    from dlm import Rule
    body = (Atom("p", (x, z)), Atom("p", (z, y)))
    heads = [Atom(f"h{i}", (x, y)) for i in range(1, 5)]          # 4 uses
    exp = Experience(tuple(Rule(h, body, f"r{i}") for i, h in enumerate(heads)))
    facts = frozenset({A("p", "a", "b"), A("p", "b", "c")})
    pos = frozenset({Atom(h.pred, (Const("a"), Const("c"))) for h in heads})
    L = Learner(Ground(), exp, facts, pos, frozenset())
    before = theory_dl(exp.rules)
    L2 = L.observe(compress=True)
    assert L2.memory[-1]["dl"] < before
    assert L2.memory[-1]["compressed"], "a recurring body should be folded"
    assert L2.memory[-1]["false_final"] == 0
    # the folded theory still derives every positive
    assert pos <= L2.closure()


def test_checkpoint_and_resume():
    L = Learner(Ground())
    L = L.observe(facts={A("r", "a")}, positives={A("q", "a")})
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "learner.json")
        save_theory(path, L.to_theory())
        back = Learner.from_theory(load_theory(path))
    assert back.experience == L.experience
    assert back.positives == L.positives
    assert len(back.memory) == 1
    # resuming extends the same state, not a fresh one
    cont = back.observe(facts={A("r", "b")}, negatives={A("q", "b")})
    assert cont.memory[-1]["retracted"]
    assert len(cont.memory) == 2


def test_rule_key_is_renaming_invariant():
    from dlm import Rule
    a = Rule(Atom("q", (Var("?x"),)), (Atom("r", (Var("?x"),)),))
    b = Rule(Atom("q", (Var("?y"),)), (Atom("r", (Var("?y"),)),))
    c = Rule(Atom("q", (Var("?x"),)), (Atom("s", (Var("?x"),)),))
    assert rule_key(a) == rule_key(b)
    assert rule_key(a) != rule_key(c)