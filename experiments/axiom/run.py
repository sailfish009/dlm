#!/usr/bin/env python3
"""End-to-end falsifier for the IR-native axiom-moving learner."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dlm import (Atom, Rule, canonical_json, closure, dump, episode_ir, field,
                 from_json, new_state, rule_from_ir, rule_to_ir, run)  # noqa: E402


def A(pred, *args):
    return Atom(pred, args)


def world(source, a, b, c, role="train"):
    nodes = (a, b, c)
    facts = {A("edge", a, b), A("edge", b, c)}
    positive = {A("reach", a, c)}
    negative = {A("reach", x, z) for x in nodes for z in nodes if (x, z) != (a, c)}
    return episode_ir(source, facts, positive, negative, role=role)


def execute():
    episodes = (world("train-a", "a", "b", "c"),
                world("train-b", "d", "e", "f"),
                world("held", "g", "h", "i", "validation"))
    state = new_state(episodes)
    evidence_before = canonical_json(field(state, "evidence"))
    repl = run("(step 96)", state)
    transition = field(repl, "value")[1]
    after = field(repl, "state")[1]
    experience = field(field(after, "theory"), "experience")[1:]
    learned = tuple(rule_from_ir(rule) for rule in experience)
    expected = Rule(A("reach", "?x", "?z"),
                    (A("edge", "?x", "?y"), A("edge", "?y", "?z")))
    held = episodes[-1]
    from dlm.kernel import episode_data
    held_data = episode_data(held)
    closed = closure(held_data["facts"], learned)
    restored = from_json(canonical_json(after))
    verdict = {
        "one_model_state_tree": field(after, "version")[1] == "0.0.65",
        "treelisp_controls_transition": field(transition, "action")[1][0] == "learn-round",
        "program_language_embedded": bool(field(field(after, "language"), "programs")[1:]),
        "native_contrast_persisted": bool(field(field(after, "decision"), "replay")[1:]),
        "axiom_discovered": learned == (expected,),
        "evidence_fixed": canonical_json(field(after, "evidence")) == evidence_before,
        "heldout_entailed": A("reach", "g", "i") in closed,
        "heldout_no_false": not (held_data["contradicted"] & closed),
        "experience_not_ground": not field(field(after, "theory"), "ground")[1:],
        "exact_json_roundtrip": restored == after,
        "event_is_ir": bool(field(transition, "events")[1:]),
        "experience_lifecycle_recorded": bool(field(after, "memory")[1:]),
    }
    return {
        "version": "0.0.65",
        "learned": [dump(rule_to_ir(rule)) for rule in learned],
        "checks": field(field(after, "metrics"), "checks")[1],
        "state_root": canonical_json(after)[:80] + "...",
        "verdict": verdict,
        "all_ok": all(verdict.values()),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="")
    args = parser.parse_args()
    result = execute()
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.json:
        path = Path(args.json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0 if result["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
