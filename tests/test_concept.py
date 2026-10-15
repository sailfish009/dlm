"""Network-free tests of the v0.0043 core-concept (gist) layer.

The version adds the missing deduction: from concrete facts + acquired *library*
meanings it reports a HOLE ("what does ``datasets.MNIST`` contain?"), the reader
SEARCHES for domain knowledge, and only then can the kernel derive the core
concept ``recognizes(main, handwritten_digit)``.  Nothing here touches the
network: meanings come from the offline cache and the searched domain knowledge
is injected.  The honesty test is the ablation -- strip the acquired domain facts
and the concept must disappear (abstain).
"""
import os

from dlm.gist import (GIST_FORMS, GIST_GOALS, concept_str, external_holes,
                      strongest_concept)
from experiments.mnist.domain import (DATASET_CUES, dataset_candidates,
                                      domain_facts, reduce_entity)
from experiments.mnist.extract import extract
from experiments.mnist.knowledge import acquire_knowledge
from experiments.concept.run import run

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "experiments", "mnist", "cache")
NS_SRC = open(os.path.join(CACHE, "main.py"), "r", encoding="utf-8").read()

NO_DOMAIN = {"entities": {}, "records": [], "stats": {}}
WITH_DOMAIN = {"entities": {"mnist": "handwritten_digit"}, "records": [],
               "stats": {}}


def _offline_knowledge():
    ext = extract(NS_SRC, "main")
    know = acquire_knowledge(ext["facts"], ext["labels"], cache_dir=CACHE,
                             offline=True)
    return ext, know


# -- the reduction of "what does this dataset contain?" ----------------------
def test_reduce_entity_from_encyclopedic_summaries():
    # the Wikipedia opening paragraphs that the acquirer reduces
    assert reduce_entity(
        "The MNIST database is a large database of handwritten digits that is "
        "commonly used for training various image processing systems.") == "handwritten_digit"
    assert reduce_entity(
        "Fashion-MNIST is a large, freely available dataset of fashion images "
        "that is commonly used for training and testing machine learning "
        "systems.") == "clothing_item"
    assert reduce_entity(
        "The CIFAR-10 dataset contains 60,000 32x32 color images in 10 "
        "different classes.") == "object_category"
    # a definition with no cue yields nothing (abstain, never invent)
    assert reduce_entity("A text file with comma separated values.") is None


def test_dataset_candidates_only_ask_never_answer():
    ext = extract(NS_SRC, "main")
    cands = dataset_candidates(ext["facts"], ext["labels"])
    assert cands == {"mnist": "MNIST"}  # a QUESTION, not a fact
    assert domain_facts({}) == []


def test_gist_rules_name_no_dataset_or_library_symbol():
    text = " ".join(str(part) for rule in GIST_FORMS for part in rule).lower()
    for forbidden in ("mnist", "nn_module", "conv2d", "linear",
                      "pytorch", "cifar", "imagenet"):
        assert forbidden not in text
    # ``dataset_of`` IS the rule's only external predicate: the acquisition seam.
    assert "dataset_of" in text
    assert GIST_GOALS[0] == "recognizes"


def test_gap_is_reported_before_the_search():
    ext = extract(NS_SRC, "main")
    facts = [tuple(f) for f in ext["facts"]]
    cands = dataset_candidates(facts, ext["labels"])
    holes = external_holes(facts, cands)
    assert holes == ["mnist"]
    # once the domain fact exists the hole is closed
    facts.append(("dataset_of", "mnist", "handwritten_digit"))
    assert external_holes(facts, cands) == []


# -- the loop: search -> re-learn -> certify the concept ---------------------
def test_core_concept_derived_only_with_acquired_domain_knowledge():
    _ext, know = _offline_knowledge()

    with_dom = run(NS_SRC, source="cache/main.py", module="main", cache_dir=CACHE,
                   offline=True, knowledge=know, domain=WITH_DOMAIN)
    assert "(recognizes main handwritten_digit)" in with_dom["concepts"]
    assert with_dom["core_concept"] == "(recognizes main handwritten_digit)"
    assert with_dom["verdict"]["core_concept_captured"]
    assert with_dom["verdict"]["core_concept_certified"]
    assert with_dom["proof"]["verified"] is True
    # every emitted sentence cites an atom the kernel actually derived
    assert with_dom["all_sentences_certified"]

    no_dom = run(NS_SRC, source="cache/main.py", module="main", cache_dir=CACHE,
                 offline=True, knowledge=know, domain=NO_DOMAIN)
    assert all("recognizes" not in c for c in no_dom["concepts"])
    assert no_dom["verdict"]["abstains_without_knowledge"]
    assert not no_dom["verdict"]["core_concept_captured"]


def test_two_rounds_relearn_after_the_search():
    _ext, know = _offline_knowledge()
    res = run(NS_SRC, source="cache/main.py", module="main", cache_dir=CACHE,
              offline=True, knowledge=know, domain=WITH_DOMAIN)
    assert len(res["rounds"]) == 2
    r1, r2 = res["rounds"]
    assert r1["gaps"] == ["mnist"]
    assert all("recognizes" not in c for c in r1["concepts"])
    assert any("recognizes" in c for c in r2["concepts"])
    assert res["verdict"]["relearn_after_acquisition"]
    assert res["concept_score"]["score"] == 1.0


def test_concept_sentences_speak_the_acquired_entity():
    _ext, know = _offline_knowledge()
    res = run(NS_SRC, source="cache/main.py", module="main", cache_dir=CACHE,
              offline=True, knowledge=know, domain=WITH_DOMAIN)
    core = [s for s in res["sentences"] if s["level"] == "core"]
    assert len(core) == 1
    text = core[0]["text"].lower()
    assert "handwritten digits" in text and "mnist" in text


def test_strongest_concept_prefers_recognition():
    from dlm import Const, Atom
    atoms = {Atom("trains_model", (Const("main"),)),
             Atom("recognizes", (Const("main"), Const("handwritten_digit"))),
             Atom("is_supervised", (Const("main"),))}
    assert strongest_concept(atoms).pred == "recognizes"
    assert strongest_concept({Atom("is_supervised", (Const("main"),))}).pred == "is_supervised"
    assert strongest_concept(set()) is None
    assert concept_str(None) == "(none)"
    assert concept_str(Atom("recognizes", (Const("main"), Const("handwritten_digit")))) \
        == "(recognizes main handwritten_digit)"