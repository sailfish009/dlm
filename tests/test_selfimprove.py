"""Integration: the model self-evaluates and closes its own weak spot (v0.0056).

Pins the loop end-to-end on the real north-star slice: the model must DISCOVER
(not be told) that ``recognizes`` is unprovable, identify the acquirable missing
premise, fix it from web-derived knowledge, and abstain rather than invent when
acquisition is scrambled or removed.  Network-free (offline replay).
"""
import os

from experiments.selfimprove.run import run as selfimprove_run
from experiments.mnist.run import READER, pipeline

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "experiments", "mnist", "cache")
NS_SRC = open(os.path.join(CACHE, "main.py"), "r", encoding="utf-8").read()

_RESULT = {}


def _result():
    if "r" not in _RESULT:
        _RESULT["r"] = selfimprove_run(NS_SRC, cache_dir=CACHE, offline=True)
    return _RESULT["r"]


def test_model_discovers_the_recognizes_gap_itself():
    r = _result()
    assert "recognizes" in r["actionable_before"]
    assert r["weak_spots_before"][0]["target"] == "recognizes"
    assert r["weak_spots_before"][0]["external"] == ["dataset_of"]


def test_one_self_directed_acquisition_proves_the_target():
    r = _result()
    assert r["ability_after"]["proved"].get("recognizes")
    assert r["rounds"][0]["gained"] == ["recognizes"]
    assert r["stop"] == "saturated"


def test_controls_abstain_and_scramble():
    r = _result()
    assert r["controls"]["scramble_improved"] is False
    assert r["controls"]["no_web_stop"] == "acquire_empty"
    assert r["verdict"]["scramble_no_gain"] and r["verdict"]["no_web_abstains"]


def test_multi_round_loop_iterates():
    assert _result()["multi_round"]["ok"] is True


def test_all_verdicts_hold():
    r = _result()
    assert r["verdict_ok"], r["verdict"]


def test_deterministic():
    a = selfimprove_run(NS_SRC, cache_dir=CACHE, offline=True)
    b = selfimprove_run(NS_SRC, cache_dir=CACHE, offline=True)
    assert a["rounds"] == b["rounds"]
    assert a["ability_before"] == b["ability_before"]
    assert a["ability_after"] == b["ability_after"]


def test_reader_owns_assess_and_self_improve():
    p = pipeline(NS_SRC, module="main", cache_dir=CACHE, offline=True, domain={})
    ab = READER.assess(p)
    assert "recognizes" in ab.actionable
    res = READER.self_improve(
        p, acquire=lambda spot: {"facts": [("dataset_of", "mnist", "handwritten_digit")],
                                 "provenance": {"test": True}},
        external={"dataset_of"}, max_rounds=2)
    assert res.ability_after.is_proved("recognizes")