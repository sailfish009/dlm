"""North-star vertical slice: acquire -> learn -> understand -> IR-TREE -> reading.

Reads the PyTorch MNIST example, REDUCES it to function-free Horn facts, LEARNS
the transitive ``calls`` rule from the reduction itself, derives an understanding
set through the trusted kernel, emits it as an IR *form* (IR-TREE), and glosses it
into a **leveled natural-language reading** (N1..N9) -- each sentence carrying the
atoms that entail it, checked against the kernel closure.  Where the reduction
captured nothing, there is no sentence.

v0.0053 INTEGRATES the reading into the body.  Before this version the body used a
private flat realizer (``realize.py``) and the leveled reading (gist, causal 'why',
certified absences) lived only in a side experiment, so the body's own final output
never reached the purpose sentence.  Now the body and the falsifier experiment share
one pipeline (this module): the body's ``narrative`` IS the N1..N9 reading, built
over structure + acquired ``meaning`` + SEARCHED ``dataset_of`` + acquired
``api_effect`` + the closed-world/equality absence layer.  One realizer, one path.
"""
from __future__ import annotations

import argparse
import json
import os
import time

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.abstract import abstract_theory
from dlm.closedworld import CANDIDATE_LAYERS, candidate_facts
from dlm.equality import (absence_rule_equality, same_kind_facts, symbols_in,
                          uses_layer_rules)
from dlm.gist import external_holes, gist_rules
from dlm.ground import Ground, learn
from dlm.lisp import atom_to_form, dump, form_to_rule, rule_to_form
from dlm.agent import (Reader, astr, atom_of, induce_transitive,
                       transitive_closure)
from dlm.narrative import (LEVELS, analyze_sentences, reading, reading_level,
                           reading_score)
from dlm.proof import proof_ir, proof_size, prove, verify

try:
    from .acquire import URL, acquire
    from .api_semantics import api_effect_facts, direct_explains
    from .domain import (DOMAIN_VOCAB, DOMAIN_VERSION, ENTITY_PHRASES)
    from .extract import extract
    from .knowledge import KNOWLEDGE_VERSION, SYMBOL_VOCAB
    from .semantics import bridge_forms, meaning_forms
    from .semantics import UNDERSTANDING  # noqa: F401  (re-exported for callers)
    from .signature import build_signature
except ImportError:  # direct `python experiments/mnist/run.py`
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mnist.acquire import URL, acquire
    from mnist.api_semantics import api_effect_facts, direct_explains
    from mnist.domain import (DOMAIN_VOCAB, DOMAIN_VERSION, ENTITY_PHRASES)
    from mnist.extract import extract
    from mnist.knowledge import KNOWLEDGE_VERSION, SYMBOL_VOCAB
    from mnist.semantics import bridge_forms, meaning_forms
    from mnist.semantics import UNDERSTANDING  # noqa: F401
    from mnist.signature import build_signature

KNOWLEDGE_CACHE = os.path.join(os.path.dirname(__file__), "cache")

CALLS = Rule(Atom("calls", (Var("?x"), Var("?z"))),
             (Atom("calls", (Var("?x"), Var("?y"))), Atom("calls", (Var("?y"), Var("?z")))))

# The reduction's own vocabulary: the learner induces laws over STRUCTURE only.
# The acquired ``meaning`` facts (and the understanding predicates they derive)
# are built for interpretation; letting them into the body search yields
# in-sample-coincidental rules (e.g. ``backpropagates`` in a transitive-calls
# body), so the structural law is induced over the reduction vocabulary alone.
STRUCTURAL = frozenset({"imports", "defines", "method_of", "inherits",
                        "creates", "calls", "step_of", "before"})
STRUCT_GROUND = Ground(())


def transitive(atoms: set) -> set:
    return transitive_closure(set(atoms), "calls")


def negatives(closed_calls: set, universe: list, limit=None) -> list:
    have = {(a.args[0].name, a.args[1].name) for a in closed_calls}
    out = []
    for x in universe:
        for z in universe:
            if x == z or (x, z) in have:
                continue
            out.append(Atom("calls", (Const(x), Const(z))))
            if limit is not None and len(out) >= limit:
                return out
    return out


