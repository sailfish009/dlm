"""Offline tests for the web + kernel self-supervision experiment (NOTE §43).

No test touches the network: the Wikidata/Wikipedia layer is exercised through
its pure parsers and cache, and the end-to-end harness runs on a synthetic
corpus with ``web.extract`` monkeypatched.
"""
from __future__ import annotations

import argparse
from random import Random

from dlm.engine import closure
from dlm.logic import Atom, Const
from dlm.selfsup import FeatureScorer

from experiments.webssl import run as runmod
from experiments.webssl import web as webmod
from experiments.webssl.bridge import (
    build_kb,
    default_rules,
    derived_atoms,
    fact_to_atom,
    supports,
)
from experiments.webssl.proposer import (
    LearnedNlProposer,
    StructuralScorer,
    SurfaceScorer,
    atom_text,
    nl_pair_features,
    train_nl_proposer,
)
from experiments.webssl.web import Doc, Fact, WebCache, _entity_targets, slug, split_sentences


def A(pred, *names):
    return Atom(pred, tuple(Const(n) for n in names))


# -- web layer (pure helpers + cache) --------------------------------------
def test_slug_is_a_single_token():
    assert slug("Marie Curie") == "marie_curie"
    assert slug("  K. Gödel!! ") == "k_g_del"
    assert slug("") == "unknown"


def test_split_sentences_drops_fragments():
    text = "Alan Turing was a mathematician. He was born in London! Ok? Yes, indeed he was."
    got = split_sentences(text)
    assert got[0] == "Alan Turing was a mathematician."
    assert all(len(s) >= 12 for s in got)
    assert "Ok?" not in got


def test_entity_targets_keeps_only_entity_valued_claims():
    ent = {
        "claims": {
            "P31": [{"mainsnak": {"datavalue": {"type": "wikibase-entityid", "value": {"id": "Q5"}}}}],
            "P106": [{"mainsnak": {"datavalue": {"type": "string", "value": "mathematician"}}}],
        }
    }
    assert _entity_targets(ent) == [("instance_of", "Q5")]


def test_web_cache_roundtrip_and_offline_miss(tmp_path):
    cache = WebCache(str(tmp_path))
    assert cache.get("k", lambda: {"v": 1}) == {"v": 1}
    # a fresh cache with the same dir reads from disk, not the producer
    again = WebCache(str(tmp_path))
    assert again.get("k", lambda: (_ for _ in ()).throw(AssertionError("refetched"))) == {"v": 1}
    offline = WebCache(str(tmp_path / "empty"), offline=True)
    try:
        offline.get("missing", lambda: {})
    except FileNotFoundError:
        pass
    else:  # pragma: no cover
        raise AssertionError("offline cache miss should raise")


# -- bridge: web facts -> kernel -------------------------------------------
def _toy_facts():
    hierarchy = [
        Fact("subclass_of", "scientist", "person"),
        Fact("subclass_of", "physicist", "scientist"),
        Fact("subclass_of", "city", "place"),
    ]
    facts = [
        Fact("instance_of", "curie", "physicist"),
        Fact("occupation", "curie", "physicist"),
        Fact("birthplace", "curie", "warsaw"),
        Fact("instance_of", "paris", "city"),
        Fact("located_in", "paris", "france"),
    ]
    return hierarchy, facts


def test_default_rules_have_five_general_laws():
    names = {r.name for r in default_rules()}
    assert {"subclass_trans", "occupation_up", "instance_up"} <= names


def test_kernel_derives_multi_hop_truth_from_web_facts():
    hierarchy, facts = _toy_facts()
    kb = build_kb(hierarchy, facts)
    every = closure(kb)
    # transitive class chain + inheritance up it
    assert A("subclass_of", "physicist", "person") in every
    assert A("instance_of", "curie", "person") in every
    assert A("occupation", "curie", "person") in every
    # derived, not stated
    derived = derived_atoms(kb, hierarchy + facts)
    assert A("instance_of", "curie", "person") in derived
    # a directly stated fact is not "derived"
    assert fact_to_atom(Fact("instance_of", "curie", "physicist")) not in derived


def test_supports_keeps_only_atoms_the_kernel_can_prove():
    hierarchy, facts = _toy_facts()
    kb = build_kb(hierarchy, facts)
    bad = [Fact("birthplace", "nobody", "nowhere")]
    kept = supports(kb, facts + bad)
    assert Fact("birthplace", "curie", "warsaw") in kept
    assert bad[0] not in kept


