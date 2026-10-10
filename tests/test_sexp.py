"""Tests for the canonical S-expr concrete syntax (module 2)."""
from __future__ import annotations

import pytest

from dlm.logic import Atom, Const, Literal, Rule, Var
from dlm.sexp import (
    SexpError,
    Sym,
    atom_to_form,
    dump,
    dump_all,
    form_to_atom,
    form_to_literal,
    form_to_rule,
    literal_to_form,
    parse,
    rule_to_form,
)


# -- reader ----------------------------------------------------------------
def test_parse_atom():
    assert parse("(calls alice bob)") == ((Sym("calls"), Sym("alice"), Sym("bob")),)


def test_parse_multiple_top_level_forms():
    assert parse("(a) (b c)") == ((Sym("a"),), (Sym("b"), Sym("c")))


def test_parse_nesting_is_general():
    assert parse("(a (b c))") == ((Sym("a"), (Sym("b"), Sym("c"))),)


def test_parse_variables_are_symbols():
    assert parse("(parent ?x ?y)") == ((Sym("parent"), Sym("?x"), Sym("?y")),)


def test_comments_are_ignored():
    assert parse("(a) ; trailing\n(b)") == ((Sym("a"),), (Sym("b"),))


def test_string_literals_distinguish_from_symbols():
    forms = parse('("a" a)')
    assert forms == (("a", Sym("a")),)
    assert isinstance(forms[0][0], str) and not isinstance(forms[0][0], Sym)


def test_empty_input_is_no_forms():
    assert parse("   ; nothing\n") == ()


def test_unbalanced_open():
    with pytest.raises(SexpError):
        parse("(a b")


def test_unbalanced_close():
    with pytest.raises(SexpError):
        parse("a)")


def test_unterminated_string():
    with pytest.raises(SexpError):
        parse('(a "b)')


# -- writer ----------------------------------------------------------------
def test_dump_atom_and_nullary():
    assert dump((Sym("rains"),)) == "(rains)"
    assert dump((Sym("p"), Sym("a"))) == "(p a)"


def test_dump_quotes_string_literals():
    assert dump("a b") == '"a b"'


def test_round_trip():
    text = "(rule (ancestor ?x ?y) (parent ?x ?y))\n(proof (a b) (c))"
    assert parse(dump_all(parse(text))) == parse(text)


# -- logic bridge ----------------------------------------------------------
def test_atom_form_round_trip():
    a = Atom("parent", (Const("alice"), Var("x")))
    assert atom_to_form(a) == (Sym("parent"), Sym("alice"), Sym("?x"))
    assert form_to_atom(atom_to_form(a)) == a


def test_literal_not_form():
    lit = Literal(Atom("charges", (Const("c1"), Const("c2"))), negated=True)
    assert literal_to_form(lit) == (Sym("not"), (Sym("charges"), Sym("c1"), Sym("c2")))
    assert form_to_literal(literal_to_form(lit)) == lit


def test_positive_literal_form_has_no_not():
    lit = Literal(Atom("p", (Const("a"),)))
    assert literal_to_form(lit) == (Sym("p"), Sym("a"))


def test_atom_str_is_sexp():
    # logic.py renders atoms in the same canonical notation as this module.
    assert str(Atom("parent", (Const("alice"), Const("bob")))) == "(parent alice bob)"
    assert dump(atom_to_form(Atom("parent", (Const("alice"), Const("bob"))))) == "(parent alice bob)"


# -- layer separation ------------------------------------------------------
def test_parser_accepts_nesting_but_bridge_rejects_it():
    # syntax is general; the function-free core cannot turn a nested arg into a term.
    forms = parse("(p (q a))")
    with pytest.raises(SexpError):
        form_to_atom(forms[0])


def test_untrusted_input_is_data_not_code():
    # "(eval (danger))" is parsed as plain data; nothing is executed.
    assert parse("(eval (danger))") == ((Sym("eval"), (Sym("danger"),)),)


# -- rules -----------------------------------------------------------------
def test_rule_form_round_trip():
    r = form_to_rule(parse("(rule (ancestor ?x ?y) (parent ?x ?y))")[0])
    assert r.head == Atom("ancestor", (Var("x"), Var("y")))
    assert dump(rule_to_form(r)) == "(rule (ancestor ?x ?y) (parent ?x ?y))"


def test_named_rule_form():
    r = form_to_rule(parse("(rule anc (ancestor ?x ?y) (parent ?x ?y))")[0])
    assert r.name == "anc"
    assert dump(rule_to_form(r)) == "(rule anc (ancestor ?x ?y) (parent ?x ?y))"


def test_rule_form_rejects_unsafe_rule():
    with pytest.raises(ValueError):
        form_to_rule(parse("(rule (p ?x) (q a))")[0])