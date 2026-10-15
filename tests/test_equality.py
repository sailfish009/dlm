"""Network-free tests of the v0.0051 equality/congruence layer (D7a).

v0.0051 adds D7a: equality as a FINITE congruence over the given symbol set.  It
lets the kernel conclude that two different symbols denote the SAME layer kind,
which fixes a real false negative -- v0.0050 certified ``absent(net, maxpool2d)``
though the forward pass CALLS ``F.max_pool2d``.  The tests check that the alias
relation is a true equivalence relation, that the extension is conservative (it
adds only ``same_kind``/``uses_layer`` and no positive conclusion), and that the
false negative is reproduced without equality and gone with it.
"""
import os

from dlm import Atom, Const, KnowledgeBase, closure
from dlm.closedworld import absence_rule, absent_kinds, candidate_facts
from dlm.equality import (absence_rule_equality, canonical, kind, same_kind_facts,
                          same_kind_pairs, symbols_in, uses_layer_rules)
from dlm.closedworld import CANDIDATE_LAYERS

from experiments.reading.run import run
from experiments.equal.run import run as run_equal
from experiments.equal.run import _equivalence_holds

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "experiments", "mnist", "cache")
NS_SRC = open(os.path.join(CACHE, "main.py"), "r", encoding="utf-8").read()


# -- canonicalisation ---------------------------------------------------------
def test_prefixes_and_aliases_map_to_a_canonical_kind():
    assert canonical("f_max_pool2d") == "max_pool2d"
    assert kind("f_max_pool2d") == "maxpool2d"
    assert kind("nn_conv2d") == "conv2d"
    assert kind("transforms_normalize") == "normalize"
    assert kind("totally_unrelated") == "totally_unrelated"


def test_same_kind_is_an_equivalence_relation():
    syms = ["f_max_pool2d", "maxpool2d", "nn_conv2d", "conv2d", "other"]
    pairs = same_kind_pairs(syms)
    assert _equivalence_holds(pairs)
    assert ("f_max_pool2d", "maxpool2d") in pairs
    assert ("nn_conv2d", "conv2d") in pairs
    assert ("other", "conv2d") not in pairs


# -- the false negative, synthetic --------------------------------------------
def _tiny_theory():
    facts = {
        Atom("is_module", (Const("net"),)),
        Atom("method_of", (Const("net"), Const("fwd"))),
        Atom("calls", (Const("fwd"), Const("f_max_pool2d"))),
        Atom("has_layer", (Const("net"), Const("linear"))),
    }
    return facts


def test_maxpool_absence_reproduced_without_equality():
    kb = KnowledgeBase(set(_tiny_theory()))
    kb.add_rule(absence_rule())
    kb.add_facts(candidate_facts())
    assert "maxpool2d" in absent_kinds(closure(kb), "net")


def test_equality_blocks_the_functional_absence():
    facts = _tiny_theory()
    kb = KnowledgeBase(set(facts))
    kb.add_facts(candidate_facts())
    kb.add_facts(same_kind_facts(symbols_in(facts)))
    for r in uses_layer_rules():
        kb.add_rule(r)
    kb.add_rule(absence_rule_equality())
    cw = closure(kb)
    assert "maxpool2d" not in absent_kinds(cw, "net")
    assert Atom("uses_layer", (Const("net"), Const("maxpool2d"))) in cw
    # every remaining absence is a candidate the module genuinely does not use
    used = {a.args[1].name for a in cw if a.pred == "uses_layer"}
    assert all(l not in used for l in absent_kinds(cw, "net"))


def test_extension_is_conservative_over_old_predicates():
    facts = _tiny_theory()
    old = closure(KnowledgeBase(set(facts)))
    kb = KnowledgeBase(set(facts))
    kb.add_facts(same_kind_facts(symbols_in(facts)))
    for r in uses_layer_rules():
        kb.add_rule(r)
    new = closure(kb)
    new_preds = {"same_kind", "uses_layer"}
    assert {a for a in new if a.pred not in new_preds} == old


# -- the real program ---------------------------------------------------------
def test_real_program_recognises_the_pool_call():
    r = run_equal(NS_SRC, cache_dir=CACHE, offline=True)
    assert all(r["verdict"].values())
    assert "maxpool2d" in r["used_layers"]
    assert "maxpool2d" not in r["absent_with_equality"]


def test_reading_verdicts_include_equality():
    r = run(NS_SRC, cache_dir=CACHE, offline=True)
    v = r["verdict"]
    assert v["equality_absence_sound"]
    assert v["equality_blocks_functional_absence"]
    assert v["congruence_present"]
    assert "maxpool2d" not in r["absences"]
    assert all(CANDIDATE_LAYERS)  # the universe is still fully enumerated