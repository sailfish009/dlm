"""v0.0053 integration: the north-star BODY itself speaks the leveled reading.

Before v0.0053 the body (``experiments/mnist/run.py``) used a private flat realizer
and its own final output never reached the purpose ("recognize ...") sentence; only
the side experiment ``experiments/reading`` did.  These tests pin the fix: the body
emits N1..N9 over structure + acquired ``meaning`` + SEARCHED ``dataset_of`` +
acquired ``api_effect`` + the closed-world/equality absence layer, and it shares ONE
pipeline with the falsifier experiment (``mnist.run.pipeline``).  Network-free.
"""
import os

from experiments.mnist.run import run as body_run
from experiments.reading.run import run as reading_run

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "experiments", "mnist", "cache")
NS_SRC = open(os.path.join(CACHE, "main.py"), "r", encoding="utf-8").read()

_RESULT = {}


def _body():
    if "r" not in _RESULT:
        _RESULT["r"] = body_run(NS_SRC, "inline://northstar", cache_dir=CACHE,
                                offline=True)
    return _RESULT["r"]


# -- the defect itself: the body's own narrative carries the purpose sentence --
def test_body_narrative_contains_purpose_sentence():
    r = _body()
    assert r["northstar_purpose"] is True
    assert any("recognize handwritten digits" in s["text"] for s in r["narrative"]), \
        "the body's final output must contain the learned purpose sentence"


# -- and it reaches the top of the ladder, not just the structural rungs -------
def test_body_reaches_n9_and_is_certified():
    r = _body()
    assert r["reading_level"] == 9
    assert r["all_sentences_verified"] is True
    assert all(s["certified"] for s in r["narrative"])
    assert r["absence_sentences"], "certified negatives must be emitted by the body"
    for lv in ("N4_composition", "N5_architecture", "N6_causal", "N7_purpose",
               "N8_analogy", "N9_absence"):
        assert r["levels_present"][lv] is True, lv


# -- one pipeline: the body and the experiment compute the identical reading ---
def test_body_and_reading_share_one_pipeline():
    body = _body()
    exp = reading_run(NS_SRC, cache_dir=CACHE, offline=True)
    assert [s["text"] for s in body["narrative"]] == [s["text"] for s in exp["sentences"]]
    assert body["sentence_analysis"]["by_level"] == exp["sentence_analysis"]["by_level"]


# -- the searched domain fact is what carries the gist (honesty) ---------------
def test_purpose_depends_on_searched_domain_fact():
    r = _body()
    assert r["domain"]["entities"] == {"mnist": "handwritten_digit"}
    # with no domain fact, the gist must abstain while structure stays
    empty = body_run(NS_SRC, "inline://northstar", cache_dir=CACHE, offline=True,
                     domain={"entities": {}, "records": [], "stats": {}})
    assert empty["northstar_purpose"] is False
    assert empty["all_sentences_verified"] is True
    assert any(s["level"] == 1 for s in empty["narrative"])


def test_body_is_deterministic():
    a = body_run(NS_SRC, "inline://northstar", cache_dir=CACHE, offline=True)
    b = body_run(NS_SRC, "inline://northstar", cache_dir=CACHE, offline=True)
    assert a == b