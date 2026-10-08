"""Tests for the matched-arm grounding evaluation helpers (v0.0003, L4)."""
from __future__ import annotations

import run_grounding_eval as rge
from dlm.grounding import Grounding
from dlm.interpreter import parse_atom


def _g(atom: str, ok: bool = True) -> Grounding:
    return Grounding(ok=ok, atom=parse_atom(atom) if ok else None)


def test_family_templates_are_valid_atoms():
    for rel, spec in rge.FAMILY.items():
        for split in ("train", "val", "test"):
            for ph in spec[split]:
                for p in rge.patterns(rel, split):
                    pass
        assert spec["template"].startswith(rel)
    pats = rge.all_patterns("test")
    assert len(pats) == sum(len(s["test"]) for s in rge.FAMILY.values())


def test_test_atoms_are_all_in_the_train_candidate_set():
    train_atoms = {rge.canon(a) for _, a in rge.pairs_for("train")}
    test_atoms = {rge.canon(a) for _, a in rge.pairs_for("test")}
    assert test_atoms and test_atoms <= train_atoms


def test_phrase_label_masks_entities():
    assert rge.phrase_label("is alice a parent of bob?") == "is {e} a parent of {e}?"


def test_metrics_counts_coverage_and_accuracy():
    pairs = [("s1", "parent(alice,bob)"), ("s2", "parent(bob,carol)")]
    grounds = [_g("parent(alice, bob)"), _g("x", ok=False)]
    m = rge.metrics(grounds, pairs)
    assert m["coverage"] == 0.5
    assert m["exact_accuracy"] == 0.5
    assert m["exact_when_covered"] == 1.0
    assert m["relation_when_covered"] == 1.0
    assert m["abstention_rate"] == 0.5


def test_tune_threshold_prefers_exact_then_coverage():
    pairs = [("s1", "parent(alice,bob)"), ("s2", "parent(bob,carol)")]

    def score(sentences, th):
        # only "s1" is above 0.6; both above 0.0
        return [_g("parent(alice,bob)"), _g("parent(alice,bob)")] if th <= 0.0 else [
            _g("parent(alice,bob)"), _g("x", ok=False)]

    th, m = rge.tune_threshold(score, pairs)
    assert th == 0.0  # covering both yields the second exact hit
    assert m["exact_accuracy"] == 0.5


def test_per_phrase_groups_by_surface_shape():
    pairs = [("is alice a parent of bob?", "parent(alice,bob)"),
             ("is carol a parent of dave?", "parent(carol,dave)"),
             ("is alice an ancestor of bob?", "ancestor(alice,bob)")]
    grounds = [_g("parent(alice,bob)"), _g("parent(carol,dave)"), _g("ancestor(alice,bob)")]
    out = rge.per_phrase(grounds, pairs)
    assert set(out) == {"is {e} a parent of {e}?", "is {e} an ancestor of {e}?"}
    assert out["is {e} a parent of {e}?"]["exact_accuracy"] == 1.0