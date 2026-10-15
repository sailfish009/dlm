"""Network-free tests of the v0.0050 reading additions.

v0.0050 makes the deduction ladder VISIBLE in the final natural-language output:
  * N9 -- the first NEGATIVE sentence, a certified closed-world absence (D5),
    which pure Horn deduction can never produce; and
  * a binding D6 typed admission gate -- an ill-typed theory makes the reader
    ABSTAIN (raise) instead of deriving, while typing never changes the honest
    closure.

The tests assert the realization is a genuine negative, that it appears on the
real program with every sentence certified, that the negative disappears when
the layer is presented (non-monotonic), and that the typed gate is load-bearing.
"""
import os

from dlm import Atom, Const
from dlm.narrative import LEVELS, reading

from experiments.reading.run import run

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "experiments", "mnist", "cache")
NS_SRC = open(os.path.join(CACHE, "main.py"), "r", encoding="utf-8").read()


def _reading(module="main"):
    return run(NS_SRC, module=module, cache_dir=CACHE, offline=True)


# -- the ladder gained a NEGATIVE rung ----------------------------------------
def test_levels_include_absence():
    assert LEVELS[9] == "absence"


# -- synthetic realization ----------------------------------------------------
def test_absent_atom_becomes_a_certified_negative_sentence():
    closed = {Atom("absent", (Const("net"), Const("maxpool2d")))}
    sents = reading(closed, {"net": "Net", "maxpool2d": "maxpool2d"}, {},
                    module="main", meanings={})
    n9 = [s for s in sents if s["level"] == 9]
    assert len(n9) == 1
    assert n9[0]["text"] == "Net does not contain a maxpool2d layer."
    assert n9[0]["certified"] is True
    assert n9[0]["support"] == ["(absent net maxpool2d)"]


def test_article_is_used_before_a_vowel():
    closed = {Atom("absent", (Const("net"), Const("attention")))}
    sents = reading(closed, {"net": "Net"}, {}, module="main", meanings={})
    assert sents[0]["text"] == "Net does not contain an attention layer."


def test_no_negative_without_a_closed_world_conclusion():
    # a closure with no ``absent`` atom must not fabricate a negative sentence
    sents = reading({Atom("has_layer", (Const("net"), Const("linear")))}, {}, {},
                    module="main", meanings={})
    assert not any(s["level"] == 9 for s in sents)


# -- the real reading reaches N9 ----------------------------------------------
def test_reading_reaches_absence_level():
    r = _reading()
    assert r["reading_level"] >= 9
    assert r["levels_present"]["N9_absence"] is True
    assert r["reading_score"] >= 0.99


def test_n9_sentences_are_negatives_and_certified():
    r = _reading()
    n9 = [s for s in r["sentences"] if s["level"] == 9]
    assert n9
    assert all("does not contain" in s["text"] for s in n9)
    assert all(s["certified"] for s in n9)
    assert all(tok.startswith("(absent ") for s in n9 for tok in s["support"])
    assert "lstm" in r["absences"] and "attention" in r["absences"]
    # v0.0051: max-pool is genuinely used (the forward calls F.max_pool2d), so the
    # D7a equality layer correctly RETRACTS the v0.0050 false negative.
    assert "maxpool2d" not in r["absences"]


# -- D5 non-monotonicity and the D6 typed gate --------------------------------
def test_negative_needs_the_closed_world_layer():
    assert _reading()["verdict"]["negative_needs_closed_world"] is True


def test_nonmonotonic_retraction_in_the_reading():
    assert _reading()["verdict"]["nonmonotonic_negative_retracts"] is True


def test_typed_gate_binds_and_preserves_truth():
    r = _reading()
    assert r["verdict"]["typed_gate_binds"] is True
    assert r["verdict"]["typing_does_not_change_truth"] is True


def test_all_reading_verdicts_hold():
    assert all(_reading()["verdict"].values())


def test_deterministic():
    assert _reading() == _reading()