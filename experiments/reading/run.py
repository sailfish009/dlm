"""Experiments/reading -- the falsifier harness for the leveled reading (offline).

The north-star body (``experiments/mnist/run.py``) now emits the N1..N9 reading
itself (v0.0053 integration).  This experiment does not re-implement that pipeline:
it consumes the SAME ``mnist.run.pipeline`` and only adds the FALSIFIERS -- the
typed admission gate, the closed-world non-monotonicity probe, and the honesty
ablation -- so the reading's claims can be independently checked.

The reading ladder (N1..N9):
    N1 facts, N2 meanings, N3 idioms, N4 a NAMED gradient step,
    N5 the forward-pass architecture, N6 a certified "why" (from acquired
    ``api_effect`` facts + observed direct calls), N7 the purpose/gist (from the
    derived ``recognizes`` concept, which needs SEARCHED domain knowledge),
    N8 a structural analogy, N9 a certified ABSENCE -- derivable only by stratified
    closed-world negation (D5) over a GIVEN candidate universe and NON-MONOTONIC.

Typing (D6) is deliberately NOT a sentence level: the reader is closed with a
GIVEN typed/moded :class:`~dlm.Signature`, so an ill-typed theory makes it
ABSTAIN (raise) instead of deriving -- typing GATES admission, it never asserts.

The honesty test is built in: strip the acquired domain facts and the N7 gist
must disappear (the reader abstains), while everything the structure supports
stays.  Nothing is printed that the kernel closure does not entail.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from dlm import Atom, Const, KnowledgeBase, closure
from dlm.closedworld import CANDIDATE_LAYERS
from dlm.narrative import LEVELS, reading, reading_level, reading_score

try:
    from ..mnist.domain import ENTITY_PHRASES
    from ..mnist.run import closed_for, pipeline
    from ..mnist.signature import adversarial
except ImportError:  # direct `python experiments/reading/run.py`
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mnist.domain import ENTITY_PHRASES
    from mnist.run import closed_for, pipeline
    from mnist.signature import adversarial

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "mnist", "cache")
NORTH_STAR_SRC = os.path.join(CACHE, "main.py")


def run(src: str, module: str = "main", cache_dir: str = CACHE,
        offline: bool = True, knowledge: dict = None, domain: dict = None) -> dict:
    p = pipeline(src, module=module, cache_dir=cache_dir, offline=offline,
                 knowledge=knowledge, domain=domain)
    labels, pipelines = p["labels"], p["pipelines"]
    knowledge, meanings = p["knowledge"], p["meanings"]
    base, base_kb, closed = p["base"], p["base_kb"], p["closed"]
    causal, sig = p["causal"], p["sig"]
    entities = p["entities"]
    sentences = p["sentences"]
    sentence_analysis = p["sentence_analysis"]

    # HONESTY ABLATION: without the searched domain knowledge -> no gist.
    closed_ctrl = closed_for(base, sig=sig, close_world=True) | causal
    sents_ctrl = reading(closed_ctrl, labels, pipelines, module=module,
                         meanings=meanings, entity_phrases=ENTITY_PHRASES)
    abstains_without_domain = not any(s["level"] == 7 and "recognize" in s["text"]
                                      for s in sents_ctrl)

    # D6 typed admission GATE: an ill-typed rule makes the reader ABSTAIN (raise)
    # rather than derive from it; truth is never polluted by an inadmissible rule.
    bad = KnowledgeBase(base_kb)
    bad.add_rule(adversarial()[2][1])              # the type-clash clause
    try:
        closure(bad, sig)
        typed_gate_binds = False
    except TypeError:
        typed_gate_binds = True
    typed_equals_untyped = closed == (closed_for(base_kb, close_world=True) | causal)

    # D5 NON-MONOTONICITY in the reading: presenting a candidate layer retracts
    # its certified NEGATIVE sentence (pure Horn can never retract).
    neg_wo = closed_for(base_kb, sig=sig, close_world=False) | causal
    negative_needs_closed_world = not any(a.pred == "absent" for a in neg_wo)
    subjects = sorted(a.args[0].name for a in closed if a.pred == "is_module")
    net = subjects[0] if subjects else module
    used = sorted(a.args[1].name for a in closed
                  if a.pred == "uses_layer" and a.args[0].name == net)
    absent = sorted(a.args[1].name for a in closed
                    if a.pred == "absent" and a.args[0].name == net)
    probe_layer = next((l for l in CANDIDATE_LAYERS if l not in used), None)
    if probe_layer is None:
        retracted = True
    else:
        # The non-monotonicity is a property of the NEGATION layer, so probe it
        # UNTYPED: the D6 signature would reject an unknown candidate name as a
        # non-layer, which is orthogonal to the retraction being tested.
        base_probe = base_kb | {Atom("has_layer", (Const(net), Const(probe_layer)))}
        sents_probe = reading(closed_for(base_probe, close_world=True) | causal,
                              labels, pipelines, module=module, meanings=meanings,
                              entity_phrases=ENTITY_PHRASES)
        retracted = not any(s["level"] == 9 and f" {probe_layer} layer" in s["text"]
                            for s in sents_probe)

    level = reading_level(sentences)
    score = reading_score(sentences)
    produced = {f"N{n}_{name}": any(s["level"] == n and s["certified"] for s in sentences)
                for n, name in LEVELS.items()}
    verdict = {
        "all_sentences_certified": all(s["certified"] for s in sentences) and bool(sentences),
        "named_composition_step": produced["N4_composition"],
        "architecture_topology": produced["N5_architecture"],
        "causal_why": produced["N6_causal"],
        "purpose_gist": produced["N7_purpose"],
        "analogy_sentence": produced["N8_analogy"],
        "negative_absence_sentence": produced["N9_absence"],
        "negative_needs_closed_world": negative_needs_closed_world,
        "nonmonotonic_negative_retracts": retracted,
        "equality_absence_sound": all(l not in used for l in absent),
        "equality_blocks_functional_absence": ("maxpool2d" in used
                                               and "maxpool2d" not in absent),
        "congruence_present": any(a.pred == "same_kind" for a in closed),
        "typed_gate_binds": typed_gate_binds,
        "typing_does_not_change_truth": typed_equals_untyped,
        "abstains_without_domain": abstains_without_domain,
        "reading_level_at_least_7": level >= 7,
        "reading_level_at_least_8": level >= 8,
        "reading_level_at_least_9": level >= 9,
        "reading_score_at_least_half": score >= 0.5,
    }
    return {
        "source": module,
        "counts": {"facts": len(base), "derived_atoms": len(closed)},
        "absences": sorted(a.args[1].name for a in closed
                           if a.pred == "absent" and a.args[0].name == net),
        "used_layers": used,
        "domain": {"entities": entities,
                   "stats": p["domain"].get("stats", {}) if isinstance(p["domain"], dict) else {}},
        "reading_level": level,
        "reading_level_name": LEVELS.get(level, "none"),
        "reading_score": score,
        "levels_present": produced,
        "sentences": sentences,
        "sentence_analysis": sentence_analysis,
        "all_sentences_certified": verdict["all_sentences_certified"],
        "ablation_without_domain": [s["text"] for s in sents_ctrl if s["level"] == 7],
        "verdict": verdict,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="leveled final NL reading of a program")
    ap.add_argument("--local", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "reading"))
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

    print(f"facts   : {result['counts']['facts']} base, {result['counts']['derived_atoms']} derived")
    print(f"domain  : {result['domain']['entities']}  {result['domain']['stats']}")
    print(f"reading : level N{result['reading_level']} ({result['reading_level_name']})  "
          f"score {result['reading_score']}")
    print("--- leveled reading (each line backed by kernel facts) ---")
    for s in result["sentences"]:
        mark = "ok " if s["certified"] else "?? "
        print(f"  {mark}N{s['level']} {s['kind']:<12} {s['text']}")
    sa = result["sentence_analysis"]
    print("--- sentence analysis (presentation reach vs deduction content) ---")
    print(f"  sentences={sa['sentence_count']} certified={sa['certified']} "
          f"support_atoms={sa['distinct_support_atoms']} "
          f"mean_support={sa['mean_support_size']}")
    print(f"  by level : {sa['by_level']}")
    print(f"  rung kind: " + "; ".join(f"N{n}={sa['rung_kind'][n]}" for n in sa["levels_present"]))
    print(f"  presentation-only={sa['presentation_only_levels']} "
          f"knowledge-dependent={sa['knowledge_dependent_levels']}")
    print(f"  every support atom in kernel closure: {sa['all_support_in_closure']}")
    print(f"  negative (N9) sentences: {sa['negative_sentences']} -> {sa['negative_texts']}")
    neg = [s["text"] for s in result["sentences"] if s["level"] == 9]
    print(f"negatives (D5) : {neg}")
    print(f"ablation (no domain knowledge): N7 = {result['ablation_without_domain']}")
    print(f"levels : {result['levels_present']}")
    print(f"verdict: {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())