"""Tests for the matched-arm dialogue evaluation (v0.0003, W4)."""
from __future__ import annotations

import run_dialogue_eval as rde
from dlm.dialogue import ABSTAIN


def test_arms_produce_expected_metric_keys():
    for arm in ("t1_only", "chain"):
        res = rde.run_arm(arm)
        m = res["metrics"]
        for key in ("coverage", "abstention_rate", "exact_atom_accuracy",
                    "verdict_accuracy", "confident_wrong", "by_phrasing"):
            assert key in m, key
        assert len(res["turns"]) == len(rde.SCRIPT)


def test_out_of_domain_abstains_in_every_arm():
    for arm in ("t1_only", "chain"):
        rows = rde.run_arm(arm)["turns"]
        ood = [r for r in rows if r["phrasing"] == "out_of_domain"]
        assert ood and all(r["kind"] == ABSTAIN for r in ood)


def test_t1_abstains_on_all_unseen_phrasing():
    rows = rde.run_arm("t1_only")["turns"]
    unseen = [r for r in rows if r["phrasing"] == "unseen"]
    assert unseen and all(not r["grounded"] for r in unseen)


def test_lexical_fallback_adds_coverage_without_confident_wrong():
    t1 = rde.run_arm("t1_only")["metrics"]
    chain = rde.run_arm("chain")["metrics"]
    assert chain["coverage"] > t1["coverage"]
    assert chain["confident_wrong"] == 0
    assert chain["verdict_accuracy"] >= t1["verdict_accuracy"]


def test_grounded_verdicts_are_correct_in_this_script():
    """When a verdict is produced at all, it matched the gold label."""
    for arm in ("t1_only", "chain"):
        assert rde.run_arm(arm)["metrics"]["verdict_accuracy_when_grounded"] == 1.0


def test_judge_is_deterministic():
    arms = {a: rde.run_arm(a) for a in ("t1_only", "chain")}
    assert rde.judge(arms) == rde.judge(arms) == "fallback_helps"


def test_every_ask_turn_has_a_gold_atom():
    for utterance, intent, gold_atom, _, phrasing in rde.SCRIPT:
        if intent == "ask" and phrasing != "out_of_domain":
            assert gold_atom is not None, utterance