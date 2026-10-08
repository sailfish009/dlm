"""Tests for the grounded dialogue loop (dlm/dialogue.py, v0.0003)."""
from __future__ import annotations

import pytest

from dlm import DialogueSession, GrammarGrounder, KnowledgeBase, Pattern, fact, rule
from dlm.dialogue import ABSTAIN, ANSWER, ASSERT, REJECT
from dlm.grounder_learn import CharNgramGrounder, synthesize_pairs
from dlm.grounding import ChainGrounder, Grounding
from dlm.terms import Var

QUERY_PATTERNS = [
    Pattern("is {x} a parent of {y}", "parent({x},{y})"),
    Pattern("{x} is a parent of {y}", "parent({x},{y})"),
    Pattern("is {x} a grandparent of {y}", "grandparent({x},{y})"),
    Pattern("is {x} an ancestor of {y}", "ancestor({x},{y})"),
]
ASSERT_PATTERNS = [
    Pattern("{x} is a parent of {y}", "parent({x},{y})", kind="assert"),
]
ENTITIES = ("alice", "bob", "carol", "dave")


def build_kb() -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in [("alice", "bob"), ("bob", "carol"), ("carol", "dave")]:
        kb.add_fact(fact("parent", a, b))
    x, y, z = Var("x"), Var("y"), Var("z")
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, y), name="anc_base"))
    kb.add_rule(rule(fact("ancestor", x, y), fact("parent", x, z),
                     fact("ancestor", z, y), name="anc_step"))
    kb.add_rule(rule(fact("grandparent", x, y), fact("parent", x, z),
                     fact("parent", z, y), name="gp"))
    return kb


def session() -> DialogueSession:
    # assert patterns first: "X is P" is a statement, "is X P" is a question.
    # Negation is handled by the grounder stripping "not", not by a pattern,
    # so the same assert pattern also covers "X is not P".
    grounder = GrammarGrounder(ASSERT_PATTERNS + QUERY_PATTERNS)
    return DialogueSession(build_kb(), grounder)


# -- queries ---------------------------------------------------------------
def test_direct_fact_answers_yes_with_proof():
    r = session().say("Is alice a parent of bob?")
    assert r.kind == ANSWER and r.derivable is True and bool(r)
    assert r.text.startswith("yes")
    assert r.proof is not None and r.proof.depth() == 1
    assert "parent(alice, bob)" in r.text


def test_derived_fact_answers_yes_with_multi_step_proof():
    r = session().say("Is alice an ancestor of dave?")
    assert r.derivable is True
    assert r.proof is not None and r.proof.depth() >= 3
    assert "anc_step" in r.text


def test_false_query_answers_no_without_proof():
    r = session().say("Is dave an ancestor of alice?")
    assert r.kind == ANSWER and r.derivable is False and bool(r)
    assert r.text == "no"


def test_negated_query_on_underivable_atom_is_yes():
    r = session().say("Is dave a grandparent of alice?")
    assert r.derivable is False
    # closed-world negation path via the engine
    r2 = session().say("is not bob a parent of carol?")
    assert r2.kind == ANSWER and r2.derivable is False


# -- assertions / learning -------------------------------------------------
def test_assert_grows_kb_and_is_then_usable():
    s = session()
    before = s.kb.num_facts
    r = s.say("dave is a parent of erin")
    assert r.kind == ASSERT and r.added is True
    assert s.kb.num_facts == before + 1
    assert "dave" in str(r.grounding.atom)
    # the new fact now participates in deduction
    assert s.say("Is carol an ancestor of erin?").derivable is True


def test_assert_is_idempotent():
    s = session()
    s.say("alice is a parent of bob")
    r = s.say("alice is a parent of bob")
    assert r.kind == ASSERT and r.added is False
    assert "already known" in r.text


def test_assert_marks_user_provenance():
    s = session()
    r = s.say("dave is a parent of erin")
    assert r.provenance == "user"
    assert "parent(dave, erin)" in s.user_facts
    # a query proven only through the user fact is labelled 'user'
    q = s.say("Is carol an ancestor of erin?")
    assert q.provenance == "user"


def test_negated_assert_consistent_when_not_derivable():
    s = session()
    before = s.kb.num_facts
    r = s.say("alice is not a parent of dave")
    assert r.kind == ASSERT and r.added is False
    assert "consistent" in r.text
    assert s.kb.num_facts == before


def test_negated_assert_rejected_on_contradiction():
    s = session()
    r = s.say("alice is not a parent of bob")
    assert r.kind == REJECT and not bool(r)
    assert "contradiction" in r.text


# -- abstention ------------------------------------------------------------
def test_ungrounded_utterance_abstains_and_never_guesses():
    r = session().say("does berlin like cake")
    assert r.kind == ABSTAIN and not bool(r)
    assert r.grounding is not None and r.grounding.ok is False
    assert r.derivable is None and r.proof is None


def test_empty_and_noise_inputs_abstain():
    s = session()
    assert s.say("").kind == ABSTAIN
    assert s.say("???").kind == ABSTAIN


def test_non_ground_atom_is_rejected_not_asserted():
    class VarGrounder:
        def ground(self, sentence: str) -> Grounding:
            from dlm.interpreter import parse_atom
            return Grounding(True, parse_atom("parent(?x,bob)"), kind="assert")

    s = DialogueSession(build_kb(), VarGrounder())
    before = s.kb.num_facts
    r = s.say("anyone is related to bob")
    assert r.kind == ABSTAIN and s.kb.num_facts == before


# -- chain / plug-in composition -------------------------------------------
def test_chain_grounder_falls_back_to_lexical_t2():
    train = synthesize_pairs(ASSERT_PATTERNS + QUERY_PATTERNS, ENTITIES, seed=0)
    chain = ChainGrounder([GrammarGrounder(ASSERT_PATTERNS + QUERY_PATTERNS), CharNgramGrounder(train)])
    s = DialogueSession(build_kb(), chain)
    r = s.say("Is alice the mother of bob?")   # unseen phrasing -> T2
    assert r.grounding is not None and r.grounding.source.startswith("char_ngram")


def test_crashing_plugin_does_not_break_the_loop():
    class Boom:
        def ground(self, sentence: str) -> Grounding:
            raise RuntimeError("plugin exploded")

    s = DialogueSession(build_kb(), ChainGrounder([Boom(), GrammarGrounder(QUERY_PATTERNS)]))
    r = s.say("Is alice a parent of bob?")
    assert r.kind == ANSWER and r.derivable is True


# -- bookkeeping -----------------------------------------------------------
def test_ask_and_tell_force_intent_on_ambiguous_phrase():
    """The same surface form can be a question or a statement; ask/tell decide."""
    s = session()
    assert s.ask("alice is a parent of bob").kind == ANSWER
    s2 = session()
    r = s2.tell("carol is a parent of erin")
    assert r.kind == ASSERT and r.added is True
    assert s2.ask("alice is a parent of bob").derivable is True


def test_history_and_transcript():
    s = session()
    s.say("Is alice a parent of bob?")
    s.say("dave is a parent of erin")
    s.say("who likes cake")
    assert len(s.history) == 3
    text = s.transcript()
    assert text.count("user>") == 3 and text.count("DLM:") == 3


def test_reply_text_is_template_only_not_generated():
    """The dynamic part of a 'yes' reply is exactly the proof rendering."""
    s = session()
    r = s.say("Is alice an ancestor of dave?")
    assert r.proof is not None
    assert r.text == f"yes — {s.verbalizer.render_proof(r.proof)}"