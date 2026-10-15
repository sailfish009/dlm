"""Experiments/abstraction -- L5..L9 on the program corpus (untrusted, offline).

Ladder:
  L5 composition  -- structural conjunctive patterns over relational facts
  L6 architecture -- recurring ordered motifs in the forward pipeline
  L7 intent       -- purpose hypotheses read from the program's own text
  L8 causal       -- "why" sentences from ACQUIRED API-effect facts + observed calls
  L9 transfer     -- the patterns applied to held-out programs (real main.py + a
                     new shape), reported as analogies

Only L5/L6/L9 are kernel-certified (patterns become definitional rules and the
kernel derives their instances).  L7 is explicitly a HYPOTHESIS (intent is not in
the closure).  L8 is as sound as its acquired API facts.  The run also reports an
``abstraction_score`` against a human checklist for the real program.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import time

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure
from dlm.compose import (
    induce_patterns, is_connected, motifs, pattern_extension, transfer_patterns,
)
from dlm.ground import Ground
from dlm.lisp import form_to_rule
from dlm.proof import prove, verify

try:
    from ..generalize.programs import NORTH_STAR, corpus, program
    from ..mnist.api_semantics import API_EFFECTS, API_PROVENANCE
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import CALLS, atom_of
    from ..mnist.semantics import bridge_forms
except ImportError:  # direct `python experiments/abstraction/run.py`
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from generalize.programs import NORTH_STAR, corpus, program
    from mnist.api_semantics import API_EFFECTS, API_PROVENANCE
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import CALLS, atom_of
    from mnist.semantics import bridge_forms

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "mnist", "cache")
NORTH_STAR_SRC = os.path.join(CACHE, "main.py")

# L6: normalize concrete ops to architecture ROLES so motifs transfer across
# programs with different layer names (self.conv1 vs self.c1).  Untrusted reader.
ROLE_CUES = [("conv", "conv"), ("max_pool", "pool"), ("pool", "pool"),
             ("dropout", "dropout"), ("flatten", "flatten"), ("relu", "relu"),
             ("softmax", "softmax"), ("linear", "linear"), ("fc", "linear"),
             ("c1", "conv"), ("c2", "conv"), ("c3", "conv")]


def role_of(slug: str) -> str:
    for cue, role in ROLE_CUES:
        if cue in slug:
            return role
    return slug


def normalize_ops(ops) -> list:
    return [role_of(o) for o in ops]


def _subseq(sub, seq) -> bool:
    return any(tuple(seq[i:i + len(sub)]) == tuple(sub)
               for i in range(len(seq) - len(sub) + 1))

# ---- L7: intent cues (hand-given READER, like the bridge -- no program truth) ----
INTENT_CUES = [
    ("mnist", "classifies handwritten digits (MNIST)"),
    ("epoch", "trains for a number of epochs"),
    ("batch size", "configures the batch size"),
    ("learning rate", "configures the learning rate"),
    ("gamma", "decays the learning rate across epochs"),
    ("single pass", "can run a quick single-pass smoke test"),
    ("saving", "can save the trained model"),
    ("checkpoint", "can resume from a checkpoint"),
    ("seed", "makes the run reproducible"),
    ("accelerator", "selects the compute accelerator"),
    ("logging", "logs training progress"),
    ("example", "is a reference example implementation"),
]

# ---- L8: ACQUIRED API-effect facts live in experiments/mnist/api_semantics.py --

def full_facts(src: str, module: str = "prog"):
    """Extract + acquire + derive the program's closed fact set (per program).

    ``module`` is the file's own name; keeping it distinct from the entry
    function name avoids a spurious ``defines(X,_) = {entry}`` degeneracy.
    """
    ext = extract(src, module)
    kb = acquire_knowledge(ext["facts"], ext["labels"], cache_dir=CACHE, offline=True)
    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(kb["meanings"])}
    k = KnowledgeBase(base)
    for r in Ground(tuple(form_to_rule(f) for f in bridge_forms())).rules:
        k.add_rule(r)
    k.add_rule(CALLS)
    return closure(k), ext["labels"], ext["pipelines"]


def forward_pipeline(pipelines) -> list:
    for key, ops in pipelines.items():
        if key.endswith("_forward"):
            return list(ops)
    return []


def intent_hypotheses(src: str) -> list:
    """L7: read purpose hypotheses from the program's own docstrings/help text."""
    tree = ast.parse(src)
    texts = []
    doc = ast.get_docstring(tree)
    if doc:
        texts.append(doc)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            d = ast.get_docstring(node)
            if d:
                texts.append(d)
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg in ("help", "description") and isinstance(kw.value, ast.Constant) \
                        and isinstance(kw.value.value, str):
                    texts.append(kw.value.value)
    out, seen = [], set()
    for t in texts:
        low = t.lower()
        for cue, gloss in INTENT_CUES:
            if cue in low and gloss not in seen:
                seen.add(gloss)
                out.append({"intent": gloss, "cue": cue, "evidence": t.strip(),
                            "status": "hypothesis", "certified": False})
    return out


