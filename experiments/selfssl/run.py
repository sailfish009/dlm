"""Recursive self-supervised learning -- the north star as ONE closed loop.

The single recursive self-supervised learning experiment (v0.0058).  It runs
forever, prints a natural-language summary of every round so you can watch it,
and only stops when YOU stop it (Ctrl-C).

Each round performs exactly one *train -> evaluate -> summarize* cycle, in the
order that makes the evaluation honest:

  TRAIN     PERCEIVE one new program (the real main.py, then the 12-program
            corpus, then a deterministic stream of generated variants), REDUCE
            it to function-free Horn facts.
  LEARN     INDUCE concepts over the corpus the model ALREADY had (its own past
            output -- the recursion: output becomes the next input), never over
            the program under test.
  EVALUATE  re-derive those concepts by PROOF on the HELD-OUT new program
            (``dlm.generalize.transfer``), reify the model's own ``calls``
            relation one more level through the kernel (``dlm.recursive``), and
            self-assess from the kernel closure only (``dlm.ability``) -- so a
            weak spot is a *question*, never a claim.
  SUMMARIZE emit one natural-language sentence describing the round, built from
            the model's own derived conclusions -- never from a label.
  ADMIT     only now fold the new program into the corpus, so the next round
            learns from strictly more of the model's own conclusions.

Nothing here is supervised: the kernel is the only judge.  The loop terminates
only when (a) a ``--rounds`` cap is given, or (b) the user presses Ctrl-C; on
stop it writes a report.

Report: ``reports/selfssl/<stamp>/result.json`` (or ``--json PATH``).
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_EXP = os.path.dirname(_HERE)
_ROOT = os.path.dirname(_EXP)
for _p in (_ROOT, _EXP):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dlm import Atom, Const, KnowledgeBase, closure
from dlm.ability import ability_profile
from dlm.generalize import induce_concepts, transfer
from dlm.gist import EXTERNAL_PREDICATES, gist_rules
from dlm.ground import Ground
from dlm.lisp import form_to_rule
from dlm.recursive import recurse

try:                                     # imported as experiments.selfssl.run
    from ..mnist.extract import extract
    from ..mnist.knowledge import acquire_knowledge, meaning_facts
    from ..mnist.run import CALLS, KNOWLEDGE_CACHE, atom_of, pipeline
    from ..mnist.semantics import UNDERSTANDING, bridge_forms
    from ..generalize.programs import NORTH_STAR, corpus, program
except ImportError:                      # direct `python experiments/selfssl/run.py`
    from mnist.extract import extract
    from mnist.knowledge import acquire_knowledge, meaning_facts
    from mnist.run import CALLS, KNOWLEDGE_CACHE, atom_of, pipeline
    from mnist.semantics import UNDERSTANDING, bridge_forms
    from generalize.programs import NORTH_STAR, corpus, program

VERSION = "0.0.58"

# Behaviour gloss for a concept body -- presentation only, never consulted for
# truth (the kernel decides whether the concept fires).
_PHRASE = {
    "backpropagates": "backpropagates the loss",
    "optimizes": "updates parameters",
    "trains": "performs a training step",
    "evaluates": "runs in evaluation mode",
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
    return _PHRASE.get(pred, pred)


def _gloss(concept) -> str:
    return " and ".join(_phrase(pred, rest) for pred, rest in concept.body)


def _ns(prog_id: str, atom: Atom) -> Atom:
    """Name-space the SUBJECT (arg0) so programs share one vocabulary.

    Shared constant rest-args (conv2d/linear/...) stay un-namespaced so features
    align across programs -- exactly the convention in ``experiments/generalize``.
    """
    if not atom.args:
        return atom
    return Atom(atom.pred, (Const(f"{prog_id}__{atom.args[0].name}"),) + tuple(atom.args[1:]))


def reduce_program(prog_id: str, src: str, *, cache_dir: str,
                   offline: bool) -> tuple:
    """Reduce one program -> (namespaced UNDERSTANDING atoms, namespaced calls edges).

    The understanding atoms are what the generaliser mines; the calls edges are the
    raw relation the recursive reification composes.  Both are name-spaced per
    program so the accumulated corpus is one shared vocabulary.
    """
    ext = extract(src, "main")
    kb = acquire_knowledge(ext["facts"], ext["labels"], cache_dir=cache_dir,
                           offline=offline)
    base = {atom_of(f) for f in ext["facts"]}
    base |= {atom_of(f) for f in meaning_facts(kb["meanings"])}
    k = KnowledgeBase(base)
    for r in Ground(tuple(form_to_rule(f) for f in bridge_forms())).rules:
        k.add_rule(r)
    k.add_rule(CALLS)
    closed = closure(k)
    under = {_ns(prog_id, a) for a in closed if a.pred in UNDERSTANDING}
    edges = {(f"{prog_id}__{f[1]}", f"{prog_id}__{f[2]}")
             for f in ext["facts"] if f[0] == "calls"}
    return under, edges


def _theory_rules():
    """Bridge + gist rules -- the model's GIVEN conceptual vocabulary."""
    return (tuple(r for r in Ground(tuple(form_to_rule(f) for f in bridge_forms())).rules)
            + gist_rules())


