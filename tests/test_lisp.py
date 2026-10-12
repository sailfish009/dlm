"""Tests for dlm/lisp.py -- the v0.0029 Lisp seam (unified eval, macros,
proof-as-data, source round-trip, tree reification)."""
from __future__ import annotations

import ast
import pathlib

import pytest

from dlm import Atom, Const, Proof, SexpError, Sym, dump, form_to_atom
from dlm import clause_to_form, form_to_rule, theory_sexp
import dlm.lisp as lisp
from dlm.lisp import (
    DefMacro,
    Env,
    EvalError,
    eval_form,
    eval_sexp,
    expand_source,
    form_to_proof,
    form_variables,
    is_quote,
    is_var,
    is_wildcard,
    macroexpand,
    match_form,
    proof_to_form,
    quasiquote_form,
    query_tree,
    quote_form,
    source_roundtrip,
    source_theory,
    subst_form,
    theory_source,
    tree_atoms,
    tree_kb,
    verify_form,
)

REPO = pathlib.Path(__file__).resolve().parents[1]


# -- 1. unified evaluation -------------------------------------------------
def test_eval_runs_a_whole_program():
    env = Env()
    out = eval_sexp(
        "(fact (e a b)) (fact (e b c))"
        " (rule step (t ?x ?y) (e ?x ?y))"
        " (rule rec (t ?x ?y) (e ?x ?z) (t ?z ?y))"
        " (query (t a c))",
        env,
    )
    proof = out[-1]
    assert isinstance(proof, Proof)
    assert proof.atom == Atom("t", (Const("a"), Const("c")))
    assert env.kb.has_fact(Atom("e", (Const("a"), Const("b"))))


def test_eval_query_missing_goal_is_none():
    assert eval_sexp("(query (p a))", Env())[0] is None


def test_unknown_head_abstains():
    with pytest.raises(EvalError):
        eval_sexp("(frobnicate 1 2)", Env())


def test_eval_of_a_non_tuple_self_evaluates():
    env = Env()
    assert eval_form(Sym("alan"), env) == Sym("alan")
    assert eval_form("literal", env) == "literal"


def test_eval_do_returns_last_and_collects_theory():
    env = Env()
    (clause,) = eval_sexp("(clause c 1.0 (t ?x ?y) (e ?x ?y))", env)
    assert clause.name == "c"
    assert env.theory is not None and env.theory.params == 1
    assert eval_sexp("(do (fact (p a)) (fact (q a)))", env)[0] == Atom(
        "q", (Const("a"),)
    )


def test_eval_never_asserts_beyond_the_kernel():
    # a bare rule does not prove anything; only a query consults the kernel
    env = Env()
    eval_sexp("(rule r (t ?x) (e ?x))", env)
    assert eval_sexp("(query (t a))", env)[0] is None


# -- 2. the code algebra ---------------------------------------------------
def test_match_form_consistent_and_clash():
    b = match_form((Sym("?op"), Sym("?a"), Sym("?a")), (Sym("+"), Sym("x"), Sym("x")))
    assert b == {"?op": Sym("+"), "?a": Sym("x")}
    assert match_form((Sym("?a"), Sym("?a")), (Sym("x"), Sym("y"))) is None


def test_match_form_wildcard_and_list_length():
    b = match_form((Sym("f"), Sym("_"), Sym("?z")), (Sym("f"), Sym("any"), Sym("q")))
    assert b is not None and set(b) == {"?z"}
    assert match_form((Sym("f"), Sym("?x")), (Sym("f"),)) is None


def test_subst_form_and_form_variables():
    tpl = (Sym("f"), Sym("?x"), (Sym("g"), Sym("?y")))
    assert form_variables(tpl) == ("?x", "?y")
    assert subst_form(tpl, {"?x": Sym("1"), "?y": Sym("2")}) == (
        Sym("f"),
        Sym("1"),
        (Sym("g"), Sym("2")),
    )


def test_var_wildcard_predicates():
    assert is_var(Sym("?x")) and not is_var(Sym("x")) and not is_var("?x")
    assert is_wildcard(Sym("_")) and not is_wildcard(Sym("?x"))


# -- 3. quote / quasiquote / macros ---------------------------------------
def test_quote_is_data_not_evaluated():
    q = quote_form((Sym("t"), Sym("?x")))
    assert is_quote(q)
    assert eval_sexp(dump(q), Env())[0] == (Sym("t"), Sym("?x"))


