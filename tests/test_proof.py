"""DLM v0.0039 tests: proof as data -- derive, verify, measure, and tamper."""
from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.proof import Proof, prove, verify, proof_size, proof_ir


def _kb():
    kb = KnowledgeBase({Atom("parent", (Const("a"), Const("b"))),
                        Atom("parent", (Const("b"), Const("c")))})
    kb.add_rule(Rule(Atom("ancestor", (Var("?x"), Var("?y"))),
                     (Atom("parent", (Var("?x"), Var("?y"))),), "base"))
    kb.add_rule(Rule(Atom("ancestor", (Var("?x"), Var("?y"))),
                     (Atom("parent", (Var("?x"), Var("?z"))),
                      Atom("ancestor", (Var("?z"), Var("?y")))), "step"))
    return kb


def test_prove_verify_and_size():
    kb = _kb()
    q = Atom("ancestor", (Const("a"), Const("c")))
    p = prove(kb, q)
    assert p is not None and not p.is_fact
    assert verify(p, kb)
    assert proof_size(p) > 1                     # a tree, not a single node
    assert p.atom == q


def test_leaf_fact_proof_and_abstain():
    kb = _kb()
    leaf = prove(kb, Atom("parent", (Const("a"), Const("b"))))
    assert leaf.is_fact and verify(leaf, kb)
    assert prove(kb, Atom("ancestor", (Const("c"), Const("a")))) is None


def test_tampered_proof_is_rejected():
    kb = _kb()
    p = prove(kb, Atom("ancestor", (Const("a"), Const("c"))))
    bad = Proof(Atom("ancestor", (Const("a"), Const("c"))), p.rule,
                tuple(Proof(Atom("parent", (Const("c"), Const("c"))), None, ())
                      for _ in p.premises))
    assert not verify(bad, kb)


def test_proof_ir_is_a_form():
    kb = _kb()
    p = prove(kb, Atom("ancestor", (Const("a"), Const("c"))))
    form = proof_ir(p)
    assert form[0] == "proof" and form[1] == ("ancestor", "a", "c")