_VARIANT_LAYERS = (
    ("conv2d", "linear"), ("conv2d", "linear", "dropout"), ("linear",),
    ("conv2d", "dropout"), ("conv2d", "linear", "max_pool2d"),
    ("linear", "dropout"), ("conv2d",),
)


def _variant(i: int) -> str:
    layers = _VARIANT_LAYERS[i % len(_VARIANT_LAYERS)]
    return program(layers=layers, backward=(i % 2 == 0), step=(i % 3 != 0),
                   ev=(i % 4 != 1), nograd=(i % 5 != 2), save=(i % 6 != 3),
                   loader=(i % 7 != 4), sched=(i % 2 == 1), entry="main")


def source_stream(cache_dir: str):
    """An unbounded, deterministic stream of (name, source) learning episodes.

    Round 0 is the real PyTorch MNIST example (from cache); then the 12-program
    corpus; then generated variants forever.  Deterministic, so an offline run
    replays byte-for-byte and the bounded test is reproducible.
    """
    cached = os.path.join(cache_dir, "main.py")
    if os.path.exists(cached):
        with open(cached, encoding="utf-8") as fh:
            yield (NORTH_STAR, fh.read())
    for p in corpus():
        yield (p["name"], p["source"])
    i = 0
    while True:
        i += 1
        yield (f"g{i}", _variant(i))


def _headline(src: str, cache_dir: str, offline: bool):
    """The model's own deepest POSITIVE reading for this program, or None.

    Certified-absence sentences (level 9) are excluded from the headline: they are
    valid but uninformative about what the program *is*.  The deepest reading at
    its level is preferred; ties go to the longest text.
    """
    try:
        p = pipeline(src, module="main", cache_dir=cache_dir, offline=offline)
    except Exception:                       # noqa: BLE001 -- a read must never kill the loop
        return None
    cert = [s for s in p.get("sentences", []) if s.get("certified") and s["level"] < 9]
    if not cert:
        return None
    top = max(s["level"] for s in cert)
    return max((s for s in cert if s["level"] == top),
               key=lambda s: len(s["text"]))["text"]


def _summarize(m: dict, gloss) -> str:
    """One natural-language sentence about the round, from its derived quantities.

    ``m`` carries only kernel/model outputs (counts, concept body gloss, proof
    counts, recursion depth) -- there is no free-text generation and no label.
    """
    clauses = [f"Round {m['round']} read {m['source']} and reduced it to "
               f"{m['new_facts']} new facts"]
    if m["concepts"]:
        if m["concepts_transferred"]:
            clauses.append(
                f"from the {m['corpus_facts']} facts it already had it induced "
                f"{m['concepts']} concepts, and {m['concepts_transferred']} of "
                f"them re-derive on this held-out program by proof "
                f"({m['transfer_instances']} instances, e.g. a subject that {gloss})")
        else:
            clauses.append(
                f"from the {m['corpus_facts']} facts it already had it induced "
                f"{m['concepts']} concepts, but none re-derives on this "
                f"program by proof yet")
    else:
        clauses.append(
            f"its corpus of {m['corpus_facts']} facts is still too small to "
            f"induce a non-degenerate concept")
    clauses.append(
        f"in-sample it derives {m['derived_atoms']} atoms and proves "
        f"{m['proved']}/{m['targets']} of its own promises")
    clauses.append(
        f"its reified calls relation reaches depth {m['reach_depth']} "
        f"({m['reach_pairs']} pairs)")
    if m["actionable"]:
        t = m["actionable"][0]
        clauses.append(
            f"its open promise '{t}' is blocked only on acquired knowledge "
            f"({', '.join(m['external'][t])})")
    text = "; ".join(clauses)
    if m["reading"]:
        text += f'. Its deepest certified reading: "{m["reading"]}"'
    return text + "."


