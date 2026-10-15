"""Integration: closed-loop recursive self-supervised learning (v0.0058).

Pins the north-star loop end-to-end on the real slice, network-free (offline
replay): the model must ADMIT each new program into its own corpus, INDUCE
concepts over what it already had, TRANSFER them to the held-out program by
proof, keep reifying its own calls relation, and SUMMARISE every round in a
natural-language sentence built from its own derived conclusions -- with no
self-termination short of the cap / the user.
"""
import os

from experiments.selfssl.run import (
    KNOWLEDGE_CACHE, reduce_program, run, source_stream,
)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "experiments", "mnist", "cache")
NS_SRC = open(os.path.join(CACHE, "main.py"), "r", encoding="utf-8").read()

_RESULT = {}


def _result():
    if "r" not in _RESULT:
        _RESULT["r"] = run(max_rounds=9, cache_dir=KNOWLEDGE_CACHE, offline=True,
                           do_reading=False)
    return _RESULT["r"]


def test_stream_is_deterministic_and_starts_at_the_north_star():
    s1 = source_stream(KNOWLEDGE_CACHE)
    s2 = source_stream(KNOWLEDGE_CACHE)
    first = [next(s1) for _ in range(4)]
    again = [next(s2) for _ in range(4)]
    assert first == again
    assert first[0] == ("northstar", NS_SRC)
    assert first[1][0] == "p0"
    assert "import torch" in first[1][1]


def test_reduce_program_namespaces_the_subject_only():
    under, edges = reduce_program("prog", NS_SRC, cache_dir=CACHE, offline=True)
    assert under, "the reduction must derive UNDERSTANDING atoms"
    assert all(a.args[0].name.startswith("prog__") for a in under)
    # shared constants in the rest-args stay un-namespaced so features align
    layers = {a.args[1].name for a in under if a.pred == "has_layer"}
    assert layers and all("__" not in l for l in layers)
    # the raw calls relation is name-spaced on both ends
    assert edges and all(a.startswith("prog__") and b.startswith("prog__")
                         for a, b in edges)


def test_every_round_gets_a_natural_language_summary():
    r = _result()
    assert r["rounds_run"] == 9
    assert r["all_ok"]
    for rd in r["rounds"]:
        assert rd["summary"] and rd["summary"].endswith(".")
        assert rd["source"] in rd["summary"]
        assert "Round" in rd["summary"]


def test_corpus_and_reach_grow_but_never_terminate_the_loop():
    r = _result()
    facts = [rd["corpus_facts"] for rd in r["rounds"]]
    assert facts == sorted(facts) and facts[-1] > facts[0]
    reach = [rd["reach_pairs"] for rd in r["rounds"]]
    assert reach == sorted(reach) and reach[-1] > reach[0]
    # the loop never self-terminates; only the cap (or the user) stops it
    assert r["interrupted"] is False


def test_concepts_are_induced_and_transfer_by_proof():
    r = _result()
    induced = [rd for rd in r["rounds"] if rd["concepts"] > 0]
    assert induced, "the corpus must become large enough to induce a concept"
    assert any(rd["concepts_transferred"] > 0 for rd in r["rounds"]), \
        "an induced concept must re-derive on a held-out program by proof"
    # transfer is real deduction, not a re-description: the count is
    # <= the number of induced concepts.
    for rd in r["rounds"]:
        assert rd["concepts_transferred"] <= rd["concepts"]


def test_self_evaluation_reports_the_honest_open_promise():
    r = _result()
    last = r["rounds"][-1]
    # the model still cannot prove `recognizes` without acquired `dataset_of`
    assert "recognizes" in last["open"]
    assert "recognizes" in last["actionable"]
    assert last["proved"] < last["targets"]


def test_loop_is_deterministic_offline():
    a = run(max_rounds=4, cache_dir=KNOWLEDGE_CACHE, offline=True, do_reading=False)
    b = run(max_rounds=4, cache_dir=KNOWLEDGE_CACHE, offline=True, do_reading=False)
    for ra, rb in zip(a["rounds"], b["rounds"]):
        assert {k: v for k, v in ra.items() if k != "seconds"} == \
               {k: v for k, v in rb.items() if k != "seconds"}


def test_summarize_uses_only_model_outputs():
    from experiments.selfssl.run import _summarize
    m = {"round": 0, "source": "prog", "new_facts": 7, "corpus_facts": 0,
         "concepts": 0, "concept_literals": [], "concepts_transferred": 0,
         "transfer_instances": 0, "derived_atoms": 109, "targets": 15,
         "proved": 14, "open": ["recognizes"], "actionable": ["recognizes"],
         "external": {"recognizes": ["dataset_of"]}, "reach_depth": 2,
         "reach_pairs": 87, "reading": None}
    text = _summarize(m, None)
    assert text.endswith(".") and "Round 0 read prog" in text
    assert "recognizes" in text and "dataset_of" in text
    assert "109" in text and "14/15" in text and "depth 2" in text