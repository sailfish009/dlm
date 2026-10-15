"""Experiments/generalize -- learn concepts on a corpus, transfer to the north star.

Pipeline (all offline, deterministic)::

    corpus of programs --extract+acquire--> understanding facts (namespaced)
        --dlm.generalize.induce_concepts--> invented concepts (train split)
        --dlm.generalize.transfer--> kernel re-derives them on HELD-OUT programs
        --> abstracted sentences for the north star, each backed by a kernel proof

The real PyTorch MNIST example is held out: the generalisation is learned on the
synthetic corpus and *applied* to the north star by deduction, exactly as the
``calls`` law is learned across repos in ``experiments/code``.
"""
from __future__ import annotations

import argparse
import json
import os
import time

from dlm import Atom, Const, KnowledgeBase, closure
from dlm.generalize import concept_instances, induce_concepts, transfer
from dlm.ground import Ground
from dlm.lisp import form_to_rule
from dlm.proof import prove, verify

try:
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import CALLS, atom_of
    from ..mnist.semantics import UNDERSTANDING, bridge_forms
    from .programs import NORTH_STAR, corpus
except ImportError:  # direct `python experiments/generalize/run.py`
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import CALLS, atom_of
    from mnist.semantics import UNDERSTANDING, bridge_forms
    from generalize.programs import NORTH_STAR, corpus

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "mnist", "cache")
NORTH_STAR_SRC = os.path.join(CACHE, "main.py")

PRED_PHRASE = {
    "backpropagates": "backpropagates (loss.backward)",
    "optimizes": "updates parameters (optimizer.step)",
    "trains": "performs a training step",
    "evaluates": "runs the model in evaluation mode",
    "uses_grad_free": "computes without gradients",
    "loads_data": "loads data",
    "saves_model": "saves the model",
    "builds_model": "builds a model",
    "orchestrates": "orchestrates train and test",
    "is_module": "is a neural-network module",
    "inherits": "inherits a base class",
}


def _phrase(pred: str, rest) -> str:
    if pred == "has_layer":
        return f"has a {rest[0]} layer" if rest else "has a layer"
    return PRED_PHRASE.get(pred, pred)


def understanding_facts(prog_id: str, src: str) -> set:
    """Reduce one program, acquire its meaning, and return its UNDERSTANDING atoms.

    Constants in argument 0 (the subject) are namespaced with ``prog_id`` so the
    corpus shares one vocabulary without collisions.
    """
    ext = extract(src, "main")
    kb = acquire_knowledge(ext["facts"], ext["labels"], cache_dir=CACHE, offline=True)
    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(kb["meanings"])}
    k = KnowledgeBase(base)
    for r in Ground(tuple(form_to_rule(f) for f in bridge_forms())).rules:
        k.add_rule(r)
    k.add_rule(CALLS)
    closed = closure(k)
    out = set()
    for a in closed:
        if a.pred in UNDERSTANDING:
            out.add(Atom(a.pred, (Const(f"{prog_id}__{a.args[0].name}"),) + tuple(a.args[1:])))
    return out


def _display(subject: str) -> str:
    return subject.split("__", 1)[1] if "__" in subject else subject


