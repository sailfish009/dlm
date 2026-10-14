"""DLM v0.0038 tests: kernel, Lisp medium, Ground/Experience learning."""
import itertools

from dlm import Atom, Const, Rule, Var, KnowledgeBase, closure, entails, description_length
from dlm.lisp import (parse, dump, match_form, subst_form, form_to_atom,
                      form_to_rule, atom_to_form, eval_sexp, Env)
from dlm.ground import Ground, Experience, lgg_atoms, variate, learn


def A(pred, *args):
    return Atom(pred, tuple(Const(a) if isinstance(a, str) else a for a in args))


def test_closure_transitive():
    kb = KnowledgeBase({A("parent", "a", "b"), A("parent", "b", "c")})
    kb.add_rule(Rule(A("ancestor", Var("?x"), Var("?y")), (A("parent", Var("?x"), Var("?y")),)))
    kb.add_rule(Rule(A("ancestor", Var("?x"), Var("?y")),
                     (A("parent", Var("?x"), Var("?z")), A("ancestor", Var("?z"), Var("?y")))))
    assert A("ancestor", "a", "c") in closure(kb)
    assert A("ancestor", "c", "a") not in closure(kb)


def test_entails_and_dl():
    kb = KnowledgeBase({A("parent", "a", "b")})
    r = Rule(A("ancestor", Var("?x"), Var("?y")), (A("parent", Var("?x"), Var("?y")),))
    kb.add_rule(r)
    assert entails(kb, A("ancestor", "a", "b"))
    assert description_length([r]) == 2


def test_lisp_roundtrip():
    f = parse("(rule (ancestor ?x ?y) (parent ?x ?y))")[0]
    a = form_to_atom(f[1])
    assert atom_to_form(a) == f[1]
    r = form_to_rule(f)
    assert r.head.pred == "ancestor" and len(r.body) == 1


def test_match_is_pronominal_and_open():
    pat = parse("(parent ?x ?y)")[0]
    b1 = match_form(pat, parse("(parent n0 n1)")[0])
    b2 = match_form(pat, parse("(parent n7 n8)")[0])   # never-seen referents
    assert b1 == {"?x": "n0", "?y": "n1"}
    assert b2 == {"?x": "n7", "?y": "n8"}
    assert match_form(parse("(parent ?x ?x)")[0], parse("(parent a b)")[0]) is None
    assert subst_form(parse("(ancestor ?x ?y)")[0], b1) == ("ancestor", "n0", "n1")


def test_eval_only_query_reads_truth():
    env = Env()
    eval_sexp("(fact (parent a b))", env)
    assert eval_sexp("(query (parent a b))", env) == (True,)
    assert eval_sexp("(query (parent b a))", env) == (False,)


def test_lgg_and_variate():
    g = lgg_atoms([A("ancestor", "a", "c"), A("ancestor", "b", "c")])
    assert g.pred == "ancestor" and isinstance(g.args[0], Var) and g.args[1] == Const("c")
    v = variate(A("ancestor", "a", "b"))
    assert all(isinstance(t, Var) for t in v.args)


def _family(n):
    facts = {A("parent", f"n{i}", f"n{i+1}") for i in range(n)}
    pos = {A("ancestor", f"n{i}", f"n{j}") for i in range(n) for j in range(i + 2, n + 1)}
    neg = {A("ancestor", f"n{i}", f"n{j}") for i in range(n) for j in range(0, i + 1)}
    return facts, pos, neg


def test_ground_is_immutable_and_base_only():
    ground = Ground.from_forms(parse("(rule (ancestor ?x ?y) (parent ?x ?y))"))
    facts, pos, _ = _family(6)
    base = ground.base(facts)
    closed = closure(base)
    # base case alone cannot derive length-2 ancestors
    assert A("ancestor", "n0", "n1") in closed
    assert A("ancestor", "n0", "2") not in closed
    assert ground.rules[0].name != "exp_0"          # Ground untouched


def test_learn_covers_and_is_sound():
    ground = Ground.from_forms(parse("(rule (ancestor ?x ?y) (parent ?x ?y))"))
    facts, pos, neg = _family(6)
    res = learn(ground, facts, pos, neg)
    assert res.covered == frozenset(pos)             # all positives derived
    assert res.false_assert == frozenset()           # no negative derived (sound)
    assert res.clauses >= 1                          # experience grew
    assert len(ground.rules) == 1                    # ground unchanged


def test_learn_uses_kernel_gate_on_overgeneral():
    # every literal covering the positive also covers the negative: veto -> no rule
    ground = Ground(())
    facts = {A("q", "a"), A("q", "b")}
    pos = {A("goal", "a")}
    neg = {A("goal", "b")}
    res = learn(ground, facts, pos, neg, max_body=2, extra_vars=1)
    assert res.clauses == 0                     # nothing sound was found
    assert res.false_assert == frozenset()      # and nothing unsound was admitted
    assert res.covered == frozenset()


def test_conservative_extension_keeps_ground_closure():
    ground = Ground.from_forms(parse("(rule (ancestor ?x ?y) (parent ?x ?y))"))
    facts, pos, neg = _family(7)
    res = learn(ground, facts, pos, neg)
    # every atom Ground derived before is still derived with Experience added
    base = ground.base(facts)
    with_exp = res.experience.to_kb(base)
    assert closure(base) <= closure(with_exp)