# -- proposers (untrusted) -------------------------------------------------
def test_structural_scorer_ranks_what_it_trained_on():
    sc = StructuralScorer()
    atoms = [A("instance_of", "a", "b"), A("instance_of", "a", "c")]
    from dlm.selfsup import Example, train
    from dlm.logic import Literal
    examples = (Example("x", Literal(atoms[0]), True), Example("x", Literal(atoms[1]), False))
    train(sc.scorer, examples, kb=None, epochs=8)
    assert sc.rank(atoms)[0] == atoms[0]
    assert sc.trained and sc.feature_count() > 0


def test_surface_scorer_prefers_sentences_that_share_tokens():
    sc = SurfaceScorer()
    sentence = "Marie Curie was born in Warsaw."
    good = A("birthplace", "curie", "warsaw")
    bad = A("occupation", "curie", "physicist")
    assert sc.rank(sentence, [bad, good])[0] == good
    assert atom_text(good) == "(birthplace curie warsaw)"


# -- learned NL proposer (the CLM seam, SSL-NL) ----------------------------
def test_nl_pair_features_are_predicate_conditioned():
    feats = set(nl_pair_features("Marie was born in Warsaw.", A("birthplace", "curie", "warsaw")))
    assert "pred=birthplace&w=born" in feats  # the cue that surface overlap misses
    assert "pred=birthplace&objtok=warsaw" in feats
    assert "pred=birthplace&obj_seen=True" in feats


def _nl_pairs():
    cities = ["warsaw", "paris", "london"]
    pairs = []
    for i, city in enumerate(cities):
        slug = f"e{i}"
        pairs.append(
            (
                slug,
                f"Person{i} was born in {city.title()}.",
                [A("birthplace", slug, city)],
                [A("birthplace", slug, c) for c in cities]
                + [A("occupation", slug, "physicist"), A("instance_of", slug, "person")],
            )
        )
    for i in range(3):
        slug = f"p{i}"
        pairs.append(
            (
                slug,
                f"Scientist{i} worked as a physicist.",
                [A("occupation", slug, "physicist")],
                [A("occupation", slug, o) for o in ("physicist", "chemist", "writer")]
                + [A("birthplace", slug, "warsaw"), A("instance_of", slug, "person")],
            )
        )
    return pairs


def test_learned_nl_proposer_learns_cue_words_and_transfers():
    prop = train_nl_proposer(_nl_pairs(), epochs=15, lr=0.2, seed=0)
    # the shared cue word was learned, not just the seen object
    assert prop.weights.get("pred=birthplace&w=born", 0.0) > 0.0
    # held-out entity AND unseen object ("rome"): cue "born" must select birthplace
    sent = "Dana was born in Rome."
    cands = [A("birthplace", "dana", "rome"), A("occupation", "dana", "physicist"),
             A("instance_of", "dana", "person")]
    assert prop.rank(sent, cands)[0] == A("birthplace", "dana", "rome")
    # cue "physicist" selects occupation, not birthplace
    sent2 = "Eve was a physicist."
    cands2 = [A("birthplace", "eve", "rome"), A("occupation", "eve", "physicist"),
              A("instance_of", "eve", "person")]
    assert prop.rank(sent2, cands2)[0] == A("occupation", "eve", "physicist")


def test_nl_folds_hold_out_entities_and_cover_all():
    pairs = _nl_pairs()
    seen = set()
    for train, test in runmod._nl_folds(pairs, k=3, seed=0):
        tr, te = {p[0] for p in train}, {p[0] for p in test}
        assert te and not (tr & te)
        seen |= te
    assert seen == {p[0] for p in pairs}


def test_learned_nl_proposer_save_load_roundtrip(tmp_path):
    prop = train_nl_proposer(_nl_pairs(), epochs=10, lr=0.2, seed=0)
    path = tmp_path / "nl_reader.json"
    prop.save(str(path))
    again = LearnedNlProposer.load(str(path))
    assert again.weights == prop.weights
    assert again.updates == prop.updates
    sent = "Dana was born in Rome."
    cands = [A("birthplace", "dana", "rome"), A("occupation", "dana", "physicist")]
    assert again.rank(sent, cands) == prop.rank(sent, cands)
    # a foreign/corrupt artifact is rejected rather than silently loaded
    bad = tmp_path / "bad.json"
    bad.write_text('{"format": "nope"}', encoding="utf-8")
    try:
        LearnedNlProposer.load(str(bad))
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("unknown weights format should raise")


