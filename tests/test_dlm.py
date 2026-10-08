"""DLM v0.0002 tests: wire schema, interpreter, decision engine, adapter."""
from __future__ import annotations

import math

import pytest

from dlm import (
    ChainInterpreter,
    ChoiceQuestion,
    DecisionEngine,
    DlmTorso,
    FEATURE_NAMES,
    GroundingInterpreter,
    KnowledgeBase,
    NoulQuestion,
    ParsedOption,
    SchemaInterpreter,
    ScoreQuestion,
    SystemOneService,
    derive_confidence,
    derive_score_confidence,
    fact,
    parse_atom,
    rule,
)
from dlm.interpreter import ParseError
from dlm.terms import V


def reach_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("edge", a, b))
    x, y, z = V("x"), V("y"), V("z")
    kb.add_rule(rule(fact("reach", x, y), fact("edge", x, y), name="base"))
    kb.add_rule(rule(fact("reach", x, z), fact("edge", x, y), fact("reach", y, z), name="step"))
    kb.add_rule(rule(fact("level", 1), fact("reach", "alice", "carol"), name="l1"))
    return kb


# -- schema ---------------------------------------------------------------
def test_confidence_formulas_match_reference():
    assert derive_confidence([1.0, 0.0, 0.0]) == 1.0
    assert derive_confidence([0.5, 0.5]) == 0.0
    assert math.isclose(derive_confidence([1 / 3, 1 / 3, 1 / 3]), 0.0, abs_tol=1e-12)
    assert derive_score_confidence([0.0, 1.0, 0.0]) == 1.0
    assert math.isclose(derive_score_confidence([0.5, 0.0, 0.5]), 0.0, abs_tol=1e-12)


def test_wire_validation():
    with pytest.raises(ValueError):
        ChoiceQuestion(instructions="x", criteria={"only": None})
    with pytest.raises(ValueError):
        ScoreQuestion(instructions="x", criteria=["a"])
    with pytest.raises(ValueError):
        NoulQuestion(instructions="x", criteria={"maybe": None})


# -- interpreter ----------------------------------------------------------
def test_parse_atom_forms():
    assert str(parse_atom("edge(alice, bob)")) == "edge(alice, bob)"
    assert str(parse_atom("node(alice).")) == "node(alice)"
    assert str(parse_atom("reach(?x, ?y)")) == "reach(?x, ?y)"
    assert str(parse_atom('p("a b", 2)')) == "p(a b, 2)"
    with pytest.raises(ParseError):
        parse_atom("alice is connected")


def test_schema_interpreter_negation_and_abstain():
    si = SchemaInterpreter()
    r = si.interpret(None, "not edge(alice, bob)")
    assert r.ok and r.negated and str(r.atom) == "edge(alice, bob)"
    bad = si.interpret(None, "alice is connected to bob")
    assert not bad.ok and bad.atom is None


def test_chain_interpreter_prefers_first_success():
    si = SchemaInterpreter()
    g = GroundingInterpreter(lambda state, opt: ParsedOption(atom=parse_atom("seen(cat)"), ok=True))
    chain = ChainInterpreter(si, g)
    assert str(chain.interpret(None, "edge(a, b)").atom) == "edge(a, b)"
    assert str(chain.interpret(None, "the cat").atom) == "seen(cat)"


# -- decision engine ------------------------------------------------------
def test_noul_true_false_and_abstain():
    eng = DecisionEngine(reach_kb())
    assert eng.noul(NoulQuestion(instructions="reach(alice,carol)")).noul == 1.0
    assert eng.noul(NoulQuestion(instructions="reach(carol,alice)")).noul == 0.0
    abstained = eng.noul(NoulQuestion(instructions="alice knows carol"))
    assert abstained.abstained and abstained.noul == 0.5


def test_choice_single_correct_is_confident():
    eng = DecisionEngine(reach_kb())
    q = ChoiceQuestion(instructions="which?", criteria={
        "a": "reach(alice,dave)", "b": "reach(carol,bob)", "c": "reach(dave,alice)"})
    ans = eng.choice(q)
    assert ans.choice == "a" and not ans.abstained
    assert ans.confidence >= 0.9  # P2: a forced answer is certain


def test_choice_abstains_on_uninterpretable_option():
    eng = DecisionEngine(reach_kb())
    q = ChoiceQuestion(instructions="mixed", criteria={"a": "reach(alice,dave)", "b": "alice is connected"})
    ans = eng.choice(q)
    assert ans.abstained and ans.confidence == 0.0
    assert set(ans.probabilities.values()) == {0.5}  # uniform, never a guess


def test_score_reads_ordinal_levels():
    eng = DecisionEngine(reach_kb())
    ans = eng.score(ScoreQuestion(instructions="rate", criteria=["low", "mid", "high"]))
    assert not ans.abstained
    assert abs(ans.score - 1.0) < 0.05  # level(1) is the derivable level
    assert set(ans.legend) == {"0", "1", "2"}


def test_registered_null_p4_false_positive():
    """P4: an instantiable-but-wrong rule is not separable, so it scores 1.0."""
    kb = reach_kb()
    x, y = V("x"), V("y")
    kb.add_rule(rule(fact("reach", x, y), fact("edge", y, x), name="rev"))  # semantically wrong
    eng = DecisionEngine(kb)
    # reach(bob,alice) is false in the real chain, but rev derives it from edge(alice,bob).
    assert eng.noul(NoulQuestion(instructions="reach(bob,alice)")).noul == 1.0


# -- adapter --------------------------------------------------------------
def test_torso_feature_contract():
    tor = DlmTorso(DecisionEngine(reach_kb()))
    hit = tor.features("", "reach(alice,carol)")
    miss = tor.features("", "reach(carol,alice)")
    assert hit.shape == (len(FEATURE_NAMES),)
    assert hit[0] == 1.0 and hit[1] == 1.0
    assert miss[0] == 1.0 and miss[1] == 0.0
    assert tor.batch_features("", ["reach(alice,carol)", "reach(carol,alice)"]).shape == (2, len(FEATURE_NAMES))
    assert tor.state_features().shape == (4,)


def test_wire_roundtrip():
    svc = SystemOneService(DecisionEngine(reach_kb()))
    out = svc.handle({
        "state": "",
        "questions": {
            "q_entail": {"type": "noul", "instructions": "reach(alice,carol)"},
            "q_pick": {"type": "choice", "instructions": "which?",
                       "criteria": {"a": "reach(alice,dave)", "b": "reach(carol,bob)"}},
            "q_rate": {"type": "score", "instructions": "rate", "criteria": ["low", "mid", "high"]},
        },
    })
    assert out["model"] == "dlm-engine-latest"
    assert out["answers"]["q_entail"]["noul"] == 1.0
    assert out["answers"]["q_pick"]["choice"] == "a"
    assert "legend" in out["answers"]["q_rate"]
    assert out["usage"] == {"input_tokens": 0, "output_tokens": 0}


def test_no_tokenizer_or_lm_head_in_decision_path():
    """The decision path must not import a language model runtime."""
    import sys

    assert "transformers" not in sys.modules
    import dlm.decision  # noqa: F401

    assert "transformers" not in sys.modules