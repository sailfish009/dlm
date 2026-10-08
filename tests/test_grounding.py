"""Tests for the deterministic grounding front-end (v0.0003, T1)."""
from __future__ import annotations

import pytest

from dlm import ChainGrounder, GrammarGrounder, Grounding, Pattern


def build() -> GrammarGrounder:
    return GrammarGrounder([
        Pattern("is {x} a grandparent of {y}", "grandparent({x},{y})", name="gp"),
        Pattern("is {x} a parent of {y}", "parent({x},{y})", name="parent"),
        Pattern("is {x} an ancestor of {y}", "ancestor({x},{y})", name="anc"),
        Pattern("{x} is a parent of {y}", "parent({x},{y})", kind="assert", name="tell"),
    ])


def test_query_grounding():
    g = build().ground("Is Alice a grandparent of Carol?")
    assert g.ok and not g.negated
    assert g.kind == "query"
    assert str(g.atom) == "grandparent(alice, carol)"


def test_assert_grounding():
    g = build().ground("alice is a parent of dave")
    assert g.ok and g.kind == "assert"
    assert str(g.atom) == "parent(alice, dave)"


def test_negation_is_recorded_not_ignored():
    g = build().ground("is dave not an ancestor of alice")
    assert g.ok and g.negated
    assert str(g.atom) == "ancestor(dave, alice)"


def test_abstains_out_of_domain():
    g = build().ground("Is Berlin the capital of Germany?")
    assert not g.ok and g.atom is None
    assert "no pattern" in g.reason


def test_abstains_on_empty():
    assert not build().ground("   ").ok


def test_case_and_punctuation_normalization():
    a = build().ground("IS ALICE A GRANDPARENT OF CAROL")
    b = build().ground("is alice a grandparent of carol.")
    assert a.ok and b.ok and str(a.atom) == str(b.atom)


def test_first_matching_pattern_wins_deterministically():
    g = GrammarGrounder([
        Pattern("is {x} a parent of {y}", "parent({x},{y})", name="first"),
        Pattern("is {x} a parent of {y}", "guardian({x},{y})", name="second"),
    ])
    out = g.ground("is a b")  # any match uses the same regex shape
    # specific check with real words
    out2 = g.ground("is alice a parent of bob")
    assert out2.ok and out2.source.endswith("first")
    assert str(out2.atom) == "parent(alice, bob)"


def test_bad_template_abstains_instead_of_crashing():
    g = GrammarGrounder([Pattern("hello {x}", "not an atom(")])
    out = g.ground("hello world")
    assert not out.ok


def test_chain_grounder_falls_through_to_second():
    primary = GrammarGrounder([Pattern("is {x} a king of {y}", "king({x},{y})")])
    backup = build()
    chain = ChainGrounder([primary, backup])
    assert chain.ground("is alice a grandparent of carol").ok
    assert not chain.ground("who likes cake?").ok


def test_chain_grounder_survives_a_crashing_plugin():
    class Boom:
        def ground(self, sentence: str) -> Grounding:
            raise RuntimeError("plugin failure")

    chain = ChainGrounder([Boom(), build()])
    out = chain.ground("is alice a parent of bob")
    assert out.ok and str(out.atom) == "parent(alice, bob)"


def test_abstain_rate_on_a_fixed_out_of_domain_set():
    """Grounding correctness is Tier 2 only if measured; here: honest abstention."""
    g = build()
    ood = [
        "what is the weather today",
        "who likes cake",
        "Berlin is the capital of Germany",
        "tell me a joke",
    ]
    abstained = sum(1 for s in ood if not g.ground(s).ok)
    assert abstained == len(ood)  # never guesses outside the closed vocabulary