def _learn_calls(base: set):
    """Induce the structural ``calls`` law over ``base`` (one learning pass)."""
    return induce_transitive(base, STRUCTURAL, pred="calls",
                             max_body=2, extra_vars=2, max_rules=4)


def _kb_with(base: set, res, *, close_world: bool) -> KnowledgeBase:
    """Build the understanding KB: bridges + gist + induced law (+ D5/D7a absence)."""
    kb = KnowledgeBase(base)
    for f in bridge_forms():
        kb.add_rule(form_to_rule(f))
    for r in gist_rules():
        kb.add_rule(r)
    for r in res.experience.rules:
        kb.add_rule(r)
    if close_world:
        kb.add_facts(candidate_facts())
        kb.add_facts(same_kind_facts(symbols_in(kb.facts)))
        for r in uses_layer_rules():
            kb.add_rule(r)
        kb.add_rule(absence_rule_equality())
    return kb


def closed_for(base: set, *, sig=None, close_world: bool = False) -> set:
    """Induce the calls law, apply bridge + gist (+ absence) rules, close.

    ``close_world`` adds the D5 closed-world ``absent`` rule over the GIVEN
    candidate universe (through the D7a equality bridge, so aliases are not
    falsely absent).  ``sig`` (a typed/moded :class:`~dlm.Signature`) makes the
    kernel check the theory statically first: an ill-typed theory raises
    ``TypeError`` instead of deriving anything.
    """
    res, _ = _learn_calls(base)
    kb = _kb_with(base, res, close_world=close_world)
    return closure(kb, sig) if sig is not None else closure(kb)


def causal_atoms(base: set) -> set:
    """Acquired ``api_effect`` facts + ``explains`` for DIRECT calls only."""
    direct = [(a.args[0].name, a.args[1].name) for a in base if a.pred == "calls"]
    atoms = {atom_of(f) for f in api_effect_facts()}
    atoms |= {atom_of(f) for f in direct_explains(direct)}
    return atoms


# The MODEL's autonomous reader, configured with the GIVEN PyTorch vocabulary.
# The experiment supplies only the reducer + bridge/gist rules + cue lexicons;
# the loop itself (web acquisition, induction, closure, reading) is in dlm.
READER = Reader(
    perceive=extract,
    symbol_vocab=SYMBOL_VOCAB,
    entity_vocab=DOMAIN_VOCAB,
    bridges=bridge_forms,
    gists=gist_rules,
    structural=tuple(sorted(STRUCTURAL)),
    signature_builder=build_signature,
    causal=causal_atoms,
    entity_phrases=ENTITY_PHRASES,
    law_pred="calls",
    symbol_version=KNOWLEDGE_VERSION,
    domain_version=DOMAIN_VERSION,
)


def pipeline(src: str, module: str = "main", cache_dir: str = KNOWLEDGE_CACHE,
             offline: bool = True, knowledge: dict = None, domain: dict = None) -> dict:
    """The ONE integrated path, now driven by the MODEL's autonomous reader.

    ``dlm.agent.Reader`` owns the loop (perceive -> acquire -> search -> induce ->
    close -> read); this function only supplies the GIVEN PyTorch vocabulary via
    the module-level :data:`READER`.  Shared by the north-star body (:func:`run`)
    and the falsifier experiment (``experiments/reading``).
    """
    return READER.run(src, module=module, cache_dir=cache_dir, offline=offline,
                      knowledge=knowledge, domain=domain)


