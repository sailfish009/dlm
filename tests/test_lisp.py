"""Tests for the lisp automation API: round-trip, findall, prove/verify, abstain."""
from dlm.lisp import Abstain, Env, dump, eval_sexp, parse
from dlm.proof import form_to_proof, verify


def _family_env():
    env = Env()
    eval_sexp("(fact (parent a b))", env)
    eval_sexp("(fact (parent b c))", env)
    eval_sexp("(rule (ancestor ?x ?y) (parent ?x ?y))", env)
    eval_sexp("(rule (ancestor ?x ?y) (parent ?x ?z) (ancestor ?z ?y))", env)
    return env


def test_internal_round_trip_is_exact():
    forms = [
        ("ancestor", "?x", "?y"),
        ("rule", ("ancestor", "?x", "?y"), ("parent", "?x", "?y")),
        ("proof", ("ancestor", "a", "b"), ("fact",)),
        ("nested", ("a", ("b", ("c",))), "_"),
    ]
    for f in forms:
        assert parse(dump(f))[0] == f


def test_findall_enumerates_derived_atoms():
    env = _family_env()
    got = eval_sexp("(findall (ancestor ?x ?y))", env)[0]
    assert got == (("ancestor", "a", "b"), ("ancestor", "a", "c"),
                   ("ancestor", "b", "c"))


def test_prove_is_data_and_reverifies():
    env = _family_env()
    proof_form = eval_sexp("(prove (ancestor a c))", env)[0]
    assert proof_form[0] == "proof"
    assert form_to_proof(proof_form) is not None
    assert verify(form_to_proof(proof_form), env.kb) is True
    # the proof form survives a dump -> parse round-trip and still verifies
    again = parse(dump(proof_form))[0]
    assert verify(form_to_proof(again), env.kb) is True


def test_verify_rejects_tampered_proof():
    env = _family_env()
    proof_form = eval_sexp("(prove (ancestor a c))", env)[0]
    tampered = ("proof", ("ancestor", "a", "zzz")) + tuple(proof_form[2:])
    assert verify(form_to_proof(tampered), env.kb) is False


def test_abstain_is_a_value_not_an_exception():
    env = _family_env()
    got = eval_sexp("(prove (ancestor c a))", env)[0]
    assert isinstance(got, Abstain)
    assert eval_sexp("(abstain nothing-known)", env) == (Abstain("nothing-known"),)


def test_macro_generates_a_rule_that_only_the_kernel_confirms():
    # code that writes code: a macro expands a call into a (rule ...) form, which
    # the same eval_form asserts -- but only the kernel decides truth.
    env = _family_env()
    eval_sexp("(defmacro ancestor-direct (?x ?y) (rule (anc-d ?x ?y) (parent ?x ?y)))", env)
    eval_sexp("(ancestor-direct a b)", env)
    assert eval_sexp("(query (anc-d a b))", env) == (True,)
    # the macro rewrites, but the kernel still refuses an empty body: the body
    # (parent c a) is not a fact, so the head is not derivable
    eval_sexp("(ancestor-direct c a)", env)
    assert eval_sexp("(query (anc-d c a))", env) == (False,)