def step(state: dict, name: str, src: str, *, cache_dir: str, offline: bool,
         do_reading: bool, min_support: int, max_body: int,
         max_concepts: int) -> dict:
    """One train -> learn -> evaluate -> summarize -> admit round."""
    t0 = time.time()
    index = state["round"]
    corpus_facts = len(state["corpus"])

    # TRAIN -- perceive + reduce the new program (not yet absorbed)
    under, edges = reduce_program(name, src, cache_dir=cache_dir, offline=offline)
    n_new = len(under - state["corpus"])

    # LEARN -- induce concepts over what the model ALREADY had (its own output)
    conc = induce_concepts(state["corpus"], min_support=min_support,
                           max_body=max_body, max_concepts=max_concepts)

    # EVALUATE -- deductive transfer to the HELD-OUT program, then close + assess
    held = transfer(conc.concepts, under)
    rec = recurse(sorted(state["edges"] | edges))
    reach = {Atom("reach", (Const(a), Const(b))) for a, b in rec.relation}
    theory = _theory_rules() + conc.rules()
    kb = KnowledgeBase(state["corpus"] | under | reach)
    for r in theory:
        kb.add_rule(r)
    closed = closure(kb)
    ab = ability_profile(theory, closed, facts=state["corpus"] | under,
                         external=EXTERNAL_PREDICATES)

    reading = _headline(src, cache_dir, offline) if do_reading else None
    xfer = [c for c in conc.concepts if held.get(c.name, {}).get("hits")]
    metrics = {
        "round": index,
        "source": name,
        "new_facts": n_new,
        "corpus_facts": corpus_facts,
        "concepts": len(conc.concepts),
        "concept_literals": [
            [f"{p}(X,{','.join(rest)})" if rest else f"{p}(X)" for p, rest in c.body]
            for c in conc.concepts],
        "concepts_transferred": len(xfer),
        "transfer_instances": sum(held[c.name]["hits"] for c in conc.concepts),
        "derived_atoms": ab.derived_total,
        "targets": len(ab.targets),
        "proved": len(ab.targets) - len(ab.open),
        "open": list(ab.open),
        "actionable": list(ab.actionable),
        "external": {t: list(ab.external[t]) for t in ab.open},
        "reach_depth": rec.depth,
        "reach_pairs": len(rec.relation),
        "reading": reading,
    }
    metrics["summary"] = _summarize(metrics, _gloss(xfer[0]) if xfer else None)

    # ADMIT -- output becomes the next round's input (the recursion)
    state["corpus"] |= under
    state["edges"] |= edges
    state["round"] = index + 1
    metrics["seconds"] = round(time.time() - t0, 3)
    return metrics


def run(*, max_rounds=None, cache_dir: str = KNOWLEDGE_CACHE, offline: bool = True,
        do_reading: bool = True, min_support: int = 2, max_body: int = 3,
        max_concepts: int = 8, should_stop=None, on_round=None) -> dict:
    """Run the closed loop until the cap, the user, or the stream ends.

    ``should_stop()`` is polled BETWEEN rounds so a Ctrl-C finishes the round in
    flight instead of losing it.  Returns the round records plus final metrics;
    the caller owns printing and persistence.
    """
    should_stop = should_stop or (lambda: False)
    state = {"round": 0, "corpus": set(), "edges": set()}
    rounds = []
    interrupted = False
    try:
        for name, src in source_stream(cache_dir):
            if (max_rounds is not None and len(rounds) >= max_rounds) or should_stop():
                break
            rd = step(state, name, src, cache_dir=cache_dir, offline=offline,
                      do_reading=do_reading, min_support=min_support,
                      max_body=max_body, max_concepts=max_concepts)
            rounds.append(rd)
            if on_round is not None:
                on_round(rd)
    except KeyboardInterrupt:                 # the user forced quit mid-round
        interrupted = True
    return {
        "rounds": rounds,
        "interrupted": interrupted,
        "rounds_run": len(rounds),
        "final_corpus_facts": len(state["corpus"]),
        "final_reach_pairs": (rounds[-1]["reach_pairs"] if rounds else 0),
        "max_concepts_transferred": max(
            (rd["concepts_transferred"] for rd in rounds), default=0),
        "all_ok": bool(rounds) and all(rd["summary"] for rd in rounds),
    }