def law_transfer(base: set) -> dict:
    """Can the general call law be induced from ONE file?  Hold out each owner.

    All multi-hop ``calls`` pairs in a single small file share the entry point
    (``main``), so restricting to any train split leaves no non-trivial positive
    to generalize from.  This is the honest reason the general law is learned
    across repos (``experiments/code``) and merely APPLIED here.
    """
    calls = {a for a in base if a.pred == "calls"}
    pos_all = transitive(calls)
    universe = sorted({t.name for a in calls for t in a.args})
    negs = negatives(pos_all, universe)
    struct = {a for a in base if a.pred in STRUCTURAL}
    owners = sorted({a.args[0].name for a in calls})
    out = {}
    testable = False
    for held in owners:
        train = {a.args[0].name for a in calls if a.args[0].name != held}
        held_pos = {p for p in pos_all if p.args[0].name == held and p not in base}
        nondirect = {p for p in pos_all if p.args[0].name in train and p not in base}
        if held_pos:
            testable = True
        if not held_pos:
            out[held] = {"status": "not_testable", "held_nondirect": 0}
            continue
        if not nondirect:
            out[held] = {"status": "no_multi_hop_train_examples",
                         "held_nondirect": len(held_pos)}
            continue
        res = learn(STRUCT_GROUND, struct, [p for p in pos_all if p.args[0].name in train], negs,
                    max_body=2, extra_vars=2, max_rules=3)
        out[held] = {"status": "learned", "rules": len(res.experience.rules),
                     "held_covered": len({p for p in held_pos if p in res.covered}),
                     "held_nondirect": len(held_pos)}
    return {"per_held_owner": out,
            "general_law_identifiable_from_one_file":
                testable and any(v.get("status") == "learned" and v["held_nondirect"] > 0
                                 for v in out.values())}


