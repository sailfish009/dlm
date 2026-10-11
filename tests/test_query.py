import pytest

from dlm.logic import Atom, Const, Literal, Var
from dlm.query import WH, YESNO, Query, answer_atoms


def test_yesno_needs_literal():
    with pytest.raises(ValueError):
        Query(YESNO)
    lit = Literal(Atom("happy", (Const("alice"),)))
    assert Query(YESNO, literal=lit).is_yesno()


def test_wh_needs_patterns_and_answer():
    with pytest.raises(ValueError):
        Query(WH)
    pat = Atom("in", (Const("alice"), Var("x")))
    with pytest.raises(ValueError):
        Query(WH, patterns=(pat,))  # no answer var / predicate flag
    q = Query(WH, patterns=(pat,), answer_var=Var("x"))
    assert q.is_wh()
    assert answer_atoms(q) == (pat,)


def test_predicate_answer_needs_no_var():
    pat = Atom("happy", (Const("alice"),))
    q = Query(WH, patterns=(pat,), answer_is_predicate=True)
    assert q.answer_var is None and q.answer_is_predicate


def test_answer_atoms_empty_for_yesno():
    lit = Literal(Atom("happy", (Const("alice"),)))
    assert answer_atoms(Query(YESNO, literal=lit)) == ()