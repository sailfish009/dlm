"""Network-free tests of the accumulating-learner train experiment."""
import copy

from experiments.train.accumulate import checkpoint_probe, retraction_probe, run


class _Args:
    seed = 1
    n_train = 8
    n_test = 6
    chains = 1
    chain_len = 3
    rounds = 2
    max_body = 2
    extra_vars = 1
    max_rules = 4
    max_neg = 80
    no_compress = False
    json = ""


def _strip(out):
    """Drop the wall-clock field (the only non-deterministic one)."""
    out = copy.deepcopy(out)
    for arm in out["arms"].values():
        arm.pop("seconds", None)
    return out


def test_retraction_probe_guarantees_a_drop():
    p = retraction_probe()
    assert p["admitted"] == 1
    assert p["retracted"] == 1
    assert p["final_rules"] == 0
    assert p["false_final"] == 0
    assert p["abstains"]


def test_checkpoint_probe_matches_uninterrupted():
    p = checkpoint_probe(3)
    assert p["same_rules"] and p["same_false"]
    assert p["rounds"] == 2


def test_run_verdicts_and_determinism():
    out = run(_Args())
    assert all(out["verdict"].values()), out["verdict"]
    assert _strip(out) == _strip(run(_Args()))