def causal_sentences(closed: set) -> list:
    """L8: derive 'why' sentences from acquired API-effect facts + observed calls."""
    k = KnowledgeBase(set(closed))
    for sym, eff in API_EFFECTS:
        k.add_fact(Atom("api_effect", (Const(sym), Const(eff))))
    k.add_rule(Rule(Atom("explains", (Var("?f"), Var("?s"), Var("?e"))),
                    (Atom("calls", (Var("?f"), Var("?s"))),
                     Atom("api_effect", (Var("?s"), Var("?e")))), name="explains"))
    derived = closure(k)
    out = []
    for a in sorted(derived, key=str):
        if a.pred != "explains":
            continue
        f, s, e = (x.name for x in a.args)
        goal = Atom("calls", (Const(f), Const(s)))
        p = prove(k, goal)
        out.append({"function": f, "symbol": s, "effect": e,
                    "text": f"{f} calls {s} in order to {e}.",
                    "certified": bool(p is not None and verify(p, k)),
                    "provenance": API_PROVENANCE})
    return out


def pattern_rules(patterns) -> list:
    return [Rule(Atom(f"pattern{i}", (Var("X"),)),
                 tuple(Atom(pred, tuple(Var(v) for v in args)) for pred, args in p.body),
                 name=f"pattern{i}") for i, p in enumerate(patterns)]


def _hits(patterns, facts) -> dict:
    k = KnowledgeBase(set(facts))
    for r in pattern_rules(patterns):
        k.add_rule(r)
    closed = closure(k)
    return {f"pattern{i}": sorted(a.args[0].name for a in closed if a.pred == f"pattern{i}")
            for i in range(len(patterns))}


