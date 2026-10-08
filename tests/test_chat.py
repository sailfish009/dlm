"""Tests for the interactive dialogue driver (dlm/chat.py, v0.0003)."""
from __future__ import annotations

import dlm.chat as chat


def test_build_session_has_starter_domain():
    s = chat.build_session()
    assert s.kb.num_facts == 3 and s.kb.num_rules == 3


def test_handle_query_and_assert():
    s = chat.build_session()
    yes = chat.handle(s, "is alice an ancestor of dave")
    assert yes is not None and yes.startswith("DLM: yes") and "grammar:" in yes
    noted = chat.handle(s, "erin is a parent of frank")
    assert noted is not None and "noted parent(erin, frank)" in noted
    assert s.kb.num_facts == 4


def test_handle_abstains_on_out_of_domain():
    s = chat.build_session()
    out = chat.handle(s, "who likes cake")
    assert out is not None and "abstain" in out.lower()


def test_handle_commands_and_quit():
    s = chat.build_session()
    assert chat.handle(s, ":quit") is None
    assert "facts=" in (chat.handle(s, ":kb") or "")
    assert "parent(alice, bob)" in (chat.handle(s, ":facts") or "")
    assert "anc_step" in (chat.handle(s, ":rules") or "")
    assert (chat.handle(s, ":user") or "").strip() == "(none)"
    assert "unknown command" in (chat.handle(s, ":nope") or "")
    assert "empty input" in (chat.handle(s, "  ") or "")


def test_user_facts_are_listed_after_assertion():
    s = chat.build_session()
    chat.handle(s, "erin is a parent of frank")
    assert "parent(erin, frank)" in (chat.handle(s, ":user") or "")


def test_banner_promises_no_generation():
    assert "no generation" in chat.banner().lower()