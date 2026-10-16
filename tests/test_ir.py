import json

import pytest

from dlm import (IRValidationError, canonical_json, dag_index, dump, from_json,
                 loads, new_state, node_id, validate_model_state)


def test_sexp_is_lossless_for_strings_and_typed_terms():
    form = ("atom", "strange pred", ("const", "New York"),
            ("const", "123"), ("const", "("), ("var", "x"))
    assert loads(dump(form)) == form


def test_json_is_exactly_one_ir_expression():
    state = new_state(())
    restored = from_json(canonical_json(state))
    assert restored == state
    assert json.loads(canonical_json(state))[0] == "model-state"


def test_content_id_and_dag_view_are_deterministic():
    form = ("root", ("leaf", "x"), ("leaf", "x"))
    assert node_id(form) == node_id(loads(dump(form)))
    index = dag_index(form)
    assert index[node_id(("leaf", "x"))] == ("leaf", "x")
    assert len(index) == 2


def test_model_state_schema_rejects_missing_or_wrong_sections():
    validate_model_state(new_state(()))
    with pytest.raises(IRValidationError):
        validate_model_state(("model-state", ("version", "0.0.65")))


def test_reader_rejects_multiple_expressions_and_non_symbol_heads():
    with pytest.raises(IRValidationError):
        loads("(a) (b)")
    with pytest.raises(IRValidationError):
        loads("(1 x)")