def run(src: str, source: str = URL, module: str = "main",
        cache_dir: str = KNOWLEDGE_CACHE, offline: bool = True,
        knowledge: dict = None, domain: dict = None) -> dict:
    p = pipeline(src, module=module, cache_dir=cache_dir, offline=offline,
                 knowledge=knowledge, domain=domain)
    labels, pipelines = p["labels"], p["pipelines"]
    base, closed = p["base"], p["closed"]
    knowledge, meanings = p["knowledge"], p["meanings"]
    res, positives = p["res"], p["positives"]
    ground = Ground(tuple(form_to_rule(f) for f in bridge_forms()))

    derived_calls = {a for a in closed if a.pred == "calls"}
    false_final = sorted(astr(a) for a in derived_calls - positives)

    # the body's final natural-language output IS the leveled reading
    sentences = p["sentences"]

    target = Atom("calls", (Const(module), Const("loss_backward")))
    pr = prove(p["kb"], target) if target in closed else None
    proof = None if pr is None else {
        "atom": astr(target), "size": proof_size(pr), "verified": verify(pr, p["kb"]),
        "ir": dump(proof_ir(pr)),
    }

    trains = Atom("trains", (Const("train"),))
    p2 = prove(p["kb"], trains) if trains in closed else None
    ground_proof = None if p2 is None else {
        "atom": astr(trains), "size": proof_size(p2), "verified": verify(p2, p["kb"]),
        "ir": dump(proof_ir(p2)),
    }

    abs_res = abstract_theory(tuple(ground.rules) + tuple(res.experience.rules), closed)
    law = law_transfer(base)

    hidden = ("calls", "step_of", "before", "creates")
    ir = ("understanding",
          ("source", source),
          ("module", module),
          ("knowledge", *[atom_to_form(atom_of(f)) for f in meaning_forms(meanings)]),
          ("domain", *[atom_to_form(atom_of(f)) for f in p["dfacts_list"]]),
          ("facts", *[atom_to_form(a) for a in sorted(base, key=astr)]),
          ("ground", *[rule_to_form(r) for r in ground.rules]),
          ("learned", *[rule_to_form(r) for r in res.experience.rules]),
          ("derived", *[atom_to_form(a) for a in sorted(closed, key=astr)
                        if a.pred not in hidden]))

    level = reading_level(sentences)
    produced = {f"N{n}_{name}": any(s["level"] == n and s["certified"] for s in sentences)
                for n, name in LEVELS.items()}
    purpose = [s["text"] for s in sentences if s["level"] == 7]
    absences = [s["text"] for s in sentences if s["level"] == 9]
    return {
        "source": source,
        "module": module,
        "counts": {"facts": len(base), "calls_closure": len(positives),
                   "learned_rules": len(res.experience.rules),
                   "derived_atoms": len(closed)},
        "knowledge": {
            "stats": knowledge["stats"],
            "meanings": meanings,
            "records": [
                {"label": r["label"], "entry": r["entry"], "resolution": r["resolution"],
                 "concept": r["concept"], "url": r["url"], "definition": r["definition"],
                 "providers": r.get("providers", [])}
                for r in knowledge["records"]
            ],
        },
        "domain": {"entities": p["entities"],
                   "stats": p["domain"].get("stats", {}) if isinstance(p["domain"], dict) else {},
                   "holes": p["holes"]},
        "learned": [astr(r.head) + " :- " + ", ".join(astr(b) for b in r.body)
                    for r in res.experience.rules],
        "false_assert": len(res.false_assert),
        "false_final": false_final[:50],
        "false_final_count": len(false_final),
        "law_transfer": law,
        "ir": dump(ir),
        "narrative": sentences,
        "sentences": sentences,
        "sentence_analysis": p["sentence_analysis"],
        "reading_level": level,
        "reading_level_name": LEVELS.get(level, "none"),
        "reading_score": reading_score(sentences),
        "levels_present": produced,
        "purpose_sentences": purpose,
        "absence_sentences": absences,
        "northstar_purpose": any("recognize" in s for s in purpose),
        "all_sentences_verified": all(s["certified"] for s in sentences) and bool(sentences),
        "proof": proof,
        "ground_proof": ground_proof,
        "abstract": {"dl_before": abs_res.dl_before, "dl_after": abs_res.dl_after,
                     "gain": abs_res.compression_gain,
                     "invented": [a.name for a in abs_res.abstractions]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="MNIST north-star vertical slice")
    ap.add_argument("--url", default=URL)
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=os.path.join(os.path.dirname(__file__), "cache"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "reports", "mnist"))
    args = ap.parse_args(argv)

    src = acquire(args.url, cache_dir=args.cache, offline=args.offline, local=args.local)
    result = run(src, args.url, cache_dir=args.cache, offline=args.offline)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"source  : {result['source']}")
    kstats = result["knowledge"]["stats"]
    print(f"knowledge: {kstats['acquired']}/{kstats['candidates']} symbols acquired "
          f"({kstats['fetched_new']} new, offline={kstats['offline']}); "
          f"meanings={result['knowledge']['meanings']}")
    print(f"domain  : {result['domain']['entities']}  {result['domain']['stats']}")
    print(f"counts  : {result['counts']}  false={result['false_assert']} "
          f"false_final={result['false_final_count']}")
    print(f"learned : {result['learned']}")
    print(f"law     : general_law_identifiable_from_one_file="
          f"{result['law_transfer']['general_law_identifiable_from_one_file']} "
          f"(see experiments/code for the cross-repo law)")
    print(f"proof   : {result['proof'] and result['proof']['atom']} "
          f"size={result['proof'] and result['proof']['size']} "
          f"verified={result['proof'] and result['proof']['verified']}")
    print(f"abstract: DL {result['abstract']['dl_before']} -> {result['abstract']['dl_after']} "
          f"(gain {result['abstract']['gain']}, invented {result['abstract']['invented']})")
    print(f"reading : level N{result['reading_level']} ({result['reading_level_name']})  "
          f"score {result['reading_score']}")
    print("\n--- leveled reading (N1..N9, each line backed by kernel facts) ---")
    for s in result["narrative"]:
        mark = "ok " if s["certified"] else "?? "
        print(f"  {mark}N{s['level']} {s['kind']:<12} {s['text']}")
    sa = result["sentence_analysis"]
    print(f"\nsentences={sa['sentence_count']} certified={sa['certified']} "
          f"by level={sa['by_level']}")
    print(f"purpose : {result['purpose_sentences']}")
    print(f"absent  : {result['absence_sentences']}")
    print(f"all_sentences_verified = {result['all_sentences_verified']}")
    print(f"report: {os.path.join(out_dir, 'result.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())