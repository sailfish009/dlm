"""Network-free test of the v0.0038 web experiment (synthetic hierarchy)."""
import argparse

from experiments.web.run import run


def _args(**over):
    base = dict(docs=40, seed=3, offline=True, synthetic=True,
                cache="/tmp/dlm_web_test_cache", train_frac=0.7, max_edges=200,
                max_neg=2000, subclass_depth=1, pause=0.0, retries=0, json="")
    base.update(over)
    return argparse.Namespace(**base)


def test_synthetic_learns_transitivity_and_beats_identity():
    out = run(_args())
    assert out["verdict"]["found_transitivity"]
    assert out["verdict"]["learned_sound"]
    assert out["arms"]["learned"]["held_recovery"] > out["arms"]["identity"]["held_recovery"] + 0.1


def test_synthetic_is_deterministic():
    a = run(_args())
    b = run(_args())
    a.pop("induce_seconds", None)
    b.pop("induce_seconds", None)
    assert a == b