def test_quasiquote_substitutes_bare_and_unquote():
    tpl = (Sym("clause"), Sym("?n"), (Sym("unquote"), Sym("?h")))
    got = quasiquote_form(tpl, {"?n": Sym("c"), "?h": (Sym("p"), Sym("a"))})
    assert got == (Sym("clause"), Sym("c"), (Sym("p"), Sym("a")))


def test_macro_generates_a_clause():
    env = Env()
    eval_sexp(
        "(defmacro mk (?name ?edge) (clause ?name 1.0 (t ?x ?y) (?edge ?x ?y)))", env
    )
    (clause,) = eval_sexp("(mk c_step e)", env)
    assert clause.rule == form_to_rule(
        (Sym("rule"), Sym("c_step"), (Sym("t"), Sym("?x"), Sym("?y")), (Sym("e"), Sym("?x"), Sym("?y")))
    )
    assert clause_to_form(clause)[0] == Sym("clause")
    assert expand_source("(mk c_step e)", env.macros) == "(clause c_step 1.0 (t ?x ?y) (e ?x ?y))"


def test_macro_pattern_mismatch_abstains():
    env = Env()
    eval_sexp("(defmacro mk (?name) (clause ?name 1.0 (t ?x) (e ?x)))", env)
    with pytest.raises(EvalError):
        eval_sexp("(mk a b)", env)


# -- 4. proof as data ------------------------------------------------------
def test_proof_roundtrip_and_reverify():
    env = Env()
    out = eval_sexp(
        "(fact (e a b)) (rule step (t ?x ?y) (e ?x ?y)) (query (t a b))", env
    )
    proof = out[-1]
    form = proof_to_form(proof)
    assert form_to_proof(form) == proof
    assert verify_form(form, env.kb) is True


def test_tampered_proof_fails():
    env = Env()
    proof = eval_sexp("(fact (p a)) (query (p a))", env)[-1]
    form = proof_to_form(proof)
    tampered = (Sym("proof"), (Sym("p"), Sym("zzz")), form[2])
    assert verify_form(tampered, env.kb) is False


def test_fact_proof_uses_nil_rule():
    env = Env()
    proof = eval_sexp("(fact (p a)) (query (p a))", env)[-1]
    assert proof.is_fact
    assert proof_to_form(proof)[2] == Sym("nil")


# -- 5. source round-trip --------------------------------------------------
def test_theory_source_roundtrip():
    env = Env()
    (theory,) = eval_sexp("(theory t (clause c 1.0 (t ?x ?y) (e ?x ?y)))", env)
    text = theory_source(theory)
    assert text == theory_sexp(theory)
    assert source_roundtrip(theory) is True
    assert source_theory(text) == theory


# -- 6. tree reification ---------------------------------------------------
def test_tree_atoms_deterministic_and_queryable():
    tree = (Sym("ir"), Sym("alan"), (Sym("rel"), Sym("born")))
    a = tree_atoms(tree)
    assert a == tree_atoms(tree)
    assert Atom("leaf", (Const("tree.2.1"), Const("born"))) in a
    assert tree_kb(tree).has_fact(Atom("node", (Const("tree.2"),)))
    assert query_tree(tree, (Sym("leaf"), Sym("tree.2.1"), Sym("born"))) is not None


def test_tree_is_not_logic():
    tree = (Sym("ir"), Sym("alan"), (Sym("rel"), Sym("born")))
    with pytest.raises(SexpError):
        form_to_atom(tree)


# -- trust boundary --------------------------------------------------------
def test_core_does_not_import_lisp():
    tree = ast.parse((REPO / "dlm" / "__init__.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(not a.name.endswith("lisp") for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert "lisp" not in (node.module or "")


def test_lisp_imports_only_the_core_at_module_level():
    tree = ast.parse((REPO / "dlm" / "lisp.py").read_text())
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level > 0:  # relative: only the core package is allowed
            assert node.module in (None, "deductive"), (node.module, node.level)
        else:  # absolute: stdlib only, never an untrusted dlm submodule
            assert not (node.module or "").startswith("dlm"), node.module


def test_determinism():
    program = "(fact (e a b)) (rule step (t ?x ?y) (e ?x ?y)) (query (t a b))"
    first = [r for r in eval_sexp(program, Env()) if isinstance(r, Proof)]
    second = [r for r in eval_sexp(program, Env()) if isinstance(r, Proof)]
    assert [dump(proof_to_form(p)) for p in first] == [
        dump(proof_to_form(p)) for p in second
    ]