def run(args) -> dict:
    ns_src = open(NORTH_STAR_SRC, encoding="utf-8").read()
    # a genuinely NEW shape (layer set not present in the corpus) for L9
    new_shapes = [
        {"name": "s_dropout", "source": program(layers=("dropout",), backward=True, step=True,
         ev=True, nograd=True, save=False, loader=False, sched=False)},
    ]
    progs = [{"name": NORTH_STAR, "source": ns_src}] + corpus() + new_shapes
    facts, labels, pipes = {}, {}, {}
    for p in progs:
        closed, lab, pl = full_facts(p["source"], module=p["name"])
        facts[p["name"]] = closed
        labels[p["name"]] = lab
        pipes[p["name"]] = normalize_ops(forward_pipeline(pl))

    corpus_names = [c["name"] for c in corpus()]
    ns, held = NORTH_STAR, ["s_dropout"]

    # ---- L5: induce structural patterns on the corpus (held out ns + new shape) --
    L5 = induce_patterns({n: facts[n] for n in corpus_names}, min_support=3,
                         max_body=args.max_body, max_patterns=args.max_patterns)
    # ---- L6: forward-pass motifs (over architecture ROLES) across the corpus -----
    L6 = motifs({n: pipes[n] for n in corpus_names if pipes[n]}, min_len=2, max_len=4,
                min_support=3, top=6)
    target_roles = pipes[ns]
    arch_transfer = [m for m in L6 if _subseq(m["ops"], target_roles)]
    newshape_motifs = [m for m in L6 if _subseq(m["ops"], pipes["s_dropout"])]
    discriminate = [m for m in arch_transfer if not _subseq(m["ops"], pipes["s_dropout"])]

    L5_lits = [p.literals() for p in L5]
    L5_hits_ns = _hits(L5, facts[ns])

    # ---- L9: transfer to held-out programs + analogy -----------------------------
    L9 = transfer_patterns(L5, {ns: facts[ns], **{h: facts[h] for h in held}})
    analogy = []
    for m in L6:
        owners = [n for n in corpus_names if any(
            tuple(pipes[n][i:i + len(m["ops"])]) == tuple(m["ops"])
            for i in range(len(pipes[n]) - len(m["ops"]) + 1))]
        if len(owners) >= 2:
            analogy.append({"motif": m["ops"], "support": m["support"], "programs": owners[:5]})

    # ---- L7/L8 -------------------------------------------------------------------
    L7 = intent_hypotheses(ns_src)
    L8 = causal_sentences(facts[ns])

    # ---- abstraction_score against a human checklist for the real program --------
    delegation = [p for p in L5 if is_connected(p)]
    produced = {
        "L5_multistep_routine": bool(L5),
        "L5_compositional_pattern": bool(delegation),
        "L6_forward_motif": bool(L6),
        "L6_architecture_transfers": bool(arch_transfer),
        "L7_program_purpose": any("classifies" in i["intent"] or "reference" in i["intent"] for i in L7),
        "L7_intent_is_hypothesis": all(not i["certified"] for i in L7) and bool(L7),
        "L8_why_zero_grad": any(c["symbol"] == "optimizer_zero_grad" for c in L8),
        "L8_why_eval": any(c["symbol"] == "model_eval" for c in L8),
        "L9_transfer_to_real_program": any(v["hits"].get(ns) for v in L9.values()),
        "L9_new_shape_discriminated": bool(discriminate),
    }
    score = sum(1 for v in produced.values() if v) / len(produced)

    verdict = {
        "composition_found": any(is_connected(p) for p in L5),
        "architecture_motif_found": bool(L6),
        "architecture_transfers": bool(arch_transfer),
        "intent_hypotheses_found": bool(L7),
        "intent_not_certified": all(not i["certified"] for i in L7),
        "causal_sentences_certified": all(c["certified"] for c in L8) if L8 else False,
        "patterns_transfer": any(v["hits"].get(ns) for v in L9.values()),
        "new_shape_discriminated": bool(discriminate),
        "abstraction_score_above_half": score >= 0.5,
    }
    return {
        "corpus": {"programs": len(progs), "mining": corpus_names, "held_out": [ns] + held},
        "L5_composition": {"patterns": L5_lits, "north_star_hits": L5_hits_ns},
        "L6_architecture": {"corpus_motifs": L6, "target_roles": target_roles,
                            "transferred": arch_transfer,
                            "discriminating": discriminate},
        "L7_intent": L7,
        "L8_causal": L8,
        "L9_transfer": L9,
        "L9_analogy": analogy,
        "abstraction_score": {"produced": produced, "score": round(score, 3)},
        "verdict": verdict,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="L5..L9 abstraction ladder over a program corpus")
    ap.add_argument("--max-body", type=int, default=2)
    ap.add_argument("--max-patterns", type=int, default=6)
    ap.add_argument("--offline", action="store_true",
                    help="accepted for harness compatibility; the pipeline is always offline")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reports", "abstraction"))
    args, _unknown = ap.parse_known_args(argv)

    result = run(args)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out, stamp)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "result.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    print(f"corpus : {result['corpus']['programs']} programs (mine {len(result['corpus']['mining'])}, "
          f"held out {result['corpus']['held_out']})")
    print("L5 composition:")
    for lits, hits in zip(result["L5_composition"]["patterns"],
                          result["L5_composition"]["north_star_hits"].values()):
        print(f"   {lits}  -> north star {hits}")
    print("L6 architecture (roles):")
    print(f"   target roles: {result['L6_architecture']['target_roles']}")
    for m in result["L6_architecture"]["corpus_motifs"]:
        tag = "transfers" if m in result["L6_architecture"]["transferred"] else "-"
        print(f"   {m['ops']}  (support {m['support']}) [{tag}]")
    print(f"   discriminating on unseen shape: {result['L6_architecture']['discriminating']}")
    print(f"L7 intent hypotheses: {len(result['L7_intent'])}")
    for i in result["L7_intent"]:
        print(f"   [{i['status']}] {i['intent']}")
    print(f"L8 causal sentences: {len(result['L8_causal'])}")
    for c in result["L8_causal"]:
        print(f"   [{'ok' if c['certified'] else 'XX'}] {c['text']}")
    print("L9 transfer:")
    for k, v in result["L9_transfer"].items():
        print(f"   {k}: {v['literals']} -> { {n: h for n, h in v['hits'].items()} }")
    print(f"abstraction_score: {result['abstraction_score']['score']}  "
          f"{result['abstraction_score']['produced']}")
    print(f"verdict: {result['verdict']}")
    print(f"report: {path}")
    return 0 if all(result["verdict"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())