"""Tests for dlm.compose -- L5 composition, L6 motifs, transfer."""
from __future__ import annotations

from dlm import Atom, Const
from dlm.compose import (
    Pattern,
    induce_patterns,
    is_connected,
    motifs,
    pattern_candidates,
    pattern_extension,
    transfer_patterns,
)


def A(pred, *args):
    return Atom(pred, tuple(Const(a) for a in args))


DELEG = Pattern((("calls", ("X", "Y")), ("calls", ("Y", "Z"))))
TWO_FACTS = Pattern((("calls", ("X", "Y")), ("calls", ("X", "Z"))))


def test_pattern_extension_is_a_conjunctive_query():
    f = {A("calls", "a", "b"), A("calls", "b", "c"), A("defines", "m", "a")}
    assert pattern_extension(DELEG, f) == ("a",)
    assert pattern_extension(Pattern((("calls", ("X", "Y")),)), f) == ("a", "b")


def test_is_connected_distinguishes_composition_from_two_facts():
    assert is_connected(DELEG)              # Y shared by both literals
    assert not is_connected(TWO_FACTS)      # only the head X is shared


def test_pattern_candidates_allows_auxiliary_literals_and_requires_connection():
    cands = pattern_candidates(max_body=2)
    assert DELEG in cands                   # calls(Y,Z) does not mention X
    assert not any(len(p.body) < 2 for p in cands)
    for p in cands:
        counts: dict = {}
        for _pred, args in p.body:
            for v in set(args):
                counts[v] = counts.get(v, 0) + 1
        assert any(c >= 2 for c in counts.values())


def test_induce_finds_delegation_and_rejects_single_relation():
    corpus = {
        "a": {A("calls", "main", "train"), A("calls", "train", "zg"), A("calls", "train", "st")},
        "b": {A("calls", "main", "train"), A("calls", "train", "zg")},
        "c": {A("calls", "main", "test"), A("calls", "test", "x")},
    }
    got = induce_patterns(corpus, min_support=3, max_body=2, max_patterns=6)
    assert DELEG in got
    # a pure single-relation description is never invented as a concept
    assert not any(len(p.body) < 2 for p in got)


def test_motifs_find_recurring_ordered_subsequence():
    pipes = {"a": ["conv", "relu", "linear"], "b": ["conv", "relu", "dropout"]}
    got = motifs(pipes, min_len=2, max_len=3, min_support=2, top=5)
    ops = [tuple(m["ops"]) for m in got]
    assert ("conv", "relu") in ops


def test_transfer_reports_hits_on_held_out_programs():
    pats = [DELEG]
    facts = {"held": {A("calls", "main", "train"), A("calls", "train", "zg")}}
    tr = transfer_patterns(pats, facts)
    assert tr["pattern0"]["hits"]["held"] == ["main"]


def test_induce_is_deterministic():
    corpus = {
        "a": {A("calls", "main", "train"), A("calls", "train", "zg")},
        "b": {A("calls", "main", "train"), A("calls", "train", "st")},
        "c": {A("calls", "main", "test"), A("calls", "test", "x")},
    }
    r1 = [p.literals() for p in induce_patterns(corpus, min_support=2, max_body=2, max_patterns=4)]
    r2 = [p.literals() for p in induce_patterns(corpus, min_support=2, max_body=2, max_patterns=4)]
    assert r1 == r2