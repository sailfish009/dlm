"""Network-free tests of the v0.0038 stream (multi-round accumulation) experiment."""
import argparse

from dlm.lisp import Env, eval_sexp, macroexpand
from experiments.stream.run import (
    DOMAIN_SOURCE, domain_forms, run, true_rules, TRANSITIVE, INVERSE,
)


def _args(**over):
    base = dict(web=False, seed=1, n_train=12, n_test=10, chains=2, chain_len=4,
                max_rules=8, max_neg=8000, test_frac=0.3, docs=1,
                cache="/tmp/dlm_stream_test_cache", offline=True, subclass_depth=1,
                pause=0.0, retries=0, json="")
    base.update(over)
    return argparse.Namespace(**base)


def test_rounds_accumulate_and_increase_on_unseen_entities():
    out = run(_args())
    assert out["verdict"]["multi_round"]
    assert out["verdict"]["all_laws_found"]
    assert out["verdict"]["sound_every_round"]
    assert out["verdict"]["strictly_increases"]
    curve = [c["held_recovery"] for c in out["curve"]]
    assert curve == sorted(curve)
    assert curve[-1] == 1.0
    assert all(c["false"] == 0 for c in out["curve"])


def test_stream_is_deterministic():
    assert run(_args()) == run(_args())


def test_domain_laws_are_declared_in_lisp():
    rules = true_rules()
    shapes = {(r.head.pred, tuple(b.pred for b in r.body)) for r in rules}
    for p in TRANSITIVE:
        assert (p, (p, p)) in shapes            # transitivity
    assert (INVERSE[1], (INVERSE[0],)) in shapes  # inverse
    # expansion is pure rewriting: the macro call turns into a `rule` form
    env = Env()
    eval_sexp("(defmacro trans (?p) (rule (?p ?x ?y) (?p ?x ?z) (?p ?z ?y)))", env)
    expanded = macroexpand(("trans", "subclass_of"), env.macros)
    assert expanded[0] == "rule" and expanded[1] == ("subclass_of", "?x", "?y")
    # the declaration is deterministic
    assert domain_forms(DOMAIN_SOURCE) == domain_forms(DOMAIN_SOURCE)