def run(args) -> dict:
    programs = corpus()
    ns_src = open(NORTH_STAR_SRC, encoding="utf-8").read()
    all_progs = [{"name": NORTH_STAR, "source": ns_src}] + programs
    facts = {p["name"]: understanding_facts(p["name"], p["source"]) for p in all_progs}

    held = [NORTH_STAR, programs[-1]["name"]]
    train = [n for n in sorted(facts) if n not in held]
    train_facts = set().union(*[facts[n] for n in train])

    report = induce_concepts(train_facts, min_support=args.min_support,
                             max_body=args.max_body, max_concepts=args.max_concepts)

    transfers = {h: transfer(report.concepts, facts[h]) for h in held}

    # abstracted sentences for the north star, each backed by a kernel proof
    ns_facts = facts[NORTH_STAR]
    kb = KnowledgeBase(set(ns_facts))
    for c in report.concepts:
        kb.add_rule(c.rule)
    sentences = []
    for c in report.concepts:
        for subj in concept_instances(c, ns_facts):
            goal = Atom(c.name, (Const(subj),))
            p = prove(kb, goal)
            phrases = " and ".join(_phrase(pred, rest) for pred, rest in c.body)
            sentences.append({
                "subject": _display(subj),
                "concept": c.name,
                "text": f"{_display(subj)} {phrases}.",
                "support": [f"({c.name} {subj})"],
                "verified": bool(p is not None and verify(p, kb)),
            })

    n_detail = len(ns_facts)
    folded = sum((len(c.body) - 1) * len(concept_instances(c, ns_facts)) for c in report.concepts)
    ns_transfer = transfers[NORTH_STAR]
    n_hits = sum(v["hits"] for v in ns_transfer.values())
    held_totals = {h: sum(v["hits"] for v in transfers[h].values()) for h in held}

    # ---- falsification controls -------------------------------------------------
    # 1. the SAME miner on a SINGLE program must find nothing (the north-star gap).
    single = induce_concepts(ns_facts, min_support=args.min_support, max_body=args.max_body,
                             max_concepts=args.max_concepts)
    # 2. definitional soundness: every derived concept equals its body-match set on
    #    the training corpus (the invention adds no truth, only a name).
    from dlm import closure as _closure
    train_kb = KnowledgeBase(set(train_facts))
    for c in report.concepts:
        train_kb.add_rule(c.rule)
    train_closed = _closure(train_kb)
    sound = all(
        {a.args[0].name for a in train_closed if a.pred == c.name} == set(concept_instances(c, train_facts))
        for c in report.concepts
    )
    # 3. determinism of the miner
    again = induce_concepts(train_facts, min_support=args.min_support, max_body=args.max_body,
                            max_concepts=args.max_concepts)
    deterministic = again.to_dict() == report.to_dict()

    verdict = {
        "concepts_found": len(report.concepts) > 0,
        "concepts_non_degenerate": all(len(c.body) >= 2 for c in report.concepts),
        "single_program_finds_nothing": len(single.concepts) == 0,
        "concepts_definitionally_sound": sound,
        "deterministic": deterministic,
        "transfers_to_north_star": n_hits > 0,
        "each_held_out_gets_a_concept": all(t > 0 for t in held_totals.values()),
        "sentences_all_verified": all(s["verified"] for s in sentences) if sentences else False,
        "sentence_compression": folded > 0,
    }
    return {
        "corpus": {"programs": len(all_progs), "train": train, "held_out": held,
                   "train_subjects": report.subjects},
        "concepts": report.to_dict()["concepts"],
        "concepts_found": len(report.concepts),
        "transfer": transfers,
        "held_out_totals": held_totals,
        "controls": {
            "single_program_concepts": len(single.concepts),
            "definitionally_sound": sound,
            "deterministic": deterministic,
        },
        "north_star": {
            "detailed_atoms": n_detail,
            "abstracted_sentences": sentences,
            "folded_literals": folded,
        },
        "verdict": verdict,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="generalize concepts across a program corpus")
    ap.add_argument("--min-support", type=int, default=2)
    ap.add_argument("--max-body", type=int, default=3)
    ap.add_argument("--max-concepts", type=int, default=8)
    ap.add_argument("--offline", action="store_true",
                    help="accepted for harness compatibility; the pipeline is always offline")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "generalize"))
    args, _unknown = ap.parse_known_args(argv)

    result = run(args)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    c = result["corpus"]
    print(f"corpus : {c['programs']} programs ({len(c['train'])} train, "
          f"{len(c['held_out'])} held out: {c['held_out']})")
    print(f"concepts ({result['concepts_found']}):")
    for con in result["concepts"]:
        print(f"   {con['name']}: {con['literals']}  (support {con['support']})")
    print("transfer:")
    for prog, rep in result["transfer"].items():
        hits = {k: v["hits"] for k, v in rep.items()}
        print(f"   {prog} (total {result['held_out_totals'][prog]}): {hits}")
    print(f"controls: {result['controls']}")
    print("abstracted sentences (north star):")
    for s in result["north_star"]["abstracted_sentences"]:
        print(f"   [{'ok' if s['verified'] else 'XX'}] {s['text']}  <- {s['support']}")
    print(f"verdict: {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())