# -- harness internals -----------------------------------------------------
def test_perm_negatives_are_schema_violations_not_entailed():
    entailed = {A("subclass_of", "a", "b")}
    pos = [A("subclass_of", "a", "b")]
    negs = runmod._perm_negatives(pos, entailed=entailed, rng=Random(0), cap=10)
    assert A("subclass_of", "b", "a") in negs
    assert all(n not in entailed for n in negs)


def test_split_caps_eval_positives_and_guards_leakage():
    hierarchy, facts = _toy_facts()
    kb = build_kb(hierarchy, facts)
    tr_pos, tr_neg, te_pos, te_neg = runmod._split(
        kb, "random", 0, ent_cap=200, eval_pos=3
    )
    assert len(te_pos) <= 3
    assert not (set(te_pos) & set(tr_pos))
    assert all(n not in set(tr_pos) for n in te_neg)


def test_learnability_control_separates_a_predictable_label():
    hierarchy, facts = _toy_facts()
    kb = build_kb(hierarchy, facts)
    res = runmod._learnability_sanity(kb, 0, k=5, ent_cap=100, epochs=8, eval_pos=3)
    # the invented-predicate negatives are separable, so the learner must fit
    assert res["learned_recall"] >= 0.8
    assert res["learned_recall"] > res["chance"]
    assert res["untrained_recall"] <= res["chance"] * 3


def test_trust_invariant_blocks_a_lying_proposer():
    hierarchy, facts = _toy_facts()
    kb = build_kb(hierarchy, facts)
    every = closure(kb)
    _, support = runmod.derivations(kb)
    judge = runmod.SupportJudge(support)
    lie = A("subclass_of", "person", "physicist")  # reversed, not entailed
    assert lie not in every
    adv = runmod._adversarial_probe(kb, judge, every, [lie])
    assert adv["available"] and adv["verdict"] == "abstain"
    assert adv["false_assert"] is False


# -- end-to-end harness on a synthetic corpus (no network) -----------------
def _fake_extract(names, **kwargs):
    hierarchy, facts = _toy_facts()
    docs = [
        Doc(
            name="Curie",
            slug="curie",
            sentences=["Marie Curie was born in Warsaw.", "Curie was a physicist."],
            facts=[f for f in facts if f.subj == "curie"],
            labels={"warsaw": "Warsaw", "physicist": "physicist"},
        ),
        Doc(
            name="Paris",
            slug="paris",
            sentences=["Paris is the capital of France."],
            facts=[f for f in facts if f.subj == "paris"],
            labels={"city": "city", "france": "France"},
        ),
    ]
    return docs, hierarchy


def test_end_to_end_run_is_honest_and_zero_false_asserts(monkeypatch, tmp_path):
    monkeypatch.setattr(webmod, "extract", _fake_extract)
    weights_dir = tmp_path / "weights"
    args = argparse.Namespace(
        seeds=None, cache_dir=None, offline=True, subclass_depth=1, summary_chars=200,
        seed=0, k=5, negatives=100, eval_pos=3, epochs=8, max_sentences=2,
        clm_url=None, json=None, nl_epochs=10, nl_lr=0.2, nl_folds=2,
        save_weights=str(weights_dir),
    )
    report = runmod.run(args)
    assert report["stats"]["closure"] > 0
    trust = report["part_b_trust"]
    assert trust["false_assert"] == 0
    assert report["part_b_adversarial"]["false_assert"] is False
    assert report["stats"]["proposer_sanity"]["learned_recall"] >= 0.8
    assert any("Trust invariant" in line for line in report["verdict"])
    arms = {m["arm"] for m in report["part_c_language"]}
    assert {"surface", "learned", "learned_insample", "shuffled"} <= arms
    assert all(m["false_assert"] == 0 for m in report["part_c_language"])
    # the deployable reader and the per-fold CV models are persisted as JSON
    assert (weights_dir / "nl_reader.json").exists()
    assert (weights_dir / "nl_reader_fold0.json").exists()
    assert (weights_dir / "nl_shuffled_fold0.json").exists()
    assert report["stats"]["nl_weights_saved"].endswith("nl_reader.json")
    assert report["stats"]["nl_top_features"]