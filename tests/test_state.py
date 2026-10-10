"""Tests for seam A: structured state -> facts (module 4 / ingress)."""
from __future__ import annotations

import pytest

from dlm.convert import Ingestor, state_to_facts
from dlm.kb import DictStateGrounder, KnowledgeBase, StateBinding, StateGrounder
from dlm.logic import Atom, Const, Frame, Schema, SchemaRegistry
from dlm.reader import LexicalReader


def registry():
    return SchemaRegistry(
        [
            Schema("weather", ("condition",)),
            Schema("raining", ("state",)),
            Schema("parent", ("parent", "child")),
        ]
    )


# -- bindings --------------------------------------------------------------
def test_state_binding_rejects_empty_or_duplicate_roles():
    with pytest.raises(ValueError):
        StateBinding("k", "p", ())
    with pytest.raises(ValueError):
        StateBinding("k", "p", ("a", "a"))


def test_duplicate_binding_key_raises():
    with pytest.raises(ValueError):
        DictStateGrounder(
            [StateBinding("k", "p", ("r",)), StateBinding("k", "q", ("r",))]
        )


# -- dict grounder ---------------------------------------------------------
def test_scalar_grounding():
    g = DictStateGrounder([StateBinding("weather", "weather", ("condition",))])
    assert g.ground({"weather": "rain"}) == (
        Frame("weather", (("condition", Const("rain")),)),
    )


def test_bool_and_int_conventions_are_fixed():
    g = DictStateGrounder(
        [
            StateBinding("raining", "raining", ("state",)),
            StateBinding("weather", "weather", ("condition",)),
        ]
    )
    assert g.ground({"raining": True, "weather": 3}) == (
        Frame("raining", (("state", Const("true")),)),
        Frame("weather", (("condition", Const("3")),)),
    )


def test_multi_role_from_mapping_and_from_sequence():
    g = DictStateGrounder([StateBinding("edge", "parent", ("parent", "child"))])
    by_map = g.ground({"edge": {"parent": "a", "child": "b"}})
    by_seq = g.ground({"edge": ["a", "b"]})
    expected = (Frame("parent", (("parent", Const("a")), ("child", Const("b")))),)
    assert by_map == expected
    assert by_seq == expected


def test_undeclared_key_is_dropped_or_strict_abstains():
    bindings = [StateBinding("weather", "weather", ("condition",))]
    lenient = DictStateGrounder(bindings)
    strict = DictStateGrounder(bindings, strict=True)
    state = {"weather": "rain", "mystery": "x"}
    assert lenient.ground(state) == (Frame("weather", (("condition", Const("rain")),)),)
    assert strict.ground(state) == ()


def test_unsupported_value_is_ungroundable():
    g = DictStateGrounder([StateBinding("weather", "weather", ("condition",))])
    assert g.ground({"weather": {"nested": 1}}) == ()
    assert DictStateGrounder(
        [StateBinding("weather", "weather", ("condition",))], strict=True
    ).ground({"weather": object()}) == ()


def test_non_mapping_state_abstains():
    g = DictStateGrounder([StateBinding("weather", "weather", ("condition",))])
    assert g.ground(["weather", "rain"]) == ()
    assert g.ground(None) == ()


def test_dict_grounder_satisfies_protocol():
    assert isinstance(DictStateGrounder(), StateGrounder)


# -- ingress composition ---------------------------------------------------
def test_state_to_facts_normalizes_and_checks_schema():
    g = DictStateGrounder([StateBinding("weather", "weather", ("condition",))])
    assert state_to_facts(g, registry(), {"weather": "rain"}) == (
        Atom("weather", (Const("rain"),)),
    )


def test_state_to_facts_abstains_on_schema_mismatch():
    # binding says role 'condition' but the schema wants 'state'
    g = DictStateGrounder([StateBinding("raining", "raining", ("condition",))])
    assert state_to_facts(g, registry(), {"raining": True}) == ()


def test_ingestor_facts_path():
    ing = Ingestor(
        LexicalReader(predicates={"calls"}),
        registry(),
        DictStateGrounder([StateBinding("weather", "weather", ("condition",))]),
    )
    assert ing.facts({"weather": "rain"}) == (Atom("weather", (Const("rain"),)),)
    assert ing.facts({"unknown": "x"}) == ()


def test_ingestor_without_grounder_abstains_on_state():
    ing = Ingestor(LexicalReader(), registry())
    assert ing.facts({"weather": "rain"}) == ()


def test_grounded_facts_enter_the_kb():
    g = DictStateGrounder([StateBinding("weather", "weather", ("condition",))])
    kb = KnowledgeBase().add_facts(state_to_facts(g, registry(), {"weather": "rain"}))
    assert kb.has_fact(Atom("weather", (Const("rain"),)))
    assert len(kb) == 1