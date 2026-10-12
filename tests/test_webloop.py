"""Tests for the random-web dual-ability self-supervision harness (v0.0022).

Runs entirely on a small synthetic hierarchy -- no network, no cache, no torch.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

from experiments.webloop import run as W


@dataclass(frozen=True)
class F:
    pred: str
    subj: str
    obj: str


def _hierarchy() -> list:
    # layered graph (every node in a layer links to every node in the next):
    # node hold-out still leaves many 2-paths, so transitivity is learnable.
    layers = [[f"l{j}" for j in range(6)], [f"m{j}" for j in range(5)], [f"t{j}" for j in range(4)]]
    out = []
    for a_layer, b_layer in zip(layers, layers[1:]):
        for a in a_layer:
            for b in b_layer:
                out.append(F("subclass_of", a, b))
    return out


def _args(**over) -> argparse.Namespace:
    base = dict(
        seed=0, deduce_folds=2, deduce_edges=40, deduce_positives=120,
        budget=20000, no_scramble=False,
    )
    base.update(over)
    return argparse.Namespace(**base)


# -- helpers ---------------------------------------------------------------
def test_bfs_edges_respects_cap_and_keeps_chains():
    adj = {"n0": {"n1"}, "n1": {"n2"}, "n2": {"n3"}, "n3": set()}
    edges = W._bfs_edges(adj, ["n0"], 10)
    assert edges == [("n0", "n1"), ("n1", "n2"), ("n2", "n3")]
    capped = W._bfs_edges(adj, ["n0"], 2)
    assert len(capped) == 2


def test_node_folds_partition_deterministically():
    nodes = [f"n{i}" for i in range(10)]
    a = W._node_folds(nodes, 3, seed=1)
    b = W._node_folds(nodes, 3, seed=1)
    assert a == b
    flat = sorted(x for g in a for x in g)
    assert flat == sorted(nodes)


def test_requested_parts_selection():
    import pytest

    assert W._requested_parts("all") == ["deduction", "conversation", "probes"]
    assert W._requested_parts("deduction") == ["deduction"]
    assert W._requested_parts("conversation") == ["conversation"]
    assert W._requested_parts("conversation,probes") == ["conversation", "probes"]
    with pytest.raises(SystemExit):
        W._requested_parts("bogus")


def test_rename_predicates_invents_a_learnable_map():
    frame = W.Frame(("born",), ("probe",), ("probe",), 0)
    from dlm import Atom, Const

    ex = [("doc", frame, (Atom("birthplace", (Const("x"), Const("y"))),),
           (Atom("birthplace", (Const("x"), Const("y"))), Atom("occupation", (Const("x"), Const("y")))))]
    out = W._rename_predicates(ex, "inv_")
    _s, f2, pos, cand = out[0]
    assert pos[0].pred == "inv_birthplace"
    assert {a.pred for a in cand} == {"inv_birthplace", "inv_occupation"}


# -- the deduction ability (the heart of the harness) ----------------------
def test_deduction_induces_transitivity_and_generalises():
    out = W.deduction_part(_hierarchy(), _args())
    assert out["found_transitivity"] is True
    arms = out["arms"]
    assert arms["oracle"]["recovery"] == 1.0
    # the law is induced from kernel labels and generalises to held-out nodes
    assert arms["learned"]["recovery"] > arms["identity"]["recovery"]
    assert arms["learned"]["recovery"] > arms["scrambled"]["recovery"]
    # the learned rules never fabricate a false derivation (kernel-gated truth)
    assert arms["learned"]["false"] == 0
    assert any("subclass_of ?G0 ?E0" in r for r in out["invented_rules"])


def test_deduction_is_deterministic():
    a = W.deduction_part(_hierarchy(), _args())
    b = W.deduction_part(_hierarchy(), _args())
    # induce_seconds is wall-clock; everything else must be identical
    assert a.pop("induce_seconds") is not None and b.pop("induce_seconds") is not None
    assert a == b


def test_scrambled_labels_do_not_induce_the_law():
    strict = W.deduction_part(_hierarchy(), _args(deduce_folds=1))
    # with the true labels the law is found; the shuffled control must not
    # achieve the same held-out recovery
    assert strict["arms"]["learned"]["recovery"] >= strict["arms"]["scrambled"]["recovery"]