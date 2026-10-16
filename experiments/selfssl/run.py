#!/usr/bin/env python3
"""Endless event-driven self-study whose complete state is one IR-TREE."""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dlm import (Atom, Store, acquire_once, call_facts, episode_ir, evaluate_expr,
                 field, lower_paths, new_state, observe, realize, source_hash,
                 stop_status)  # noqa: E402


def graph_oracle(nodes: frozenset[str], edges: frozenset[tuple[str, str]]):
    adjacent = {node: set() for node in nodes}
    for left, right in edges:
        adjacent[left].add(right)
    reached = set()
    for start in nodes:
        pending = list(adjacent[start])
        seen = set()
        while pending:
            end = pending.pop()
            if end in seen:
                continue
            seen.add(end)
            if end != start:
                reached.add((start, end))
            pending.extend(adjacent.get(end, ()) - seen)
    return frozenset(reached)


def source_observation(paths):
    package = lower_paths(paths, ROOT)
    # Learn about the learning subsystem itself; the complete package remains
    # the subject IR, while this bounded projection keeps each round inspectable.
    public_learning = {"learn_round", "evaluate", "commit_transition", "observe",
                       "synthesize", "rank"}
    direct = frozenset(atom for atom in call_facts(package)
                       if atom.args[0].startswith("dlm.learn.")
                       and atom.args[0].split(".")[-1] in public_learning)
    edges = frozenset((atom.args[0], atom.args[1]) for atom in direct)
    nodes = frozenset(x for edge in edges for x in edge)
    reachable = graph_oracle(nodes, edges)
    possible = {(x, y) for x in nodes for y in nodes if x != y}
    contradicted = {Atom("depends", pair) for pair in possible - set(reachable)}
    train, held = set(), set()
    for pair in reachable:
        digest = hashlib.sha256((pair[0] + "\0" + pair[1]).encode()).digest()[0]
        (train if digest % 2 == 0 else held).add(Atom("depends", pair))
    if not train and held:
        train.add(held.pop())
    if not held and len(train) > 1:
        held.add(train.pop())
    episodes = (
        episode_ir("own-source/train", direct, train, contradicted, role="train"),
        episode_ir("own-source/held", direct, held, contradicted, role="validation"),
    )
    fingerprint = source_hash(paths)
    subject = ("source-subject", ("sha256", fingerprint), ("pyir", package))
    return episodes, subject, fingerprint


def subject_hash(state):
    subject = field(state, "subject")[1]
    return field(subject, "sha256")[1] if subject[0] == "source-subject" else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-concepts", type=int, default=40)
    parser.add_argument("--budget", type=int, default=256)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--rounds", type=int, default=0,
                        help="0 means watch until Ctrl-C")
    parser.add_argument("--store", type=Path,
                        default=ROOT / "experiments/selfssl/store")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=0)
    parser.add_argument("--no-external", action="store_true",
                        help="disable model-owned need assessment/acquisition")
    transport = parser.add_mutually_exclusive_group()
    transport.add_argument("--online", dest="online", action="store_true",
                           help="allow fresh HTTP fetches (default)")
    transport.add_argument("--offline", dest="online", action="store_false",
                           help="use only the deterministic response cache")
    parser.set_defaults(online=True)
    parser.add_argument("--providers", default="wikipedia,github,web-search")
    parser.add_argument("--external-limit", type=int, default=1)
    parser.add_argument("--web-timeout", type=float, default=10.0)
    parser.add_argument("--cache", type=Path,
                        default=ROOT / "experiments/selfssl/cache")
    args = parser.parse_args()
    if (args.max_concepts < 1 or args.budget < 1 or args.external_limit < 1
            or args.web_timeout <= 0):
        parser.error("limits must be positive")

    paths = tuple(sorted((ROOT / "dlm").glob("*.py")))
    episodes, subject, fingerprint = source_observation(paths)
    store = Store(args.store)
    if store.exists() and not args.fresh:
        state = store.load()
        if subject_hash(state) != fingerprint:
            transition = observe(state, episodes, subject)
            state = store.append(state, transition)
    else:
        state = new_state(episodes, subject=subject)
        store.create(state, overwrite=args.fresh)
    print("IR self-study is running; it speaks only on measured improvement. Ctrl-C stops.",
          flush=True)

    count = 0
    try:
        while not args.rounds or count < args.rounds:
            episodes, subject, fingerprint = source_observation(paths)
            if subject_hash(state) != fingerprint:
                state = store.append(state, observe(state, episodes, subject))
            if not args.no_external:
                providers = tuple(name.strip() for name in args.providers.split(",")
                                  if name.strip())
                acquisition = acquire_once(
                    state, cache_dir=args.cache, offline=not args.online,
                    providers=providers, limit=args.external_limit,
                    timeout=args.web_timeout)
                if acquisition is not None:
                    state = store.append(state, acquisition)
            experience = field(field(state, "theory"), "experience")[1:]
            saturated = field(stop_status(state), "status")[1] == "saturated"
            budget = 0 if saturated or len(experience) >= args.max_concepts else args.budget
            transition = evaluate_expr(("step", budget), state)
            state = store.append(state, transition)
            for event in field(transition, "events")[1:]:
                print(realize(event), flush=True)
            count += 1
            if args.checkpoint_every and count % args.checkpoint_every == 0:
                store.checkpoint(state)
            if (not args.rounds or count < args.rounds) and args.interval:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped by user; the snapshot and Experience journal were preserved.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
