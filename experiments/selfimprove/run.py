"""Self-evaluation + weakness-targeted curriculum experiment (v0.0056).

The model is NOT told what to look for.  It reads its own ability off the kernel
closure, finds the deduction target it cannot yet conclude, asks the web only for
the premise it lacks, re-closes, re-assesses, and stops on a named reason.  This
is the closed loop the model was missing: web access and self-supervision living
*inside* the model (:mod:`dlm.ability`, :mod:`dlm.curriculum`,
:mod:`dlm.agent`'s ``Reader.self_improve``).

The north-star slice instantiates it: the reader proves ``trains`` (the program
trains) but CANNOT prove ``recognizes(<program>, <what>)`` because ``dataset_of``
(what the dataset contains) is neither in the code nor in a symbol's definition.
The model discovers that gap itself and searches for it.

Falsifiers (verdict dict, all must hold):
  weakness_identified    the model itself finds an open target with an acquirable gap
  improvement_from_web   after ONE self-directed acquisition the target is proved
  web_target_resolved    no actionable weak spot remains afterwards
  targets_unrestricted   the target set is DISCOVERED from the theory (not a fixed list)
  scramble_no_gain       a scrambled acquisition (wrong fact) improves nothing
  no_web_abstains        with acquisition removed the loop abstains, invents nothing
  stop_named             the loop halts on a named reason
  deterministic          two runs are byte-identical

Writes reports/selfimprove/<stamp>/result.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_EXP = os.path.dirname(_HERE)
if _EXP not in sys.path:
    sys.path.insert(0, _EXP)

from dlm.ability import weak_spots
from dlm.curriculum import run_curriculum
from dlm.gist import EXTERNAL_PREDICATES, GIST_GOALS
from dlm import Atom, Const, Rule, Var

from mnist.acquire import URL
from mnist.domain import acquire_domain, domain_facts
from mnist.run import KNOWLEDGE_CACHE, pipeline

CACHE = KNOWLEDGE_CACHE


def reader_result(src: str, *, cache_dir: str = CACHE, offline: bool = True) -> dict:
    """Run the model with NO domain knowledge: the hole is real, not staged."""
    return pipeline(src, module="main", cache_dir=cache_dir, offline=offline,
                    domain={})


def synthetic_multi() -> dict:
    """A theory with THREE independent weak spots, to prove the loop ITERATES.

    The model is given only the seed fact; the three targets each lack one
    externally-acquirable premise.  It must discover all three gaps, resolve them
    one per round, and stop when no weak spot is left -- not because it was told
    how many there were.
    """
    def target(i):
        return f"proved_{i}"

    def prem(i):
        return f"have_{i}"

    rules = tuple(
        Rule(Atom(target(i), (Var("?x"),)),
             (Atom(prem(i), (Var("?x"),)), Atom("seed", (Var("?x"),))))
        for i in range(3))
    facts = {Atom("seed", (Const("s"),))}
    external = {prem(i) for i in range(3)}

    def acquire(spot):
        p = spot.external[0] if spot.external else (spot.missing[0] if spot.missing else "?")
        return {"facts": [Atom(p, (Const("s"),))], "query": f"supply {p}",
                "provenance": {"synthetic": True, "predicate": p}}

    def scrambled(spot):
        p = spot.external[0] if spot.external else "?"
        return {"facts": [Atom(p, (Const("WRONG"),))], "query": f"scramble {p}",
                "provenance": {"synthetic": True, "scrambled": True}}

    r = run_curriculum(facts, rules, acquire=acquire, external=external, max_rounds=8)
    scr = run_curriculum(facts, rules, acquire=scrambled, external=external,
                         max_rounds=8)
    gained = [g for rd in r.rounds for g in rd.gained]
    scr_gained = [g for rd in scr.rounds for g in rd.gained]
    return {
        "targets": list(r.ability_before.targets),
        "actionable_before": list(r.ability_before.actionable),
        "rounds": [rd.to_dict() for rd in r.rounds],
        "stop": r.stop,
        "proved_after": [t for t in r.ability_after.targets if r.ability_after.is_proved(t)],
        "open_after": list(r.ability_after.open),
        "gained": gained,
        "scramble_stop": scr.stop,
        "scramble_gained": scr_gained,
        "ok": (r.stop == "saturated" and len(r.rounds) == 3
               and all(r.ability_after.is_proved(target(i)) for i in range(3))
               and gained == [target(i) for i in range(3)]
               and not any(scr.ability_after.is_proved(target(i)) for i in range(3))
               and not scr_gained),
    }


def web_acquire(p: dict, *, scramble: bool = False, offline: bool = True):
    """The model's ONLY side-effecting seam: search the web for the missing premise.

    It asks for the dataset the program instantiates (the weak spot), reduces the
    fetched prose to a domain entity, and returns it WITH provenance.  When asked
    to scramble it returns a wrong fact, to prove that improvement is caused by the
    CONTENT and re-checked by the kernel -- not by the act of acquiring.
    """
    holes = list(p["holes"])
    cands = p["cands"]

    def acquire(spot):
        if not spot.external:
            return {}
        if not holes:
            return {"facts": [], "provenance": {"reason": "no_hole"}}
        if scramble:
            decoy = ("dataset_of", f"not_{holes[0]}", "handwritten_digit")
            return {"facts": [decoy], "query": "scrambled",
                    "provenance": {"provider": "scramble", "slugs": [holes[0]],
                                   "scrambled": True}}
        dom = acquire_domain({h: cands[h] for h in holes}, CACHE, offline=offline)
        entities = dom.get("entities", {})
        facts = [tuple(f) for f in domain_facts(entities)]
        recs = {r.get("slug"): r for r in dom.get("records", [])}
        prov = {
            "provider": "wikipedia+stackoverflow",
            "offline": offline,
            "slugs": sorted(entities),
            "records": [
                {"slug": slug, "concept": ent,
                 "resolution": (recs.get(slug) or {}).get("entity"),
                 "url": ((recs.get(slug) or {}).get("wikipedia") or {}).get("url"),
                 "providers": (recs.get(slug) or {}).get("providers", [])}
                for slug, ent in sorted(entities.items())
            ],
        }
        return {"facts": facts, "query": f"what does dataset {holes[0]} contain",
                "provenance": prov}

    return acquire


def run(src: str, *, cache_dir: str = CACHE, offline: bool = True) -> dict:
    p = reader_result(src, cache_dir=cache_dir, offline=offline)

    web = web_acquire(p, offline=offline)
    result = run_curriculum(p["base"], READER_RULES(p), acquire=web,
                            external=EXTERNAL_PREDICATES, max_rounds=6)

    # controls: same loop, acquisition scrambled / removed
    scr = run_curriculum(p["base"], READER_RULES(p),
                         acquire=web_acquire(p, scramble=True, offline=offline),
                         external=EXTERNAL_PREDICATES, max_rounds=6)
    none = run_curriculum(p["base"], READER_RULES(p), acquire=lambda spot: {},
                          external=EXTERNAL_PREDICATES, max_rounds=6)

    after = result.ability_after
    before = result.ability_before
    multi = synthetic_multi()
    verdicts = {
        "weakness_identified": bool(before.actionable),
        "improvement_from_web": after.is_proved("recognizes"),
        "web_target_resolved": not after.actionable,
        "targets_unrestricted": (len(after.targets) >= 4
                                 and bool(set(after.targets) - set(GIST_GOALS))),
        "scramble_no_gain": (not scr.ability_after.is_proved("recognizes")
                             and not scr.rounds[0].improved),
        "no_web_abstains": (none.stop == "acquire_empty"
                            and not none.ability_after.is_proved("recognizes")),
        "stop_named": result.stop in ("saturated", "no_actionable",
                                      "acquire_empty", "no_progress", "max_rounds"),
        "multi_round_self_improvement": multi["ok"],
        "deterministic": (run_curriculum(p["base"], READER_RULES(p), acquire=web,
                                         external=EXTERNAL_PREDICATES, max_rounds=6)
                          .to_dict() == result.to_dict()),
    }
    return {
        "source": src,
        "targets": list(before.targets),
        "weak_spots_before": [s.to_dict() for s in weak_spots(before)],
        "actionable_before": list(before.actionable),
        "stop": result.stop,
        "rounds": [r.to_dict() for r in result.rounds],
        "ability_before": before.to_dict(),
        "ability_after": after.to_dict(),
        "controls": {"scramble_stop": scr.stop,
                     "scramble_improved": scr.rounds[0].improved if scr.rounds else False,
                     "no_web_stop": none.stop,
                     "no_web_facts": len(none.facts)},
        "multi_round": multi,
        "verdict": verdicts,
        "verdict_ok": all(verdicts.values()),
    }


# The experiment supplies only the GIVEN, domain-specific pieces; the theory is
# the model's own (bridges + gists + the induced calls law).  Built here from the
# reader configuration so `dlm` keeps importing no experiment module.
def READER_RULES(p: dict) -> tuple:
    from mnist.run import READER
    return READER.rules_for(p)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="self-evaluation + weak-spot curriculum")
    ap.add_argument("--url", default=URL)
    ap.add_argument("--local", default="")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--offline", action="store_true",
                    help="accepted for harness parity; replay is always offline")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(__file__), "..", "..", "reports", "selfimprove"))
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)

    src = args.local if args.local else args.url
    if not os.path.exists(os.path.expanduser(src)):
        from mnist.acquire import acquire as fetch
        src = fetch(args.url, cache_dir=args.cache, offline=True, local=args.local)

    result = run(src, cache_dir=args.cache, offline=True)
    out = {"version": "0.0.56", "result": result}

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    path = os.path.abspath(args.json) if args.json else os.path.join(out_dir, "result.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    print(f"targets discovered: {result['targets']}")
    print(f"actionable weak spots before: {result['actionable_before']}")
    for w in result["weak_spots_before"]:
        mark = "*" if w["actionable"] else " "
        print(f"  {mark} {w['kind']:<8} {w['target']:<16} missing={w['missing']} "
              f"external={w['external']}")
    for r in result["rounds"]:
        ws = r["weak_spot"]
        print(f"  round {r['round']}: {ws['target']} <- [{ws['query']}] "
              f"acquired={r['acquired']} improved={r['improved']} "
              f"gained={r['gained']} stop={r['stop']}")
    print(f"ability : {len(result['ability_before']['proved'])} proved, "
          f"{len(result['ability_before']['open'])} open -> "
          f"{len(result['ability_after']['proved'])} proved, "
          f"{len(result['ability_after']['open'])} open")
    print(f"controls: {result['controls']}")
    m = result["multi_round"]
    print(f"multi-round: {len(m['rounds'])} rounds, gained={m['gained']}, "
          f"stop={m['stop']}, open_after={m['open_after']}, "
          f"scramble_stop={m['scramble_stop']} -> {'ok' if m['ok'] else 'FAIL'}")
    print(f"stop    : {result['stop']}")
    print(f"verdict : {result['verdict']}")
    print(f"self-evaluation + weak-spot curriculum: "
          f"{'PASS' if result['verdict_ok'] else 'FAIL'}")
    print(f"report: {path}")
    return 0 if result["verdict_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())