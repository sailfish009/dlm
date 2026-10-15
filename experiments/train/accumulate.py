"""DLM v0.0039 train experiment: accumulating learner vs memoryless refit.

The stream experiment already showed that ``ground.learn`` is memoryless: it
refits on the revealed set each round and cannot *retract* a rule that later
evidence falsifies.  This run drives the accumulating ``Learner`` round by round
on the same controlled domain and reports, honestly, what accumulation buys:

* negatives are revealed progressively, so an early-admitted over-general rule
  can be falsified later -- accumulation retracts it, refit simply rebuilds;
* every round checks ``false_final`` against the *full revealed complement*,
  never a sample;
* test recovery is on disjoint (open-universe) entities, so a same-distribution
  artifact cannot masquerade as generalization.

Two deterministic probes are always included: a micro-ladder that *guarantees* a
retraction fires, and a checkpoint/resume round-trip.  The stream part reports
whatever actually happens.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from typing import List

from dlm import Atom, Const, closure
from dlm.abstract import theory_dl
from dlm.accumulate import Learner, rule_key
from dlm.ground import Experience, Ground, learn
from dlm.theory import load_theory, save_theory
from experiments.stream.run import gen_synthetic, negatives, truth


def A(pred, x, y):
    return Atom(pred, (Const(x), Const(y)))


def recovery(exp_rules, test_facts, test_pos) -> float:
    if not test_pos:
        return 1.0
    closed = closure(Experience(tuple(exp_rules)).to_kb(Ground(()).base(test_facts)))
    return round(len(closed & test_pos) / len(test_pos), 4)


def retraction_probe() -> dict:
    """A guaranteed ladder: admit q(X):-r(X), then falsify it with q(b)."""
    L = Learner(Ground())
    L = L.observe(facts={A("r", "a", "a")}, positives={A("q", "a", "a")})
    L = L.observe(facts={A("r", "b", "b")}, negatives={A("q", "b", "b")})
    rec = L.memory[-1]
    return {
        "admitted": len(L.memory[0]["added"]),
        "retracted": len(rec["retracted"]),
        "final_rules": len(L.experience.rules),
        "false_final": rec["false_final"],
        "abstains": rec["uncovered"] > 0,
    }


def checkpoint_probe(seed: int) -> dict:
    """Checkpoint after one round, resume, and match the uninterrupted path."""
    def round1():
        return Learner(Ground()).observe(facts={A("r", "a", "a")},
                                         positives={A("q", "a", "a")})
    straight = round1().observe(facts={A("r", "b", "b")}, negatives={A("q", "b", "b")})
    mid = round1()
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, f"learner_{seed}.json")
        save_theory(path, mid.to_theory())
        resumed = Learner.from_theory(load_theory(path))
    cont = resumed.observe(facts={A("r", "b", "b")}, negatives={A("q", "b", "b")})
    return {
        "same_rules": cont.experience == straight.experience,
        "same_false": cont.memory[-1]["false_final"] == straight.memory[-1]["false_final"],
        "rounds": len(cont.memory),
    }


def _schedule(n: int, k: int, rounds: int) -> int:
    return max(1, n * k // rounds) if k else 0


def run(args) -> dict:
    train, test = gen_synthetic(args.seed, args.n_train, args.n_test,
                                args.chains, args.chain_len)
    train_pos = truth(train)
    test_pos = truth(test)
    full_negs = set(negatives(train, train_pos, args.max_neg))
    facts_sorted = sorted(train, key=str)
    negs_sorted = sorted(full_negs, key=str)
    rounds = args.rounds

    arms = {}
    for arm in ("accumulate", "refit"):
        records: List[dict] = []
        learner = Learner(Ground())
        t0 = time.time()
        for k in range(1, rounds + 1):
            fk = set(facts_sorted[: _schedule(len(facts_sorted), k, rounds)])
            posk = truth(fk)
            negk = set(negs_sorted[: _schedule(len(negs_sorted), k, rounds)])
            if arm == "accumulate":
                learner = learner.observe(facts=fk, positives=posk, negatives=negk,
                                          max_body=args.max_body, extra_vars=args.extra_vars,
                                          max_rules=args.max_rules, compress=not args.no_compress)
                rec = dict(learner.memory[-1])
            else:
                res = learn(Ground(()), fk, posk, negk, max_body=args.max_body,
                            extra_vars=args.extra_vars, max_rules=args.max_rules)
                closed = closure(res.experience.to_kb(Ground(()).base(fk)))
                false_final = sorted(n for n in negk if n in closed)
                rec = {
                    "round": k, "facts": len(fk), "revealed_negatives": len(negk),
                    "positives": len(posk), "retracted": [], "added": [],
                    "compressed": [], "dl": theory_dl(res.experience.rules),
                    "covered": len(res.covered), "uncovered": len(posk) - len(res.covered),
                    "false_final": len(false_final),
                    "false_atoms": [str(a) for a in false_final],
                }
                learner = Learner(Ground(), res.experience)
            rec["rules"] = len(learner.experience.rules)
            rec["held_recovery"] = recovery(learner.experience.rules, test, test_pos)
            records.append(rec)
        keys = [rule_key(r) for r in learner.experience.rules]
        arms[arm] = {
            "records": records,
            "final_rules": len(learner.experience.rules),
            "duplicate_rules": len(keys) - len(set(keys)),
            "held_recovery": records[-1]["held_recovery"],
            "retraction_events": sum(len(r["retracted"]) for r in records),
            "false_final": records[-1]["false_final"],
            "seconds": round(time.time() - t0, 3),
        }

    identity = round(len(test & test_pos) / len(test_pos), 4) if test_pos else 1.0
    probes = {"retraction": retraction_probe(), "checkpoint": checkpoint_probe(args.seed)}
    out = {
        "config": vars(args),
        "domain": {
            "train_facts": len(train), "train_pairs": len(train_pos),
            "test_facts": len(test), "test_pairs": len(test_pos),
            "revealed_negatives": len(full_negs),
        },
        "identity_recovery": identity,
        "arms": arms,
        "probes": probes,
    }
    acc = arms["accumulate"]
    out["verdict"] = {
        "retraction_probe_fires": probes["retraction"]["retracted"] >= 1
                                 and probes["retraction"]["abstains"],
        "checkpoint_roundtrip": probes["checkpoint"]["same_rules"]
                                and probes["checkpoint"]["same_false"],
        "accumulate_sound_every_round": all(r["false_final"] == 0 for r in acc["records"]),
        "accumulate_no_duplicates": acc["duplicate_rules"] == 0,
        "accumulate_beats_identity": acc["held_recovery"] > identity + 0.05,
        "accumulate_matches_refit": acc["held_recovery"] >= arms["refit"]["held_recovery"] - 0.01,
    }
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--n-train", type=int, default=24)
    p.add_argument("--n-test", type=int, default=18)
    p.add_argument("--chains", type=int, default=3)
    p.add_argument("--chain-len", type=int, default=6)
    p.add_argument("--rounds", type=int, default=4)
    p.add_argument("--max-body", type=int, default=2)
    p.add_argument("--extra-vars", type=int, default=1)
    p.add_argument("--max-rules", type=int, default=8)
    p.add_argument("--max-neg", type=int, default=8000)
    p.add_argument("--no-compress", action="store_true")
    p.add_argument("--json", default="")
    args = p.parse_args(argv)

    out = run(args)
    text = json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False)
    print(text)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0 if all(out["verdict"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())