def _fmt_round(rd: dict) -> str:
    return (f"[{rd['round']:>3}] {rd['source']:<9} "
            f"corpus={rd['corpus_facts']:<4} concepts={rd['concepts']} "
            f"xfer={rd['concepts_transferred']}({rd['transfer_instances']}) "
            f"proved={rd['proved']}/{rd['targets']} derived={rd['derived_atoms']} "
            f"reach=d{rd['reach_depth']}/{rd['reach_pairs']} ({rd['seconds']}s)\n"
            f"      > {rd['summary']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="closed-loop recursive self-supervised learning (Ctrl-C to stop)")
    ap.add_argument("--rounds", type=int, default=0,
                    help="run this many rounds then stop (0 = run until Ctrl-C)")
    ap.add_argument("--cache", default=KNOWLEDGE_CACHE)
    ap.add_argument("--offline", action="store_true", default=True,
                    help="replay from cache; deterministic (default)")
    ap.add_argument("--online", dest="offline", action="store_false",
                    help="allow live web acquisition")
    ap.add_argument("--no-reading", dest="do_reading", action="store_false",
                    help="skip the per-program north-star reading headline")
    ap.add_argument("--min-support", type=int, default=2)
    ap.add_argument("--max-body", type=int, default=3)
    ap.add_argument("--max-concepts", type=int, default=8)
    ap.add_argument("--out", default=os.path.join(_ROOT, "reports", "selfssl"))
    ap.add_argument("--json", default="")
    args = ap.parse_args(argv)

    stop = {"flag": False}

    def _on_sigint(signum, frame):        # noqa: ANN001
        if stop["flag"]:
            raise KeyboardInterrupt          # second Ctrl-C forces an immediate exit
        stop["flag"] = True
        print("\n[selfssl] stop requested -- finishing the current round, "
              "then writing the report (press Ctrl-C again to force).", flush=True)

    old = None
    try:
        old = signal.signal(signal.SIGINT, _on_sigint)
    except ValueError:                        # not the main thread
        old = None

    print(f"selfssl v{VERSION}: recursive self-supervised learning (closed loop)")
    print("  source stream: main.py -> 12-program corpus -> generated variants")
    print(f"  acquisition : {'offline (cache replay)' if args.offline else 'online'}"
          f"   reading: {'on' if args.do_reading else 'off'}")
    print(f"  stop        : " + (f"after {args.rounds} rounds"
                                 if args.rounds else "Ctrl-C (you decide)"))
    print("-" * 78)
    try:
        result = run(max_rounds=(args.rounds or None), cache_dir=args.cache,
                     offline=args.offline, do_reading=args.do_reading,
                     min_support=args.min_support, max_body=args.max_body,
                     max_concepts=args.max_concepts, should_stop=lambda: stop["flag"],
                     on_round=lambda rd: print(_fmt_round(rd), flush=True))
    except KeyboardInterrupt:
        result = {"rounds": [], "interrupted": True, "rounds_run": 0,
                  "final_corpus_facts": 0, "final_reach_pairs": 0,
                  "max_concepts_transferred": 0, "all_ok": False}
    finally:
        if old is not None:
            signal.signal(signal.SIGINT, old)

    if stop["flag"]:
        reason = "user interrupt"
    elif args.rounds:
        reason = "round cap"
    else:
        reason = "stream end"
    print("-" * 78)
    print(f"stopped after {result['rounds_run']} rounds ({reason}); "
          f"corpus={result['final_corpus_facts']} facts, "
          f"calls relation={result['final_reach_pairs']} pairs, "
          f"max concepts transferred={result['max_concepts_transferred']}")
    if result["rounds"]:
        last = result["rounds"][-1]
        print(f"last round [{last['round']}] {last['source']}: "
              f"concepts {last['concepts']} (xfer {last['concepts_transferred']}), "
              f"proved {last['proved']}/{last['targets']}, "
              f"derived {last['derived_atoms']}")

    out = {"version": VERSION, "stop_reason": reason, **result}
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = (os.path.abspath(args.json) if args.json
            else os.path.join(args.out, stamp, "result.json"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f"report: {path}")
    return 0 if (result["all_ok"] or result["rounds_run"] == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())