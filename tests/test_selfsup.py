"""Tests for module 10: DLM-native self-supervision (logic SSL, regime B)."""
from __future__ import annotations

from random import Random

import pytest

from dlm.convert import Ingestor
from dlm.engine import Retriever, closure, entails, prove
from dlm.kb import KnowledgeBase
from dlm.logic import Atom, Const, Literal, Rule, Schema, SchemaRegistry, Var
from dlm.reader import AGENT, PATIENT, LexicalReader
from dlm.selfsup import (
    Example,
    FeatureScorer,
    Pair,
    RejectionSelfTrainer,
    ScorerRetriever,
    closure_mask_examples,
    compose_rules,
    evaluate,
    features,
    flip_labels,
    minimal_pairs,
    proof_cost,
    proof_holes,
    recall_at_k,
    rule_composition_examples,
    rule_removal_examples,
    scramble_constants,
    soundness,
    ssl_l_examples,
    train,
)


def fact(pred, *names):
    return Atom(pred, tuple(Const(n) for n in names))


def theory() -> KnowledgeBase:
    kb = KnowledgeBase()
    for t in [("a", "b"), ("b", "c"), ("a", "d")]:
        kb.add_fact(fact("parent", *t))
    kb.add_rule(Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("x"), Var("y"))),)))
    kb.add_rule(
        Rule(
            Atom("ancestor", (Var("x"), Var("z"))),
            (Atom("parent", (Var("x"), Var("y"))), Atom("ancestor", (Var("y"), Var("z")))),
        )
    )
    kb.add_rule(
        Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("ancestor", (Var("x"), Var("y"))),))
    )
    return kb


# -- pretext 1: closure-mask -----------------------------------------------
def test_closure_mask_positives_and_negatives_are_kernel_labeled():
    kb = theory()
    examples = closure_mask_examples(kb, negatives=8, rng=Random(0))
    assert any(e.label is True for e in examples)
    assert any(e.label is False for e in examples)
    for e in examples:
        assert isinstance(e.target, Literal) and isinstance(e.label, bool)
        assert evaluate(kb, e.target) == e.label  # label is the kernel verdict
    assert soundness(examples, kb)


def test_closure_mask_leakage_guard_excludes_held_out():
    kb = theory()
    held = fact("ancestor", "a", "c")
    examples = closure_mask_examples(kb, negatives=10, exclude=[held])
    targets = {e.target.atom for e in examples}
    assert held not in targets


# -- pretext 2: minimal pairs ----------------------------------------------
def test_minimal_pairs_change_entailment():
    kb = theory()
    pairs = minimal_pairs(kb)
    assert pairs
    for p in pairs:
        assert isinstance(p, Pair)
        assert evaluate(kb, p.positive) is True
        assert evaluate(kb, p.negative) is False
    sign = minimal_pairs(kb, mode="sign")
    for p in sign:
        assert p.positive.negated is False and p.negative.negated is True


# -- pretext 3: rule-removal redundancy ------------------------------------
def test_rule_removal_detects_redundancy():
    kb = theory()
    examples = rule_removal_examples(kb)
    by_rule = {e.target: e for e in examples}
    identity = Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("ancestor", (Var("x"), Var("y"))),))
    transitive = next(r for r in kb.rules() if len(r.body) == 2)
    assert by_rule[identity].label is True  # removing it changes nothing
    assert by_rule[transitive].label is False  # removing it loses derivations
    assert by_rule[transitive].meta[0]  # non-empty closure delta


# -- pretext 4: rule composition -------------------------------------------
def test_rule_composition_is_sound():
    kb = theory()
    r1 = Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("x"), Var("y"))),))
    r2 = Rule(
        Atom("ancestor", (Var("x"), Var("z"))),
        (Atom("parent", (Var("x"), Var("y"))), Atom("ancestor", (Var("y"), Var("z")))),
    )
    composed = compose_rules(r1, r2)
    assert composed
    examples = rule_composition_examples(kb)
    assert examples and all(e.label is True for e in examples)


# -- pretext 5: proof holes ------------------------------------------------
def test_proof_holes_and_cost():
    kb = theory()
    holes = proof_holes(kb, atoms=[fact("ancestor", "a", "c")])
    assert holes and all(e.kind == "proof_hole" for e in holes)
    assert all(isinstance(e.label, Atom) for e in holes)
    assert proof_cost(prove(kb, fact("parent", "a", "b"))) == 1
    assert proof_cost(prove(kb, fact("ancestor", "a", "c"))) > 1


# -- the learned arm + evaluation -----------------------------------------
def _pool(kb):
    positives = sorted(closure(kb), key=str)
    negatives = [e.target.atom for e in closure_mask_examples(kb, negatives=None)]
    return sorted(set(positives) | set(negatives), key=str), positives


def test_features_include_structure_and_argument_identity():
    f = features(fact("ancestor", "a", "b"))
    assert "pred=ancestor" in f and "arity=2" in f and "arg0=a" in f and "arg1=b" in f


def test_training_improves_recall_and_beats_controls():
    kb = theory()
    pool, truths = _pool(kb)
    k = len(truths)

    trained = train(FeatureScorer(lr=0.2), closure_mask_examples(kb, negatives=None), kb=kb, epochs=5)
    assert trained.updates > 0
    recall = recall_at_k(ScorerRetriever(trained), kb, pool, truths, k)
    assert recall == 1.0

    # surface-SSL control: inverted labels teach the wrong ordering
    wrong = train(FeatureScorer(lr=0.2), flip_labels(closure_mask_examples(kb, negatives=None)), kb=kb, epochs=5)
    recall_wrong = recall_at_k(ScorerRetriever(wrong), kb, pool, truths, k)
    assert recall_wrong < recall

    # shuffled-KB control: entity-level priors do not transfer
    scrambled = scramble_constants(kb, rng=Random(1))
    pool2, truths2 = _pool(scrambled)
    recall_scrambled = recall_at_k(ScorerRetriever(trained), scrambled, pool2, truths2, len(truths2))
    assert recall_scrambled <= recall


def test_soundness_catches_a_broken_label():
    kb = theory()
    good = closure_mask_examples(kb, negatives=4)
    assert soundness(good, kb)
    assert not soundness(flip_labels(good), kb)


def test_scorer_retriever_is_a_retriever():
    assert isinstance(ScorerRetriever(FeatureScorer()), Retriever)


# -- the two ledgers -------------------------------------------------------
def test_ssl_l_examples_are_logic_only():
    kb = theory()
    examples = ssl_l_examples(kb, held_out=[fact("ancestor", "a", "c")])
    assert examples
    for e in examples:
        assert isinstance(e.target, (Atom, Literal, Rule))  # never a sentence
    assert soundness(examples, kb)


def test_rejection_self_trainer_accepts_only_provable_pairs():
    kb = KnowledgeBase().add_fact(fact("calls", "alice", "bob"))
    registry = SchemaRegistry([Schema("calls", (AGENT, PATIENT))])
    ingestor = Ingestor(LexicalReader(predicates={"calls"}), registry)
    trainer = RejectionSelfTrainer(ingestor, kb)

    assert trainer.offer("Alice calls Bob") == Literal(fact("calls", "alice", "bob"))
    assert trainer.offer("Bob calls Alice") is None  # not provable -> rejected
    assert trainer.offer("Alice flies") is None  # not normalizable -> rejected
    assert len(trainer.accepted) == 1 and len(trainer.rejected) == 2