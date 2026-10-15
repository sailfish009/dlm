"""Network-free tests of the v0.0048 typed/moded signatures (D6).

A signature gates ADMISSION, not truth.  These tests pin both halves of that
claim: every ill-shaped clause is rejected with a specific reason, and for a
well-typed theory the signature is a no-op on the closure.
"""
from dlm import (Arg, Atom, Const, KnowledgeBase, NegAtom, Rule, Signature,
                 Var, closure, fact_type_errors, type_errors)


def _sig():
    return Signature(
        args={
            "calls": (Arg("fn", "any"), Arg("callable", "any")),
            "method_of": (Arg("module", "any"), Arg("fn", "any")),
            "inherits": (Arg("module", "any"), Arg("symbol", "any")),
            "meaning": (Arg("symbol", "in"), Arg("concept", "any")),
            "is_module": (Arg("module", "in"),),
            "has_layer": (Arg("module", "in"), Arg("layer", "any")),
            "creates": (Arg("fn", "any"), Arg("callable", "any")),
            "before": (Arg("step", "in"), Arg("step", "in")),
        },
        types={"concept": frozenset({"layer", "module_base"}),
               "layer": frozenset({"conv2d", "dropout"})},
        parents={"fn": ("callable",), "module": ("fn",), "symbol": ("callable",),
                 "layer": ("symbol",)},
    )


def test_type_clash_between_disjoint_branches():
    c, x = Var("c"), Var("x")
    # ?c is a module (is_module) and a symbol (meaning slot0) -- disjoint branches.
    rule = Rule(Atom("has_layer", (c, x)),
                (Atom("is_module", (c,)), Atom("meaning", (c, Const("layer")))))
    errs = type_errors(rule, _sig())
    assert any("type clash" in e and "module" in e and "symbol" in e for e in errs)


def test_subtype_positions_do_not_clash():
    c, l = Var("c"), Var("l")
    # ?l is a layer (has_layer slot1) and a symbol (meaning slot0): layer <: symbol.
    rule = Rule(Atom("has_layer", (c, l)),
                (Atom("creates", (c, l)), Atom("meaning", (l, Const("layer")))))
    assert type_errors(rule, _sig()) == ()
    assert _sig().compatible("layer", "symbol") is True
    assert _sig().compatible("module", "symbol") is False


def test_unknown_predicate_and_arity():
    x = Var("x")
    assert type_errors(Rule(Atom("flies", (x,)), (Atom("is_module", (x,)),)), _sig())
    assert any("arity" in e for e in
               type_errors(Rule(Atom("inherits", (x,)), (Atom("is_module", (x,)),)), _sig()))


def test_constant_outside_type_is_rejected():
    c = Var("c")
    rule = Rule(Atom("has_layer", (c, Const("handwritten_digit"))),
                (Atom("is_module", (c,)),))
    assert any("not of type layer" in e for e in type_errors(rule, _sig()))
    # and on ground facts
    assert fact_type_errors(Atom("has_layer", (Const("net"), Const("handwritten_digit"))), _sig())


def test_open_type_accepts_any_constant():
    # ``fn`` has no constant set -> membership is not checked.
    assert fact_type_errors(Atom("calls", (Const("main"), Const("whatever"))), _sig()) == ()


def test_range_restriction_head_variable():
    x, y, z = Var("x"), Var("y"), Var("z")
    rule = Rule(Atom("calls", (x, y)), (Atom("calls", (x, z)),))
    assert any("head variable ?y" in e for e in type_errors(rule, _sig()))


def test_range_restriction_negated_variable():
    c, m, l = Var("c"), Var("m"), Var("l")
    rule = Rule(Atom("is_module", (c,)),
                (Atom("method_of", (c, m)), NegAtom(Atom("has_layer", (m, l)))))
    assert any("negated variable ?l" in e for e in type_errors(rule, _sig()))


def test_mode_anability_unproduced_input():
    m, c, e, d = Var("m"), Var("c"), Var("e"), Var("d")
    # ``before`` takes two inputs; neither is produced by any literal.
    rule = Rule(Atom("calls", (m, c)), (Atom("calls", (m, c)), Atom("before", (e, d))))
    assert any("mode: input ?e" in e for e in type_errors(rule, _sig()))


def test_typed_closure_is_truth_preserving():
    sig = _sig()
    facts = {Atom("has_layer", (Const("net"), Const("conv2d")))}
    rules = (Rule(Atom("is_module", (Var("c"),)), (Atom("inherits", (Var("c"), Const("nn"))),)),)
    kb = KnowledgeBase(set(facts), tuple(rules))
    assert closure(kb, sig) == closure(kb)


def test_typed_closure_rejects_ill_typed_before_deriving():
    sig = _sig()
    c = Var("c")
    bad = Rule(Atom("has_layer", (c, Const("handwritten_digit"))),
               (Atom("is_module", (c,)),), name="bad")
    kb = KnowledgeBase({Atom("inherits", (Const("net"), Const("nn"))), Atom("meaning", (Const("nn"), Const("module_base")))})
    kb.add_rule(bad)
    try:
        closure(kb, sig)
    except TypeError as exc:
        assert "ill-typed theory" in str(exc) and "bad" in str(exc)
    else:
        raise AssertionError("ill-typed theory must be rejected")
    # without the signature the same KB still closes (typing is opt-in)
    assert closure(kb)


def test_absence_rule_is_type_safe():
    from experiments.mnist.signature import SIGNATURE_ARGS, TYPE_PARENTS, absence_rule_typed
    sig = Signature(args=dict(SIGNATURE_ARGS),
                    types={"concept": frozenset({"layer"}), "layer": frozenset({"conv2d"})},
                    parents=dict(TYPE_PARENTS))
    assert type_errors(absence_rule_typed(), sig) == ()


def test_run_on_real_program_offline():
    import os
    from experiments.typed.run import run
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "experiments", "mnist", "cache")
    src = open(os.path.join(cache, "main.py"), "r", encoding="utf-8").read()
    r = run(src, cache_dir=cache, offline=True)
    assert all(r["verdict"].values())
    assert r["derived"]["recognizes"] is True
    assert "batchnorm2d" in r["derived"]["absences"]
    assert r["pruning"]["type_rejected_but_head_bound"] > 0