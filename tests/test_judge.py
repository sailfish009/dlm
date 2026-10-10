"""Tests for seam D: the judgment protocol (module 8)."""
from __future__ import annotations

import pytest

from dlm.judge import (
    Adjudicator,
    Judgement,
    Judge,
    KbProposer,
    Policy,
    ProofJudge,
    Proposal,
    Proposer,
    StaticProposer,
    Verdict,
)
from dlm.kb import KnowledgeBase
from dlm.logic import Atom, Const, Literal, Rule, Var
from dlm.reader import AGENT, PATIENT


def fixture_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    kb.add_fact(Atom("parent", (Const("a"), Const("b"))))
    kb.add_fact(Atom("parent", (Const("b"), Const("c"))))
    kb.add_rule(
        Rule(Atom("ancestor", (Var("x"), Var("y"))), (Atom("parent", (Var("x"), Var("y"))),))
    )
    kb.add_rule(
        Rule(
            Atom("ancestor", (Var("x"), Var("y"))),
            (Atom("parent", (Var("x"), Var("z"))), Atom("ancestor", (Var("z"), Var("y")))),
        )
    )
    kb.add_negation(Atom("flies", (Const("alice"),)))
    return kb


def lit(pred: str, *args: str, negated: bool = False) -> Literal:
    return Literal(Atom(pred, tuple(Const(a) for a in args)), negated)


# -- ProofJudge ------------------------------------------------------------
def test_judge_asserts_fact_with_verified_proof():
    kb = fixture_kb()
    j = ProofJudge().judge(kb, lit("parent", "a", "b"))
    assert j.asserted and j.decided and not j.refuted
    assert j.proof is not None and j.proof.is_fact
    assert j.confidence == 1.0


def test_judge_asserts_through_a_rule_and_attaches_proof():
    kb = fixture_kb()
    j = ProofJudge().judge(kb, lit("ancestor", "a", "c"))
    assert j.asserted
    assert j.proof is not None and j.proof.rule is not None


def test_judge_abstains_on_unknown_positive():
    kb = fixture_kb()
    j = ProofJudge().judge(kb, lit("ancestor", "c", "a"))
    assert j.verdict is Verdict.ABSTAIN and j.proof is None


def test_judge_abstains_on_non_ground_literal():
    kb = fixture_kb()
    j = ProofJudge().judge(kb, Literal(Atom("ancestor", (Var("x"), Const("b")))))
    assert j.verdict is Verdict.ABSTAIN


def test_judge_refutes_only_by_explicit_side_table():
    kb = fixture_kb()
    assert ProofJudge().judge(kb, lit("flies", "alice", negated=True)).refuted
    # absence is NOT refutation
    assert ProofJudge().judge(kb, lit("swims", "alice", negated=True)).verdict is Verdict.ABSTAIN


# -- protocols -------------------------------------------------------------
def test_protocol_conformance():
    assert isinstance(ProofJudge(), Judge)
    assert isinstance(StaticProposer([]), Proposer)
    assert isinstance(KbProposer(), Proposer)


# -- the trust invariant ---------------------------------------------------
def test_malicious_proposer_cannot_make_the_system_assert():
    kb = fixture_kb()
    lie = Proposal(lit("steals", "alice"), score=1.0, source="evil")
    adj = Adjudicator()
    # with an explicit query
    j = adj.decide(kb, query=lie.literal, proposals=[lie])
    assert j.verdict is Verdict.ABSTAIN and not j.asserted
    assert j.score == 1.0 and j.proposed_by == "evil"  # score kept, verdict untouched
    # proposer also cannot flip a refuted statement to asserted
    neg = Proposal(lit("flies", "alice", negated=True), score=1.0, source="evil")
    assert adj.decide(kb, query=neg.literal, proposals=[neg]).refuted


def test_score_never_becomes_a_verdict():
    j = Judgement(lit("steals", "alice"), Verdict.ABSTAIN, score=0.99)
    assert not j.asserted and not j.decided


# -- policies --------------------------------------------------------------
def test_gate_drops_learned_confidence_on_abstain():
    kb = fixture_kb()
    lie = Proposal(lit("steals", "alice"), score=0.9, source="p")
    j = Adjudicator(policy=Policy.GATE).decide(kb, query=lie.literal, proposals=[lie])
    assert j.verdict is Verdict.ABSTAIN and j.confidence is None


def test_two_axis_keeps_learned_score_as_display_confidence():
    kb = fixture_kb()
    lie = Proposal(lit("steals", "alice"), score=0.9, source="p")
    j = Adjudicator(policy=Policy.TWO_AXIS).decide(kb, query=lie.literal, proposals=[lie])
    assert j.verdict is Verdict.ABSTAIN and j.confidence == 0.9


def test_decided_verdict_keeps_proof_confidence_not_proposer_score():
    kb = fixture_kb()
    p = Proposal(lit("ancestor", "a", "c"), score=0.2, source="p")
    j = Adjudicator(policy=Policy.TWO_AXIS).decide(kb, query=p.literal, proposals=[p])
    assert j.asserted and j.confidence == 1.0 and j.score == 0.2


# -- decide without a query ------------------------------------------------
def test_decide_without_query_picks_top_scored_decided_candidate():
    kb = fixture_kb()
    proposals = [
        Proposal(lit("ancestor", "c", "a"), score=0.99),  # not entailed
        Proposal(lit("ancestor", "a", "c"), score=0.10),  # entailed
    ]
    j = Adjudicator().decide(kb, proposals=proposals)
    assert j.asserted and j.literal == lit("ancestor", "a", "c")


def test_decide_without_query_abstains_when_nothing_is_provable():
    kb = fixture_kb()
    proposals = [
        Proposal(lit("ancestor", "c", "a"), score=0.9),
        Proposal(lit("ancestor", "c", "b"), score=0.5),
    ]
    j = Adjudicator().decide(kb, proposals=proposals)
    assert j.verdict is Verdict.ABSTAIN and j.literal == lit("ancestor", "c", "a")


def test_decide_requires_a_query_or_proposals():
    with pytest.raises(ValueError):
        Adjudicator().decide(fixture_kb())


# -- KbProposer ------------------------------------------------------------
def test_kb_proposer_is_deterministic_and_limitable():
    kb = fixture_kb()
    all_p = KbProposer().propose(kb)
    assert [p.literal.atom for p in all_p] == sorted(kb.facts(), key=str)
    assert len(KbProposer(limit=1).propose(kb)) == 1
    assert all(p.literal.negated is False for p in all_p)
    assert all(p.literal.negated for p in KbProposer(negated=True).propose(kb))


def test_end_to_end_ingest_then_adjudicate():
    from dlm.convert import Ingestor
    from dlm.logic import Schema, SchemaRegistry
    from dlm.reader import LexicalReader

    reg = SchemaRegistry([Schema("calls", (AGENT, PATIENT))])
    ing = Ingestor(LexicalReader(predicates={"calls"}), reg)
    kb = KnowledgeBase().add_facts(
        tuple(l.atom for l in ing.literals("Alice calls Bob"))
    )
    query = ing.literal("Alice calls Bob")
    assert Adjudicator().decide(kb, query=query).asserted
    assert Adjudicator().decide(kb, query=ing.literal("Bob calls Alice")).verdict is Verdict.ABSTAIN