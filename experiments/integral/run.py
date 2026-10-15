"""Experiments/integral -- the three integral layers of deduction (v0.0049).

One question: where does deduction need INTEGRATION?  Three layers, three
verdicts -- and each verdict is a falsifier.

  A. forward integral (a POTENTIAL).  ``closure`` is the least fixed point of the
     immediate-consequence operator; it is path-INDEPENDENT and its DEBT (targets
     it fails to reach) is kernel-decided.  ``E = content_loss + MDL`` is genuine.
  B. evidence integral (a MEASURE).  ``Z = sum_T exp(-E(T))`` counts how many
     candidate theories are good; MAP cannot see that.  ``F <= E_MAP`` and
     ``sum posterior = 1`` are invariant checks.
  C. order integral (a CONNECTION).  Under a bounded search, per-rule credit
     depends on the ORDER rules are tried.  Sweeping the order samples a field
     whose discrete circulation (curl/holonomy) is NONZERO -- credit is not the
     gradient of any scalar.  A scalar control has EXACTLY zero circulation; the
     curl is gauge-invariant.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.connection import (block_circulation, credit, curl, deep_credit,
                            execute, gauge_shift, holonomy, scalar_curl)
from dlm.gist import gist_rules
from dlm.ground import Ground, learn
from dlm.integral import atom_str, evidence, forward, loss_integral
from dlm.lisp import form_to_rule

try:
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import (STRUCTURAL, STRUCT_GROUND, atom_of, negatives,
                             transitive)
    from ..mnist.semantics import bridge_forms
    from ..reading.run import CACHE, NORTH_STAR_SRC
except ImportError:  # direct `python experiments/integral/run.py`
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import STRUCTURAL, STRUCT_GROUND, atom_of, negatives, transitive
    from mnist.semantics import bridge_forms
    from reading.run import CACHE, NORTH_STAR_SRC

HERE = os.path.dirname(os.path.abspath(__file__))


def _kb_with(base_kb: KnowledgeBase, rules) -> KnowledgeBase:
    kb = base_kb.copy()
    for r in rules:
        kb.add_rule(r)
    return kb


# -- A. the real north-star theory: facts + bridges + gist + induced calls law --
def _build(src: str, cache_dir: str, offline: bool) -> dict:
    ext = extract(src, "main")
    k = acquire_knowledge(ext["facts"], ext["labels"], cache_dir=cache_dir, offline=offline)
    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(k["meanings"])}
    calls = {a for a in base if a.pred == "calls"}
    positives = transitive(calls)
    universe = sorted({t.name for a in calls for t in a.args})
    negs = negatives(positives, universe)
    struct = {a for a in base if a.pred in STRUCTURAL}
    res = learn(STRUCT_GROUND, struct, positives, negs,
                max_body=2, extra_vars=2, max_rules=4)
    return {
        "base": base,
        "base_kb": KnowledgeBase(set(base)),
        "bridges": tuple(form_to_rule(f) for f in bridge_forms()),
        "gists": tuple(gist_rules()),
        "learned": tuple(res.experience.rules),
        "negatives": tuple(negs),
        "positives": positives,
    }


def run_forward(t: dict) -> dict:
    base_kb, base = t["base_kb"], t["base"]
    all_rules = t["bridges"] + t["gists"] + t["learned"]
    full_set = closure(_kb_with(base_kb, all_rules))
    target = sorted(full_set - base, key=atom_str)
    full = forward(base_kb, all_rules, target, negatives=t["negatives"])
    ablated = forward(base_kb, t["bridges"] + t["gists"], target, negatives=t["negatives"])
    c1 = closure(_kb_with(base_kb, all_rules))
    c2 = closure(_kb_with(base_kb, tuple(reversed(all_rules))))
    verdict = {
        "forward_integral_defined": len(full.closure) > len(base),
        "forward_reaches_all_targets": full.debt == (),
        "forward_sound": full.false_assert == 0,
        "closure_path_independent": c1 == c2,
        "debt_is_content_loss": len(ablated.debt) > len(full.debt),
        "kernel_untouched": closure(_kb_with(base_kb, all_rules)) == full.closure,
    }
    return {
        "base_facts": len(base),
        "derived": len(full.closure) - len(base),
        "target": len(target),
        "full": full.to_dict(),
        "ablated": ablated.to_dict(),
        "verdict": verdict,
    }


# -- B. the evidence integral over candidate theories -------------------------
def run_evidence(t: dict, target) -> dict:
    base_kb = t["base_kb"]
    candidates = [
        ("full", t["bridges"] + t["gists"] + t["learned"]),
        ("no_learned", t["bridges"] + t["gists"]),
        ("gist_only", t["gists"]),
        ("bridges_only", t["bridges"]),
        ("empty", ()),
    ]
    ev = evidence(candidates, base_kb, target, negatives=t["negatives"], beta=1.0, cost=0.5)
    twin = evidence([("t1", t["gists"]), ("t2", t["gists"])], base_kb, target,
                    negatives=t["negatives"], beta=1.0, cost=0.5)
    verdict = {
        "evidence_normalized": abs(sum(ev.posterior) - 1.0) < 1e-6,
        "evidence_free_energy_le_map": ev.free_energy <= ev.map_energy + 1e-9,
        "evidence_multiplicity_positive": ev.multiplicity_reward > 1e-9,
        "twin_theories_reward_log2": abs(twin.multiplicity_reward - 0.693147) < 1e-3,
        "map_prefers_full": ev.map_name == "full",
    }
    return {"evidence": ev.to_dict(), "twin": twin.to_dict(), "verdict": verdict}


# -- C. the connection: order-sensitive credit, curl, gauge, holonomy ---------
def _probe():
    """A bounded search whose result depends on rule ORDER (budget-limited).

    ``q :- p`` is cheap and succeeds.  ``q :- deep`` is a dead-end chain that
    eats the whole budget.  With budget 5, whichever rule is tried first decides
    whether ``q`` is proved -- so per-rule credit depends on the order.
    """
    x = Var("x")
    facts = {Atom("p", (Const("a"),))}
    r_p = Rule(Atom("q", (x,)), (Atom("p", (x,)),), "r_p")
    r_d = Rule(Atom("q", (x,)), (Atom("deep", (x,)),), "r_deep")
    chain, prev = [], "deep"
    for name in ("d1", "d2", "d3", "d4", "d5"):
        chain.append(Rule(Atom(prev, (x,)), (Atom(name, (x,)),), f"r_{name}"))
        prev = name
    # prev == d5: no rule for d5, so the chain dead-ends after 5 attempts.
    return KnowledgeBase(set(facts)), (r_p, r_d) + tuple(chain), Atom("q", (Const("a"),))


def run_connection() -> dict:
    kb, rules, goal = _probe()
    budget = 5

    def field(x, y):
        tr = execute(kb, rules, [goal], priority={"r_p": x, "r_deep": y},
                     budget=budget, max_depth=32)
        n = credit(tr).net()
        return (float(n.get("r_p", 0)), float(n.get("r_deep", 0)))

    def field_g(x, y):
        p = gauge_shift({"r_p": x, "r_deep": y}, 5.0)
        tr = execute(kb, rules, [goal], priority=p, budget=budget, max_depth=32)
        n = credit(tr).net()
        return (float(n.get("r_p", 0)), float(n.get("r_deep", 0)))

    grid = (-1.0, 0.0, 1.0)
    cells = [(a, b) for a in grid for b in grid]
    h = holonomy(field, cells)
    block = block_circulation(field, 0.0, 0.0, n=2)
    scalar_zero = all(
        abs(scalar_curl(lambda x, y: x * x + y * y, a, b)) < 1e-12
        and abs(scalar_curl(lambda x, y: 3.0 * x - 2.0 * y + 7.0, a, b)) < 1e-12
        for (a, b) in cells
    )
    gauge_ok = all(abs(curl(field, a, b) - curl(field_g, a, b)) < 1e-12 for (a, b) in cells)

    # deep vs shallow on a locally-successful but dead-ending branch.
    x = Var("x")
    dp = KnowledgeBase({Atom("p", (Const("a"),))})
    dp_rules = (Rule(Atom("mid", (x,)), (Atom("p", (x,)),), "r_mid"),
                Rule(Atom("top", (x,)), (Atom("mid", (x,)), Atom("gone", (x,))), "r_top"))
    dp_goal = Atom("top", (Const("a"),))
    shallow = credit(execute(dp, dp_rules, [dp_goal], budget=100, max_depth=16))
    deep = deep_credit(dp, dp_rules, [dp_goal], budget=100, max_depth=16)

    def proved(prio):
        tr = execute(kb, rules, [goal], priority=prio, budget=budget, max_depth=32)
        return bool(tr.proved)

    verdict = {
        "connection_nonzero_holonomy": bool(h),
        "scalar_controls_exactly_zero": scalar_zero,
        "gauge_invariant": gauge_ok,
        "closed_loop_holonomy_nonzero": block != 0.0,
        "deep_differs_from_shallow": deep.net() != shallow.net(),
        "order_changes_result": proved({"r_p": 1, "r_deep": 0}) != proved({"r_p": 0, "r_deep": 1}),
    }
    return {
        "field": {k: round(v, 6) for k, v in sorted(h.items())},
        "block_circulation": round(block, 6),
        "credit_order_probe": {
            "proved_when_shallow_first": proved({"r_p": 1, "r_deep": 0}),
            "proved_when_deep_first": proved({"r_p": 0, "r_deep": 1}),
        },
        "deep_vs_shallow": {"shallow": shallow.to_dict(), "deep": deep.to_dict()},
        "verdict": verdict,
    }


# -- the whole integral -------------------------------------------------------
def run(src: str, cache_dir: str = CACHE, offline: bool = True) -> dict:
    t = _build(src, cache_dir, offline)
    fwd = run_forward(t)
    rules_all = t["bridges"] + t["gists"] + t["learned"]
    target = closure(_kb_with(t["base_kb"], rules_all)) - t["base"]
    ev = run_evidence(t, target)
    conn = run_connection()

    ladder = [0.0] + list(ev["evidence"]["losses"])
    area = loss_integral(sorted(ladder))
    verdict = {}
    for d in (fwd["verdict"], ev["verdict"], conn["verdict"]):
        verdict.update(d)
    verdict["loss_integral_finite"] = area == area and area >= 0.0
    return {"forward": fwd, "evidence": ev, "connection": conn,
            "loss_integral": round(area, 6), "verdict": verdict}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="the three integral layers of deduction")
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "integral"))
    args, _ = ap.parse_known_args(argv)

    src = open(args.local or NORTH_STAR_SRC, "r", encoding="utf-8").read()
    result = run(src, cache_dir=args.cache, offline=args.offline)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    f = result["forward"]
    e = result["evidence"]["evidence"]
    c = result["connection"]
    print(f"A forward : base={f['base_facts']} derived={f['derived']} target={f['target']} "
          f"debt(full)={len(f['full']['debt'])} debt(no_learned)={len(f['ablated']['debt'])} "
          f"sound={f['full']['sound']}")
    print(f"B evidence: log_Z={e['log_z']} F={e['free_energy']} MAP={e['map_name']} "
          f"reward={e['multiplicity_reward']:.3g} twin_reward={result['evidence']['twin']['multiplicity_reward']:.3g} "
          f"loss_integral={result['loss_integral']}")
    print(f"C connect : holonomy={c['field']} block={c['block_circulation']} "
          f"order_changes_result={c['verdict']['order_changes_result']}")
    print(f"verdict : {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())