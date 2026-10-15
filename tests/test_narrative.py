"""Network-free tests of the v0.0047 leveled narrative realizer.

The version raises the measured level of the final natural-language output from
N7 (purpose) to N8: a structural analogy between two routines that share
CERTIFIED calls but have DISJOINT regimes (e.g. train vs test).  The tests
assert the ladder reaches N8 on the real program, that every sentence stays
kernel-certified, that the analogy rests on certified calls + a certified regime
difference (never an asserted similarity), and that the honesty ablation still
holds: strip the acquired domain knowledge and the N7 gist disappears.
"""
import os

from dlm import Atom, Const
from dlm.narrative import (LEVELS, reading, reading_level, reading_score,
                           role_of)
from experiments.reading.run import run

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "experiments", "mnist", "cache")
NS_SRC = open(os.path.join(CACHE, "main.py"), "r", encoding="utf-8").read()


def _reading(module="main"):
    return run(NS_SRC, module=module, cache_dir=CACHE, offline=True)


# -- the role normaliser ------------------------------------------------------
def test_role_of_normalises_layer_names():
    assert role_of("self_conv1") == "conv"
    assert role_of("f_max_pool2d") == "pool"
    assert role_of("self_fc2") == "linear"
    assert role_of("f_log_softmax") == "softmax"
    assert role_of("mystery_op") == "mystery_op"   # unknown stays unknown


# -- the ladder ---------------------------------------------------------------
def test_reading_reaches_analogy_level():
    r = _reading()
    assert r["reading_level"] >= 8
    for lv in ("N4_composition", "N5_architecture", "N6_causal", "N7_purpose",
               "N8_analogy"):
        assert r["levels_present"][lv] is True
    assert r["reading_score"] >= 0.99


def test_every_sentence_is_kernel_certified():
    r = _reading()
    assert r["sentences"]
    assert all(s["certified"] for s in r["sentences"])
    assert r["all_sentences_certified"] is True
    assert all(r["verdict"].values())


def test_n4_names_a_bounded_gradient_step():
    r = _reading()
    n4 = [s for s in r["sentences"] if s["level"] == 4]
    assert len(n4) == 1
    text = n4[0]["text"]
    # bounded and named, not a raw source-order chain
    assert "one gradient step" in text
    assert "(reset)" in text and "(backward)" in text and "(update)" in text
    # the window starts at the reset and ends at the update
    assert text.index("zero_grad") < text.index("backward") < text.index("optimizer.step")


def test_n5_architecture_is_role_normalised_and_ordered():
    r = _reading()
    n5 = [s for s in r["sentences"] if s["level"] == 5]
    assert len(n5) == 1
    text = n5[0]["text"]
    assert "Net.forward" in text and "->" in text
    assert "conv" in text and "softmax" in text   # roles, not concrete names
    assert "classifier head" in text
    # support is the ordered before-chain, all inside the closure
    assert n5[0]["support"]
    assert all("(before " in tok for tok in n5[0]["support"])


def test_n6_causal_is_backed_by_api_effect_facts():
    r = _reading()
    n6 = [s for s in r["sentences"] if s["level"] == 6]
    assert n6
    assert all("in order to" in s["text"] for s in n6)
    # the backward step carries a real reason, not a restatement of the call
    back = [s for s in n6 if "loss.backward" in s["text"]]
    assert back and "compute the gradients" in back[0]["text"]
    # each why is supported by the observed call AND the acquired api_effect fact
    for s in n6:
        assert any(tok.startswith("(calls ") for tok in s["support"])
        assert any(tok.startswith("(api_effect ") for tok in s["support"])


def test_n7_gist_names_no_library_symbol_or_dataset():
    r = _reading()
    n7 = [s for s in r["sentences"] if s["level"] == 7 and "recognize" in s["text"]]
    assert len(n7) == 1
    text = n7[0]["text"]
    low = text.lower()
    for token in ("mnist", "torch", "pytorch", "conv", "linear", "zero_grad", "backward"):
        assert token not in low
    assert "handwritten digits" in low          # the ACQUIRED meaning, named fine
    assert n7[0]["support"] == ["(recognizes main handwritten_digit)"]


def test_n8_analogy_aligns_two_disjoint_regimes():
    r = _reading()
    n8 = [s for s in r["sentences"] if s["level"] == 8]
    assert n8
    text = n8[0]["text"]
    # the meaningful analogy is train vs test (disjoint regimes), not the
    # orchestrator `main` which carries both regimes
    assert "train" in text and "test" in text
    assert "while" in text and "both call" in text
    # support = certified shared calls (both sides) + certified regime atoms
    sup = n8[0]["support"]
    assert any(tok.startswith("(calls train ") for tok in sup)
    assert any(tok.startswith("(calls test ") for tok in sup)
    assert "(backpropagates train)" in sup and "(uses_grad_free test)" in sup
    assert n8[0]["certified"] is True


def test_honesty_ablation_gist_needs_searched_domain():
    r = _reading()
    assert r["verdict"]["abstains_without_domain"] is True
    # without the domain premise the recognizer sentence is simply not emitted
    assert not any("recognize" in t.lower() for t in r["ablation_without_domain"])


def test_deterministic():
    assert _reading() == _reading()


# -- helpers abstain cleanly --------------------------------------------------
def test_empty_reading_is_level_zero():
    assert reading_level([]) == 0
    assert reading_score([]) == 0.0
    assert LEVELS[5] == "architecture"


def test_reading_abstains_when_nothing_is_derivable():
    # an empty closure/labels/pipelines -> no sentences, level 0
    assert reading(set(), {}, {}, module="main", meanings={}) == []