"""Experiments/typed -- D6: typed/moded signatures (offline).

The north-star path reads a program and knows a lot *empirically*: the learner
samples candidate rules and keeps the ones the kernel cannot refute.  That gate
is sound but blind to the SHAPE of a clause.  This stage closes that gap: the
kernel now checks a theory against a typed/moded :class:`~dlm.Signature` BEFORE
any derivations, so an inadmissible rule is rejected rather than tested.

What is measured here:

* every rule the line already uses (bridge, gist, the learned ``calls`` law, the
  closed-world ``absent`` rule) passes the signature -- typing adds no false
  rejections;
* seven *adversarial* clauses (unknown predicate, arity mismatch, type clash,
  constant outside its type, head variable bound by no body literal, unbound
  negated variable, input never produced) are each rejected statically;
* typing is honest -- it only *forbids*: for the honest theory the closure under
  the signature is byte-for-byte the closure without it, and the same gist and
  absences are derived;
* typing prunes the candidate space: among candidates that the existing
  head-binding filter would already test, a nontrivial number are rejected on
  type/mode grounds before the kernel is ever asked.

Nothing here asserts a fact: the signature gates admission, the kernel still
decides truth.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure, type_errors

HERE = os.path.dirname(os.path.abspath(__file__))

try:
    from dlm.closedworld import candidate_facts
    from dlm.gist import gist_rules
    from dlm.ground import Ground, learn
    from dlm.lisp import form_to_rule
    from ..mnist.domain import (ENTITY_PHRASES, acquire_domain, dataset_candidates,
                                domain_facts)
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import (STRUCTURAL, STRUCT_GROUND, atom_of, negatives,
                             transitive)
    from ..mnist.semantics import bridge_forms
    from ..mnist.signature import (absence_rule_typed, adversarial, build_signature,
                                   SIGNATURE_ARGS)
except ImportError:  # direct `python experiments/typed/run.py`
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from dlm import Const, KnowledgeBase, Rule, Var, closure, type_errors
    from dlm.closedworld import candidate_facts
    from dlm.gist import gist_rules
    from dlm.ground import Ground, learn
    from dlm.lisp import form_to_rule
    from mnist.domain import (ENTITY_PHRASES, acquire_domain, dataset_candidates,
                              domain_facts)
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import (STRUCTURAL, STRUCT_GROUND, atom_of, negatives,
                           transitive)
    from mnist.semantics import bridge_forms
    from mnist.signature import (absence_rule_typed, adversarial, build_signature,
                                 SIGNATURE_ARGS)

CACHE = os.path.join(HERE, "..", "mnist", "cache")
NORTH_STAR_SRC = os.path.join(CACHE, "main.py")

# Predicates the candidate-space probe enumerates over (observed structure).
ENUM_PREDS = ("imports", "defines", "method_of", "inherits", "creates", "calls",
              "step_of", "before")


def _learned_rules(base: set):
    """Reproduce the ``calls`` law the reader induces (so it too is type-checked)."""
    calls = {a for a in base if a.pred == "calls"}
    positives = transitive(calls)
    universe = sorted({t.name for a in calls for t in a.args})
    negs = negatives(positives, universe)
    struct = {a for a in base if a.pred in STRUCTURAL}
    res = learn(STRUCT_GROUND, struct, positives, negs,
                max_body=2, extra_vars=2, max_rules=4)
    return tuple(res.experience.rules)


def _candidate_pruning(sig) -> dict:
    """How many arity-valid clauses does typing reject that head-binding would test?"""
    vars_ = [Var("?x"), Var("?y"), Var("?z")]
    literals = [Atom(p, (a, b)) for p in ENUM_PREDS for a, b in itertools.product(vars_, repeat=2)]
    heads = [Atom(p, (a, b)) for p in ENUM_PREDS for a, b in itertools.product(vars_, repeat=2)]
    bodies = [ (lit,) for lit in literals ]
    bodies += list(itertools.combinations(literals, 2))
    total = head_bound = typed_ok = new_reject = 0
    for head in heads:
        hv = {t.name for t in head.args if isinstance(t, Var)}
        for body in bodies:
            bv = {t.name for lit in body for t in lit.args if isinstance(t, Var)}
            total += 1
            if not hv <= bv:
                continue  # already dropped by the learner's head-binding filter
            head_bound += 1
            if not type_errors(Rule(head, tuple(body)), sig):
                typed_ok += 1
            else:
                new_reject += 1
    return {"candidates": total, "head_bound": head_bound, "typed_ok": typed_ok,
            "type_rejected_but_head_bound": new_reject}


def run(src: str, module: str = "main", cache_dir: str = CACHE,
        offline: bool = True, knowledge: dict = None, domain: dict = None) -> dict:
    ext = extract(src, module)
    labels = ext["labels"]
    facts = [tuple(f) for f in ext["facts"]]
    if knowledge is None:
        knowledge = acquire_knowledge(ext["facts"], labels, cache_dir=cache_dir,
                                      offline=offline)
    meanings = knowledge["meanings"]

    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(meanings)}
    base |= set(candidate_facts())

    # SEARCH for the acquired domain premise (dataset contents).
    cands = dataset_candidates(facts, labels)
    from dlm.gist import external_holes
    holes = external_holes(facts, cands)
    if domain is None:
        domain = acquire_domain({h: cands[h] for h in holes}, cache_dir=cache_dir,
                                offline=offline)
    entities = domain.get("entities", {}) if isinstance(domain, dict) else dict(domain)
    dfacts = [atom_of(f) for f in domain_facts(entities)]
    base |= set(dfacts)

    sig = build_signature(meanings, [tuple(f) for f in domain_facts(entities)])

    honest_rules = (tuple(form_to_rule(f) for f in bridge_forms())
                    + gist_rules() + _learned_rules(base) + (absence_rule_typed(),))
    rule_checks = {r.name or f"{r.head.pred}/{len(r.head.args)}": list(type_errors(r, sig))
                   for r in honest_rules}
    all_rules_type_check = all(not v for v in rule_checks.values())

    adv = adversarial()
    adv_results = []
    for name, rule, needle in adv:
        errs = type_errors(rule, sig)
        adv_results.append({"name": name, "errors": list(errs),
                            "rejected": bool(errs) and needle in " ".join(errs),
                            "expected": needle})
    all_adversarial_rejected = all(a["rejected"] for a in adv_results)
    # regression guard: naive arity checking alone would have accepted these
    arity_ok = [a for a in adv if a[2] != "arity"]

    kb = KnowledgeBase(base)
    for r in honest_rules:
        kb.add_rule(r)
    typed = closure(kb, sig)
    untyped = closure(kb)

    rejected = False
    reason = ""
    bad = kb.copy()
    bad.add_rule(adv[2][1])  # the type-clash rule
    try:
        closure(bad, sig)
    except TypeError as exc:
        rejected = True
        reason = str(exc)[:200]

    pruning = _candidate_pruning(sig)

    def has(pred, *names):
        return any(a.pred == pred and tuple(t.name for t in a.args) == names for a in typed)

    absents = sorted(a.args[1].name for a in typed if a.pred == "absent" and a.args[0].name == "net")
    verdict = {
        "all_rules_type_check": all_rules_type_check,
        "all_adversarial_rejected": all_adversarial_rejected,
        "typed_closure_admits_honest": bool(typed),
        "typed_closure_rejects_ill_typed": rejected,
        "typing_does_not_change_truth": typed == untyped,
        "recognizes_still_derived": has("recognizes", "main", "handwritten_digit"),
        "absences_still_derived": len(absents) >= 1,
        "typing_prunes_candidates": pruning["type_rejected_but_head_bound"] > 0,
        "modes_are_load_bearing": any(a["rejected"] for a in adv_results
                                      if a["name"] == "input_never_produced"),
    }
    return {
        "source": module,
        "counts": {"facts": len(base), "derived_atoms": len(typed),
                   "honest_rules": len(honest_rules)},
        "rule_checks": rule_checks,
        "adversarial": adv_results,
        "pruning": pruning,
        "rejection_reason": reason,
        "derived": {"absences": absents, "recognizes": has("recognizes", "main", "handwritten_digit")},
        "verdict": verdict,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="D6 typed/moded signatures (offline)")
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "typed"))
    args, _unknown = ap.parse_known_args(argv)

    src_path = args.local or NORTH_STAR_SRC
    src = open(src_path, "r", encoding="utf-8").read()
    result = run(src, cache_dir=args.cache, offline=args.offline)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"facts  : {result['counts']}")
    print("--- signature check on the line's own rules ---")
    for name, errs in result["rule_checks"].items():
        print(f"  {'ok ' if not errs else '!! '}{name}: {errs or 'type-safe'}")
    print("--- adversarial clauses (all must be rejected) ---")
    for a in result["adversarial"]:
        print(f"  {'ok ' if a['rejected'] else '!! '}{a['name']:<26} "
              f"-> {'; '.join(a['errors'])}")
    p = result["pruning"]
    print(f"pruning: {p['type_rejected_but_head_bound']}/{p['head_bound']} head-bound "
          f"candidates rejected on type/mode grounds (of {p['candidates']} arity-valid)")
    print(f"rejection: {result['rejection_reason']}")
    print(f"derived: {result['derived']}")
    print(f"verdict: {result['verdict']}")
    print(f"report : {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())