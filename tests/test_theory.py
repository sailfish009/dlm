"""Tests for theory persistence: exact round-trip and resume."""
import os
import tempfile

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.ground import Ground, Experience
from dlm.lisp import form_to_rule
from dlm.theory import (Theory, atom_from_json, atom_to_json, load_theory,
                        rule_from_json, rule_to_json, save_theory, theory_from_dict,
                        theory_to_dict)


def _theory() -> Theory:
    x, y, z = Var("?x"), Var("?y"), Var("?z")
    ground = (form_to_rule(("rule", ("ancestor", "?x", "?y"), ("parent", "?x", "?y"))),)
    experience = (Rule(Atom("ancestor", (x, z)),
                       (Atom("parent", (x, y)), Atom("ancestor", (y, z))), "exp0"),)
    facts = frozenset({
        Atom("parent", (Const("a"), Const("b"))),
        Atom("parent", (Const("b"), Const("c"))),
    })
    return Theory(ground, experience, facts, {"round": 3, "false_final": 0,
                                              "notes": ["resume", "ok"]})


def test_atom_and_rule_json_round_trip():
    a = Atom("p", (Const("a"), Var("?x")))
    assert atom_from_json(atom_to_json(a)) == a
    r = Rule(Atom("q", (Var("?x"),)), (Atom("p", (Var("?x"),)),), "r0")
    assert rule_from_json(rule_to_json(r)) == r


def test_theory_dict_round_trip_and_closure_identity():
    t = _theory()
    assert theory_from_dict(theory_to_dict(t)) == t
    # the loaded theory closes to exactly the same set as the original
    assert closure(theory_from_dict(theory_to_dict(t)).to_kb()) == closure(t.to_kb())


def test_save_load_and_resume():
    t = _theory()
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "theory.json")
        save_theory(path, t)
        back = load_theory(path)
        assert back == t
        assert back.meta["round"] == 3
        # resume = extend the loaded Experience and re-close, no loss of Ground
        extra = Rule(Atom("q", (Var("?x"),)), (Atom("parent", (Var("?x"), Var("?y"))),), "exp1")
        grown = Theory(back.ground, back.experience + (extra,), back.facts, back.meta)
        assert closure(back.to_kb()) <= closure(grown.to_kb())