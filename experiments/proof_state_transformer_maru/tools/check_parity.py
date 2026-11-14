#!/usr/bin/env python3
"""Parity check: C world/oracle/features vs the reference M1 implementation.

The C kernel dumps its generated worlds and the features/utilities it computed.
This script rebuilds each world with `experiments/m1_proof_state/world.py`
(reference, stdlib only) and recomputes closure, M1 state/candidate features and
the kernel utility, then compares. It is evidence tooling, not a release gate:
the release gates are bash/awk over native output only.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = HERE.parents[1] / "m1_proof_state"
sys.path.insert(0, str(REF))
import world as W  # noqa: E402

TOL = 2e-5


def parse(path: Path):
    worlds = []
    cur = None
    step = None
    for line in path.read_text().splitlines():
        t = line.split()
        if not t:
            continue
        tag = t[0]
        if tag == "W":
            cur = {
                "split": int(t[1]), "idx": int(t[2]), "ngoals": int(t[3]),
                "ents": [], "facts": [], "theory": [], "cands": [],
                "goals": [], "steps": [],
            }
            worlds.append(cur)
        elif tag == "E":
            cur["ents"] = [int(x) for x in t[1:]]
        elif tag == "F":
            cur["facts"] = [int(x) for x in t[1:]]
        elif tag == "T":
            cur["theory"] = [int(x) for x in t[1:]]
        elif tag == "C":
            cur["cands"] = [int(x) for x in t[1:]]
        elif tag == "G":
            cur["goals"] = [tuple(int(v) for v in x.split(":")) for x in t[1:]]
        elif tag == "STEP":
            step = {"s": int(t[1]), "nlive": int(t[2]), "best": int(t[3]),
                    "live": [int(x) for x in t[4:]], "state": None, "cf": {}, "util": {}}
            cur["steps"].append(step)
        elif tag == "STATE":
            step["state"] = [float(x) for x in t[1:]]
        elif tag == "CF":
            rid = int(t[1])
            ui = t.index("U")
            step["cf"][rid] = [float(x) for x in t[2:ui]]
            step["util"][rid] = float(t[ui+1])
    return worlds


def main() -> int:
    dump = Path(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "out" / "worlds.txt")
    worlds = parse(dump)
    print(f"PARITY worlds={len(worlds)}")
    maxerr_s = maxerr_c = maxerr_u = 0.0
    nsteps = ncf = 0
    for d in worlds:
        ents = tuple(d["ents"])
        facts = {(p, e): bool((d["facts"][ei] >> p) & 1)
                 for ei, e in enumerate(ents) for p in range(W.P)}
        theory = [W.ALL_RULES[r] for r in d["theory"]]
        cands = [W.ALL_RULES[r] for r in d["cands"]]
        goals = [(p, ents[ei]) for p, ei in d["goals"]]
        w = W.World("x", ents, facts, theory, cands, goals)

        # replicate the rollout and compare live sets / best / utilities
        rules = list(theory)
        used = set(theory)
        for si, st in enumerate(d["steps"]):
            live = [r for r in w.candidates if r not in used]
            live_ids = [W.ALL_RULES.index(r) for r in live]
            if live_ids != st["live"]:
                print(f"MISMATCH live world={d['idx']} step={si}: {live_ids} != {st['live']}")
                return 1
            sf = W.state_features(w, rules, goals)
            for i, (a, b) in enumerate(zip(sf, st["state"])):
                maxerr_s = max(maxerr_s, abs(a - b))
            utils = []
            for rid, r in zip(st["live"], live):
                cf = W.candidate_features(w, rules, goals, r)
                for i, (a, b) in enumerate(zip(cf, st["cf"][rid])):
                    maxerr_c = max(maxerr_c, abs(a - b))
                u = W.utility(w, rules, r, goals)
                maxerr_u = max(maxerr_u, abs(u - st["util"][rid]))
                utils.append(u)
                ncf += 1
            best = max(range(len(utils)), key=lambda i: utils[i])
            if best != st["best"]:
                print(f"MISMATCH best world={d['idx']} step={si}: {best} != {st['best']}")
                return 1
            nsteps += 1
            if utils[best] <= 0:
                break
            rules.append(live[best])
            used.add(live[best])
    print(f"PARITY steps={nsteps} candidates={ncf}")
    print(f"PARITY max_abs_err state={maxerr_s:.2e} cand={maxerr_c:.2e} util={maxerr_u:.2e}")
    ok = max(maxerr_s, maxerr_c, maxerr_u) <= TOL
    print("PARITY-PASS" if ok else "PARITY-FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())