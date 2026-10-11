"""Tests for the deduction engine (module 5)."""
from __future__ import annotations

from dlm.engine import closure, entails, holds, prove
from dlm.kb import KnowledgeBase
from dlm.kernel import Proof, verify
from dlm.logic import Atom, Const, Literal, Rule, Var


def A(pred, *names):
    return Atom(pred, tuple(Const(n) for n in names))


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("a", "b"), ("b", "c"), ("c", "d")]:
        kb.add_fact(A("parent", a, b))
    kb.add_rule(Rule(
        Atom("ancestor", (Var("x"), Var("y"))),
        (Atom("parent", (Var("x"), Var("y"))),),
        name="anc-base",
    ))
    kb.add_rule(Rule(
        Atom("ancestor", (Var("x"), Var("z"))),
        (Atom("parent", (Var("x"), Var("y"))), Atom("ancestor", (Var("y"), Var("z")))),
        name="anc-step",
    ))
    return kb


def test_closure_derives_transitive_ancestors():
    got = closure(build_kb())
    assert A("parent", "a", "b") in got
    assert A("ancestor", "a", "b") in got
    assert A("ancestor", "a", "c") in got
    assert A("ancestor", "a", "d") in got
    assert A("ancestor", "b", "d") in got
    # no spurious reverse edge
    assert A("ancestor", "d", "a") not in got


def test_entails_uses_closure():
    kb = build_kb()
    assert entails(kb, A("ancestor", "a", "d"))
    assert not entails(kb, A("ancestor", "d", "a"))


def test_prove_returns_a_verifiable_certificate():
    kb = build_kb()
    proof = prove(kb, A("ancestor", "a", "d"))
    assert isinstance(proof, Proof)
    assert proof.atom == A("ancestor", "a", "d")
    assert verify(proof, kb)
    assert "anc-step" in str(proof)


def test_prove_unknown_returns_none():
    assert prove(build_kb(), A("ancestor", "d", "a")) is None


def test_holds_positive_and_negative():
    kb = build_kb()
    kb.add_negation(A("parent", "d", "a"))
    assert holds(kb, Literal(A("ancestor", "a", "d")))
    assert not holds(kb, Literal(A("ancestor", "d", "a")))
    # a negative literal is only ever checked in the side table
    assert holds(kb, Literal(A("parent", "d", "a"), negated=True))
    assert not holds(kb, Literal(A("parent", "a", "b"), negated=True))


def test_closure_terminates_on_a_recursive_rule():
    kb = KnowledgeBase().add_fact(A("p", "a"))
    kb.add_rule(Rule(Atom("p", (Var("x"),)), (Atom("p", (Var("x"),)),)))
    assert closure(kb) == {A("p", "a")}


# -- prove completeness (regression: a loop check used to miss valid proofs) --
def test_prove_handles_repeated_derived_conjunct():
    kb = KnowledgeBase().add_fact(A("s", "a"))
    kb.add_rule(Rule(Atom("r", (Var("x"),)), (Atom("s", (Var("x"),)),)))
    kb.add_rule(
        Rule(
            Atom("h", ()),
            (Atom("r", (Const("a"),)), Atom("r", (Const("a"),))),
        )
    )
    assert entails(kb, Atom("h", ()))
    proof = prove(kb, Atom("h", ()))
    assert proof is not None and verify(proof, kb)


def test_prove_is_complete_on_cyclic_data():
    # A path-based loop check rejects ancestor(a,a) here; support-based proof
    # must find it (the least fixpoint contains it).
    kb = KnowledgeBase()
    kb.add_fact(A("parent", "a", "b"))
    kb.add_fact(A("parent", "b", "a"))
    kb.add_rule(Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("x"), Var("y"))),)))
    kb.add_rule(
        Rule(
            Atom("ancestor", (Var("x"), Var("z"))),
            (Atom("parent", (Var("x"), Var("y"))), Atom("ancestor", (Var("y"), Var("z")))),
        )
    )
    assert entails(kb, A("ancestor", "a", "a"))
    proof = prove(kb, A("ancestor", "a", "a"))
    assert proof is not None and verify(proof, kb)


def test_prove_agrees_with_entails_on_every_derived_atom():
    kb = build_kb()
    for atom in closure(kb):
        proof = prove(kb, atom)
        assert proof is not None and verify(proof, kb)


def test_prove_non_ground_abstains():
    assert prove(build_kb(), Atom("ancestor", (Const("a"), Var("y")))) is None


# -- semi-naive evaluation + argument index (performance, same fixpoint) ----
def _naive_closure(kb: KnowledgeBase):
    """Reference least fixpoint by repeatedly firing every rule (no indexes)."""
    facts = set(kb.facts())
    rules = tuple(kb.rules())
    changed = True
    while changed:
        changed = False
        for rule in rules:
            for binding in _naive_match(rule.body, facts, {}):
                head = Atom(rule.head.pred, tuple(
                    binding.get(a, a) if isinstance(a, Var) else a for a in rule.head.args
                ))
                if all(isinstance(a, Const) for a in head.args) and head not in facts:
                    facts.add(head)
                    changed = True
    return facts


def _naive_match(body, facts, binding):
    if not body:
        yield binding
        return
    first, rest = body[0], body[1:]
    for fact in tuple(facts):
        if fact.pred != first.pred or fact.arity != first.arity:
            continue
        b = dict(binding)
        ok = True
        for pattern, value in zip(first.args, fact.args):
            if isinstance(pattern, Var):
                if pattern in b and b[pattern] != value:
                    ok = False
                    break
                b[pattern] = value
            elif pattern != value:
                ok = False
                break
        if ok:
            yield from _naive_match(rest, facts, b)


def test_closure_matches_naive_reference_on_a_dense_graph():
    from random import Random

    rng = Random(20240701)
    kb = KnowledgeBase()
    nodes = [f"n{i}" for i in range(14)]
    for a in nodes:
        for b in nodes:
            if a != b and rng.random() < 0.18:
                kb.add_fact(A("e", a, b))
    kb.add_rule(Rule(
        Atom("e", (Var("x"), Var("z"))),
        (Atom("e", (Var("x"), Var("y"))), Atom("e", (Var("y"), Var("z")))),
        name="trans",
    ))
    assert closure(kb) == _naive_closure(kb)


def test_arg_index_join_keeps_bound_constant_results():
    # second body atom is partly bound; the argument index must not drop it.
    kb = KnowledgeBase()
    kb.add_fact(A("p", "a", "b"))
    kb.add_fact(A("p", "c", "b"))
    kb.add_fact(A("q", "b", "z"))
    kb.add_rule(Rule(
        Atom("r", (Var("x"),)),
        (Atom("p", (Var("x"), Const("b"))), Atom("q", (Const("b"), Const("z")))),
        name="bound",
    ))
    got = closure(kb)
    assert Atom("r", (Const("a"),)) in got
    assert Atom("r", (Const("c"),)) in got