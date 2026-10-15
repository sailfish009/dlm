"""Network-free tests of the v0.0048 stratified-negation kernel + closed world.

The new capability is a certified NEGATIVE conclusion over a given universe, with
the property pure Horn cannot have -- non-monotonicity -- while staying sound:
non-stratified theories are rejected and unsafe negated literals assert nothing.
Pure-Horn behaviour must be completely unchanged.
"""
from dlm import Atom, Const, KnowledgeBase, NegAtom, Rule, Var, closure, strata
from dlm.closedworld import (CANDIDATE_LAYERS, absence_rule, absent_kinds,
                             candidate_facts, unsound_self_negation)


def _kb(facts, rules=()):
    return KnowledgeBase(set(facts), tuple(rules))


def test_derives_certified_negatives():
    facts = {Atom("is_module", (Const("net"),)),
             Atom("has_layer", (Const("net"), Const("conv2d")))}
    kb = _kb(facts, (absence_rule(),))
    kb.add_facts(candidate_facts(("conv2d", "batchnorm2d")))
    got = absent_kinds(closure(kb), "net")
    assert got == ["batchnorm2d"]                      # conv2d present -> not absent


def test_non_monotonic_retraction():
    kb = _kb({Atom("is_module", (Const("net"),))}, (absence_rule(),))
    kb.add_facts(candidate_facts(("conv2d", "batchnorm2d")))
    assert "batchnorm2d" in absent_kinds(closure(kb), "net")
    kb2 = kb.copy()
    kb2.add_fact(Atom("has_layer", (Const("net"), Const("batchnorm2d"))))
    assert "batchnorm2d" not in absent_kinds(closure(kb2), "net")   # retracted


def test_non_stratified_is_rejected():
    kb = _kb({Atom("q", (Const("x"),))}, (unsound_self_negation(),))
    try:
        closure(kb)
    except ValueError as exc:
        assert "stratif" in str(exc)
    else:
        raise AssertionError("negative cycle must be rejected")


def test_unsafe_negation_asserts_nothing():
    x, y = Var("x"), Var("y")
    bad = Rule(Atom("bad", (x,)), (Atom("candidate_layer", (y,)),
                                   NegAtom(Atom("has_layer", (x, y)))))
    kb = _kb({Atom("is_module", (Const("net"),))}, (bad,))
    kb.add_facts(candidate_facts(("conv2d",)))
    assert not any(a.pred == "bad" for a in closure(kb))   # never guessed


def test_strata_are_well_founded():
    kb = _kb({Atom("is_module", (Const("net"),))}, (absence_rule(),))
    st = strata(kb)
    assert st["absent"] >= 1                    # negated predicate lives below
    assert st["has_layer"] == 0


def test_pure_horn_unchanged_by_negation_support():
    # No NegAtom anywhere -> the semi-naive Horn path, identical to v0.0046.
    x, y, z = Var("x"), Var("y"), Var("z")
    trans = Rule(Atom("edge", (x, z)), (Atom("edge", (x, y)), Atom("edge", (y, z))))
    kb = _kb({Atom("edge", (Const("a"), Const("b"))),
              Atom("edge", (Const("b"), Const("c")))}, (trans,))
    closed = closure(kb)
    assert Atom("edge", (Const("a"), Const("c"))) in closed
    assert strata(kb) == {"edge": 0}


def test_deterministic():
    def once():
        kb = _kb({Atom("is_module", (Const("net"),))}, (absence_rule(),))
        kb.add_facts(candidate_facts(CANDIDATE_LAYERS))
        return sorted(map(repr, closure(kb)))
    assert once() == once()


def test_run_on_real_program_offline():
    import os
    from experiments.closedworld.run import run
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "experiments", "mnist", "cache")
    src = open(os.path.join(cache, "main.py"), "r", encoding="utf-8").read()
    r = run(src, cache_dir=cache, offline=True)
    assert all(r["verdict"].values())
    assert "batchnorm2d" in r["absent"]        # real absence, certified
    assert r["retraction_probe"]["retracted"] is True