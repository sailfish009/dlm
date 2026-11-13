"""Synthetic proof-state world for M1.

Pure symbolic oracle: no learned component decides truth.  A world is a
finite propositional Horn theory over unary predicates and entities.
Candidate actions are Horn rules.  Utility is measured by closure growth on a
sandbox copy of the current theory.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

P = 6
ENTITIES = {"train": tuple(range(0, 12)), "val": tuple(range(12, 18)), "test": tuple(range(18, 26))}
TOTAL_ENTITIES = 26
GOAL_COUNT = 3
N_STEPS = 4
POOL_SIZE = 24


@dataclass(frozen=True)
class Rule:
    head: int
    body: Tuple[int, ...]

    @property
    def cost(self) -> float:
        return 0.5 + 0.75 * len(self.body)


@dataclass
class World:
    split: str
    entities: Tuple[int, ...]
    facts: Dict[Tuple[int, int], bool]
    theory: List[Rule]
    candidates: List[Rule]
    goals: List[Tuple[int, int]]
    forbidden: List[Tuple[int, int]] = field(default_factory=list)


# ---------- closure ----------

def closure(facts: Dict[Tuple[int, int], bool], rules: Sequence[Rule], entities: Sequence[int]) -> set[Tuple[int, int]]:
    known = {a for a, v in facts.items() if v}
    changed = True
    while changed:
        changed = False
        for r in rules:
            if not r.body:
                continue
            for e in entities:
                if all((p, e) in known for p in r.body):
                    a = (r.head, e)
                    if a not in known:
                        known.add(a)
                        changed = True
    return known


# ---------- generation ----------

def _all_rules() -> List[Rule]:
    out = []
    for h in range(P):
        for b in range(P):
            if b != h:
                out.append(Rule(h, (b,)))
        for b1 in range(P):
            for b2 in range(b1 + 1, P):
                if h not in (b1, b2):
                    out.append(Rule(h, (b1, b2)))
    return out


ALL_RULES = _all_rules()


def make_world(rng: random.Random, split: str, idx: int, conflict: bool = False) -> World:
    ents = rng.sample(ENTITIES[split], 6)
    facts: Dict[Tuple[int, int], bool] = {}
    for p in range(P):
        for e in ents:
            facts[(p, e)] = rng.random() < 0.26
        # guarantee some support for every predicate
        facts[(p, rng.choice(ents))] = True

    # Start with two seed rules; candidates are the rest.
    order = ALL_RULES[:]
    rng.shuffle(order)
    theory = order[:2]
    candidates = order[2:2 + POOL_SIZE]

    base = closure(facts, theory, ents)
    goals = []
    for r in candidates:
        for e in ents:
            if all((p, e) in base for p in r.body) and (r.head, e) not in base:
                goals.append((r.head, e))
    rng.shuffle(goals)
    goals = goals[:GOAL_COUNT]
    if not goals:
        return make_world(rng, split, idx, conflict)
    forbidden = []
    if conflict:
        pool = []
        for r in candidates:
            for e in ents:
                if all((p, e) in base for p in r.body) and (r.head, e) not in base and (r.head, e) not in goals:
                    pool.append((r.head, e))
        rng.shuffle(pool)
        forbidden = pool[:2]
        if not forbidden:
            return make_world(rng, split, idx, conflict)
    return World(split, tuple(ents), facts, theory, candidates, goals, forbidden)


# ---------- oracle utility ----------

def utility(world: World, rules: Sequence[Rule], cand: Rule, goals: Sequence[Tuple[int, int]]) -> float:
    ents = world.entities
    before = closure(world.facts, rules, ents)
    after = closure(world.facts, list(rules) + [cand], ents)
    new = after - before
    goal_new = sum(1 for g in goals if g in after and g not in before)
    # proof gain with a goal weight; cost discourages long rules.
    return 5.0 * goal_new + 0.15 * len(new) - cand.cost


# ---------- features ----------

def _support(body: Sequence[int], known: set[Tuple[int, int]], ents: Sequence[int]) -> int:
    return sum(1 for e in ents if all((p, e) in known for p in body))


def state_features(world: World, rules: Sequence[Rule], goals: Sequence[Tuple[int, int]]) -> List[float]:
    ents = world.entities
    known = closure(world.facts, rules, ents)
    total = P * len(ents)
    goal_known = sum(1 for g in goals if g in known)
    live = [r for r in world.candidates if r not in rules]
    supports = [_support(r.body, known, ents) / len(ents) for r in live]
    return [
        len(known) / total,
        goal_known / max(1, len(goals)),
        1.0 - len(known) / total,
        len(live) / POOL_SIZE,
        sum(supports) / max(1, len(supports)),
        max(supports) if supports else 0.0,
        min(supports) if supports else 0.0,
        len(rules) / 8.0,
    ]


def candidate_features(world: World, rules: Sequence[Rule], goals: Sequence[Tuple[int, int]], cand: Rule) -> List[float]:
    ents = world.entities
    known = closure(world.facts, rules, ents)
    sup = _support(cand.body, known, ents) / len(ents)
    goal_count = sum(1 for h, _e in goals if h == cand.head) / max(1, len(goals))
    head_known = sum(1 for e in ents if (cand.head, e) in known) / len(ents)
    body_known = sum(1 for e in ents if all((p, e) in known for p in cand.body)) / len(ents)
    f = [
        len(cand.body) / 2.0,
        cand.cost / 2.0,
        sup,
        body_known,
        head_known,
        goal_count,
        1.0 if sup > 0 else 0.0,
        1.0 if goal_count > 0 else 0.0,
    ]
    f += [1.0 if cand.head == p else 0.0 for p in range(P)]
    for slot in range(2):
        f += [1.0 if slot < len(cand.body) and cand.body[slot] == p else 0.0 for p in range(P)]
    return f


CAND_DIM = 8 + P + 2 * P

# ---------- M2: utility, conflict, admission, hard negatives ----------

M2_CAND_DIM = CAND_DIM + 2


def state_features_m2(world: World, rules: Sequence[Rule], goals: Sequence[Tuple[int, int]]) -> List[float]:
    base = state_features(world, rules, goals)
    known = closure(world.facts, rules, world.entities)
    fk = sum(1 for a in world.forbidden if a in known)
    return base + [fk / max(1, len(world.forbidden)), 1.0 - fk / max(1, len(world.forbidden))]


def candidate_features_m2(world: World, rules: Sequence[Rule], goals: Sequence[Tuple[int, int]], cand: Rule) -> List[float]:
    base = candidate_features(world, rules, goals, cand)
    known = closure(world.facts, rules, world.entities)
    fh = sum(1 for h, _e in world.forbidden if h == cand.head)
    fk = sum(1 for h, e in world.forbidden if h == cand.head and (h, e) in known)
    return base + [fh / max(1, len(world.forbidden)), fk / max(1, len(world.forbidden))]


def utility2(world: World, rules: Sequence[Rule], cand: Rule, goals: Sequence[Tuple[int, int]]) -> dict:
    ents = world.entities
    before = closure(world.facts, rules, ents)
    after = closure(world.facts, list(rules) + [cand], ents)
    new = after - before
    goal_new = sum(1 for g in goals if g in after and g not in before)
    conflict_new = sum(1 for g in world.forbidden if g in after and g not in before)
    # MDL term is the rule cost; conflict is the hard logical penalty.
    utility = 5.0 * goal_new + 0.15 * len(new) - cand.cost - 8.0 * conflict_new
    return {
        "new": len(new),
        "goal_new": goal_new,
        "conflict": conflict_new,
        "mdl": cand.cost,
        "utility": utility,
        "admit": 1.0 if (goal_new > 0 and conflict_new == 0) else 0.0,
    }


def make_steps_m2(world: World, rng: random.Random) -> List[dict]:
    rules = list(world.theory)
    steps = []
    used = set(rules)
    for _ in range(N_STEPS):
        live = [r for r in world.candidates if r not in used]
        if not live:
            break
        sf = state_features_m2(world, rules, world.goals)
        cfs = [candidate_features_m2(world, rules, world.goals, r) for r in live]
        br = [utility2(world, rules, r, world.goals) for r in live]
        us = [b["utility"] for b in br]
        best = max(range(len(live)), key=lambda i: us[i])
        hard = []
        for i, f in enumerate(cfs):
            # text/body-supported but logically conflicting candidate
            hard.append(1.0 if (br[i]["conflict"] > 0 and f[3] >= 0.5 and f[5] > 0) else 0.0)
        steps.append({
            "state": sf,
            "cands": cfs,
            "utils": us,
            "breakdown": br,
            "admit": [b["admit"] for b in br],
            "conflict": [b["conflict"] for b in br],
            "hard_neg": hard,
            "best": best,
            "rules": live,
        })
        if us[best] <= 0:
            break
        rules.append(live[best])
        used.add(live[best])
    return steps


def build_split_m2(split: str, n_worlds: int, seed: int) -> List[List[dict]]:
    rng = random.Random(seed)
    out = []
    for i in range(n_worlds):
        w = make_world(rng, split, i, conflict=True)
        out.append(make_steps_m2(w, rng))
    return out


def make_steps(world: World, rng: random.Random) -> List[dict]:
    rules = list(world.theory)
    steps = []
    used = set(rules)
    for _ in range(N_STEPS):
        live = [r for r in world.candidates if r not in used]
        if not live:
            break
        sf = state_features(world, rules, world.goals)
        cfs = [candidate_features(world, rules, world.goals, r) for r in live]
        us = [utility(world, rules, r, world.goals) for r in live]
        best = max(range(len(live)), key=lambda i: us[i])
        steps.append({"state": sf, "cands": cfs, "utils": us, "best": best, "rules": live})
        if us[best] <= 0:
            break
        rules.append(live[best])
        used.add(live[best])
    return steps


def build_split(split: str, n_worlds: int, seed: int) -> List[List[dict]]:
    rng = random.Random(seed)
    out = []
    for i in range(n_worlds):
        w = make_world(rng, split, i)
        out.append(make_steps(w, rng))
    return out
