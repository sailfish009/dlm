"""Random-web dual-ability self-supervision experiment (DLM v0.0022, NOTE 74).

Question.  Starting only from *randomly fetched* public web data and a trusted
kernel, with **zero human labels**, can one self-supervised loop improve more
than one ability at once -- and can the same harness surface behaviour we did
not programme in?

Two abilities, one data source, one label source (the kernel)::

    random Wikipedia article  ->  Wikidata claims + P279 hierarchy + prose
          |                                        |
          |  (A) deduction  -> kernel-derived subclass pairs -> induce the law
          |  (B) conversation -> sentence <-> relation (IR reader / realizer)
          v                                        v
    held-out entities   <---- generalisation ----   kernel gate (abstain, never guess)

(A) **Deduction** -- the model is *not* given the transitivity law.  It sees
    only ground facts and the kernel's derived pairs and must induce the law,
    then apply it to entities it never trained on.  Controls: facts-only
    (floor), oracle law (ceiling), shuffled labels (no-signal).
(B) **Conversation** -- an IR reader maps a sentence to the right relation and a
    realizer maps a relation back to a sentence; entity-level K-fold, cue
    ablation, surface/majority baselines.

Unexpected-behaviour probes: rules the model invents (verbatim), whether it
generalises across held-out entities, whether it ever fabricates a false
derivation, cycles/contradictions in the raw web graph, and a
deduction -> sentence -> deduction compositional round-trip.

Everything is cached under ``cache/`` so ``--offline`` reproduces a run exactly;
``--online`` fetches more random articles from the live web.  No network, no
human annotation, no torch/numpy.

Run::

    PYTHONPATH=. python experiments/webloop/run.py --offline --json report.json
    PYTHONPATH=. python experiments/webloop/run.py --online --docs 120 --seed 3
    PYTHONPATH=. python experiments/webloop/run.py --part deduction      # ability A only
    PYTHONPATH=. python experiments/webloop/run.py --part conversation   # ability B only
    PYTHONPATH=. python experiments/webloop/run.py --quick      # fast smoke test

Convenience wrappers (offline by default, timestamped report under reports/):
``./A_deduction.sh`` and ``./B_conversation.sh`` (pass ``--quick``/``--online`` etc.).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict, deque
from pathlib import Path
from random import Random
from typing import Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dlm import (  # noqa: E402
    Atom,
    Const,
    KnowledgeBase,
    Rule,
    Theory,
    Var,
    closure,
    induce_clauses,
    prove,
    solve,
)
from dlm.ssl import (  # noqa: E402
    Frame,
    IrReader,
    IrRealizer,
    IrSupervisor,
    aligned_examples,
    macro_recall_at_1,
    majority_baseline,
    reader_features,
    roundtrip_rate,
    surface_features,
)
from experiments.webloop import random_web  # noqa: E402

Example = Tuple[str, Frame, Tuple[Atom, ...], Tuple[Atom, ...]]
Row = Dict[str, float]


# ============================================================================
# small deterministic helpers
# ============================================================================
def _fa(f) -> Atom:
    """A web ``Fact`` -> a ground Horn atom."""
    return Atom(f.pred, (Const(str(f.subj)), Const(str(f.obj))))


def _pool(rows: Sequence[Row]) -> Row:
    n = sum(int(r.get("n", 0)) for r in rows)
    d = float(n) if n else 1.0
    out: Row = {"n": n}
    for key in ("recall_at_1", "kernel_accept", "recovery"):
        if any(key in r for r in rows):
            out[key] = sum(r.get(key, 0.0) * r.get("n", 0) for r in rows) / d
    out["false"] = sum(r.get("false", 0) for r in rows)
    return out


def _nonpairs(nodes: Sequence[str]) -> List[Tuple[str, str]]:
    return [(a, b) for a in nodes for b in nodes if a != b]


# ============================================================================
# Part 0. acquisition (random web, cached)
# ============================================================================
def acquisition(args: argparse.Namespace) -> Tuple[List, List, Dict[str, object]]:
    docs, hierarchy = random_web.acquire(
        args.docs,
        seed=args.seed,
        cache_dir=str(HERE / "cache"),
        offline=not args.online,
        subclass_depth=args.subclass_depth,
        summary_chars=args.summary_chars,
        pause=args.pause,
        retries=args.retries,
    )
    facts = [f for d in docs for f in d.facts]
    preds = sorted({f.pred for f in facts})
    return docs, hierarchy, {
        "docs": len(docs),
        "sentences": sum(len(d.sentences) for d in docs),
        "doc_facts": len(facts),
        "hierarchy_edges": len(hierarchy),
        "predicates": preds,
    }


# ============================================================================
# Part A. deduction -- induce the law from kernel-derived pairs
# ============================================================================
def _subclass_rule() -> Rule:
    x, y, z = Var("x"), Var("y"), Var("z")
    return Rule(
        Atom("subclass_of", (x, z)),
        (Atom("subclass_of", (x, y)), Atom("subclass_of", (y, z))),
        "subclass_trans",
    )


def _adjacency(hierarchy: Sequence) -> Dict[str, set]:
    adj: Dict[str, set] = defaultdict(set)
    for f in hierarchy:
        if f.pred == "subclass_of":
            adj[f.subj].add(f.obj)
            adj[f.obj]
    return adj


def _bfs_edges(adj: Dict[str, set], roots: Sequence[str], max_edges: int) -> List[Tuple[str, str]]:
    """A connected subgraph that preserves chains (random sampling would not)."""
    queue = deque(sorted(roots))
    seen = set(roots)
    seen_edges: set = set()
    out: List[Tuple[str, str]] = []
    while queue and len(out) < max_edges:
        n = queue.popleft()
        for m in sorted(adj.get(n, ())):
            if (n, m) in seen_edges:
                continue
            seen_edges.add((n, m))
            out.append((n, m))
            if m not in seen:
                seen.add(m)
                queue.append(m)
            if len(out) >= max_edges:
                break
    return out


def _node_folds(nodes: Iterable[str], k: int, seed: int) -> List[List[str]]:
    ns = sorted(nodes)
    Random(seed).shuffle(ns)
    k = max(1, min(int(k), len(ns))) if ns else 1
    groups: List[List[str]] = [[] for _ in range(k)]
    for i, n in enumerate(ns):
        groups[i % k].append(n)
    return groups


def _fact_kb(edges: Sequence[Tuple[str, str]]) -> KnowledgeBase:
    kb = KnowledgeBase()
    for a, b in edges:
        kb.add_fact(Atom("subclass_of", (Const(a), Const(b))))
    return kb


def _rules_kb(edges: Sequence[Tuple[str, str]], rules: Sequence[Rule]) -> KnowledgeBase:
    kb = _fact_kb(edges)
    for r in rules:
        kb.add_rule(r)
    return kb


def _has_transitivity(clauses: Sequence) -> bool:
    for c in clauses:
        body = c.rule.body
        if len(body) == 2 and all(b.pred == "subclass_of" for b in body):
            return True
    return False


def _sample(atoms: Sequence[Atom], k: int, seed: int) -> List[Atom]:
    items = sorted(atoms, key=str)
    if len(items) <= k:
        return items
    idx = list(range(len(items)))
    Random(seed).shuffle(idx)
    return sorted((items[i] for i in idx[:k]), key=str)


def deduction_part(hierarchy: Sequence, args: argparse.Namespace) -> Dict[str, object]:
    """Induce the subclass law from kernel-derived pairs; test on held-out entities."""
    if not hierarchy:
        return {"skipped": "no hierarchy"}
    trans = _subclass_rule()
    all_edges = sorted((f.subj, f.obj) for f in hierarchy if f.pred == "subclass_of")
    teacher = closure(_rules_kb(all_edges, [trans]))
    groups = _node_folds(_adjacency(hierarchy), args.deduce_folds, args.seed)

    rows: Dict[str, List[Row]] = {a: [] for a in ("identity", "oracle", "learned", "scrambled")}
    invented: List[str] = []
    seconds: List[float] = []
    found: List[bool] = []

    for gi, test_nodes in enumerate(groups):
        tn = set(test_nodes)
        train_all = [(s, o) for (s, o) in all_edges if s not in tn and o not in tn]
        tadj: Dict[str, set] = defaultdict(set)
        for s, o in train_all:
            tadj[s].add(o)
        roots = sorted(tadj, key=lambda n: (-len(tadj[n]), n))[:8]
        train_edges = _bfs_edges(tadj, roots, args.deduce_edges)
        train_nodes = sorted({a for a, _ in train_edges} | {b for _, b in train_edges})

        # labels are the kernel closure of the OBSERVED edges: the law must be
        # derivable from the training subgraph, never from a held-out path.
        train_teacher = closure(_rules_kb(train_edges, [trans]))
        universe = [Atom("subclass_of", (Const(a), Const(b))) for a, b in _nonpairs(train_nodes)]
        pos = _sample([a for a in universe if a in train_teacher], args.deduce_positives, args.seed + gi)
        neg = _sample([a for a in universe if a not in train_teacher], args.deduce_positives * 2, args.seed + gi)

        t0 = time.time()
        learned = induce_clauses(_fact_kb(train_edges), pos, neg, budget=args.budget,
                                 max_body=2, extra_vars=1)
        seconds.append(time.time() - t0)
        invented += [str(c.rule) for c in learned]
        found.append(_has_transitivity(learned))

        scrambled = ()
        if not args.no_scramble:
            rng = Random(args.seed + 1000 + gi)
            idx = list(range(len(universe)))
            rng.shuffle(idx)
            rpos = set(universe[i] for i in idx[: min(len(pos), len(universe))])
            rneg = _sample([a for a in universe if a not in rpos], len(rpos) * 2, args.seed + 7)
            scrambled = induce_clauses(_fact_kb(train_edges), sorted(rpos, key=str), rneg,
                                       budget=args.budget, max_body=2, extra_vars=1)

        held = {a for a in teacher if str(a.args[0]) in tn or str(a.args[1]) in tn}
        got = {
            "identity": closure(_fact_kb(all_edges)),
            "oracle": closure(_rules_kb(all_edges, [trans])),
            "learned": closure(_rules_kb(all_edges, [c.rule for c in learned])),
            "scrambled": closure(_rules_kb(all_edges, [c.rule for c in scrambled])),
        }
        for arm, atoms in got.items():
            recovered = len(atoms & held)
            rows[arm].append({
                "n": len(held),
                "recovered": recovered,
                "recovery": recovered / max(1, len(held)),
                "false": len(atoms - teacher),
            })

    return {
        "folds": len(groups),
        "train_edges_cap": args.deduce_edges,
        "teacher_pairs": len(teacher),
        "arms": {a: _pool(v) for a, v in rows.items()},
        "invented_rules": sorted(set(invented)),
        "transitivity_folds": int(sum(found)),
        "found_transitivity": any(found),
        "induce_seconds": [round(s, 2) for s in seconds],
    }


# ============================================================================
# Part B. conversation -- read sentences into relations, render relations back
# ============================================================================
def _build_examples(docs: Sequence, predicates: Sequence[str], mask: str) -> List[Example]:
    out: List[Example] = []
    for d in docs:
        ff = [f for f in d.facts if f.pred in predicates]
        for frame, positives, candidates in aligned_examples(d.sentences, ff, predicates, mask=mask):
            out.append((d.slug, frame, positives, candidates))
    return out


def _triples(examples: Sequence[Example]):
    return [(f, p, c) for _s, f, p, c in examples]


def _example_folds(examples: Sequence[Example], k: int, seed: int):
    slugs = sorted({e[0] for e in examples})
    Random(seed).shuffle(slugs)
    k = max(1, min(int(k), len(slugs))) if slugs else 1
    groups: List[List[str]] = [[] for _ in range(k)]
    for i, s in enumerate(slugs):
        groups[i % k].append(s)
    out = []
    for i in range(k):
        ts = set(groups[i])
        out.append(([e for e in examples if e[0] not in ts], [e for e in examples if e[0] in ts]))
    return out


def _train_reader(arm: str, train: Sequence[Example], args: argparse.Namespace) -> IrReader:
    reader = IrReader(lr=args.lr, features=surface_features if arm == "surface" else reader_features)
    IrSupervisor(reader=reader).fit_reader(
        _triples(train),
        epochs=args.epochs,
        seed=args.seed,
        scramble=(arm == "scrambled"),
        objective="softmax" if arm == "softmax" else "perceptron",
    )
    return reader


def _eval_reader(reader: IrReader, test: Sequence[Example], entailed: set) -> Row:
    n = hits = accepted = 0
    for _s, frame, positives, candidates in test:
        if not positives:
            continue
        ranked = reader.rank(frame, candidates)
        top = ranked[0] if ranked else None
        if top is None:
            continue
        n += 1
        if top in set(positives):
            hits += 1
        if top in entailed:
            accepted += 1
    d = float(n) if n else 1.0
    return {"n": n, "recall_at_1": hits / d, "kernel_accept": accepted / d, "false": 0}


def _ablate_cues(test: Sequence[Example], rng: Random) -> List[Example]:
    pool = [list(e[1].rel) for e in test if e[1].rel] or [["unknown"]]
    out: List[Example] = []
    for slug, frame, positives, candidates in test:
        other = pool[rng.randrange(len(pool))]
        out.append((slug, Frame(tuple(other), frame.subject, frame.obj, frame.order, frame.name),
                    positives, candidates))
    return out


def _rename_predicates(examples: Sequence[Example], prefix: str) -> List[Example]:
    """Invented-predicate control: the map frame -> *invented* name must be learnable."""
    out: List[Example] = []
    for slug, frame, positives, candidates in examples:
        pos = tuple(Atom(prefix + a.pred, a.args) for a in positives)
        cand = tuple(Atom(prefix + a.pred, a.args) for a in candidates)
        out.append((slug, frame, pos, cand))
    return out


def _inheritance_rules() -> Tuple[Rule, ...]:
    x, y, z = Var("x"), Var("y"), Var("z")
    return (
        _subclass_rule(),
        Rule(Atom("occupation", (x, z)), (Atom("occupation", (x, y)), Atom("subclass_of", (y, z))), "occupation_up"),
        Rule(Atom("instance_of", (x, z)), (Atom("instance_of", (x, y)), Atom("subclass_of", (y, z))), "instance_up"),
        Rule(Atom("located_in", (x, z)), (Atom("located_in", (x, y)), Atom("located_in", (y, z))), "located_in_trans"),
        Rule(Atom("part_of", (x, z)), (Atom("part_of", (x, y)), Atom("part_of", (y, z))), "part_of_trans"),
    )


def conversation_part(docs: Sequence, hierarchy: Sequence, args: argparse.Namespace) -> Dict[str, object]:
    facts = [f for d in docs for f in d.facts]
    predicates = sorted({f.pred for f in facts})
    cue = _build_examples(docs, predicates, "obj")
    deid = _build_examples(docs, predicates, "all")
    if not cue:
        return {"skipped": "no aligned examples"}

    kb = KnowledgeBase()
    for r in _inheritance_rules():
        kb.add_rule(r)
    for f in list(hierarchy) + list(facts):
        kb.add_fact(_fa(f))
    entailed = closure(kb)

    arms = ["majority", "untrained", "surface", "ir_learned", "ir_deidentified", "scrambled", "softmax"]
    rows: Dict[str, List[Row]] = {a: [] for a in arms}
    realizer_hits = realizer_n = 0

    for (train, test), (dtrain, _dtest) in zip(
        _example_folds(cue, args.folds, args.seed),
        _example_folds(deid, args.folds, args.seed),
    ):
        if not test:
            continue
        trained = {
            "untrained": IrReader(lr=args.lr),
            "surface": _train_reader("surface", train, args),
            "ir_learned": _train_reader("ir_learned", train, args),
            "scrambled": _train_reader("scrambled", train, args),
            "softmax": _train_reader("softmax", train, args),
        }
        trained["ir_deidentified"] = _train_reader("ir_learned", dtrain, args)

        rows["majority"].append({"n": len(test), "recall_at_1": majority_baseline(_triples(test)),
                                 "kernel_accept": 0.0, "false": 0})
        for arm, reader in trained.items():
            rows[arm].append(_eval_reader(reader, test, entailed))

        atoms = [e[2][0] for e in train][: args.realizer_atoms]
        realizer = IrRealizer()
        IrSupervisor(reader=trained["ir_learned"], realizer=realizer).fit_realizer(
            atoms, predicates=predicates, epochs=args.realizer_epochs, seed=args.seed)
        test_atoms = [e[2][0] for e in test][:20]
        if test_atoms:
            realizer_hits += round(roundtrip_rate(realizer, trained["ir_learned"], test_atoms,
                                                  predicates, k=3) * len(test_atoms))
            realizer_n += len(test_atoms)

    rng = Random(args.seed + 1)
    ablated = _pool([_eval_reader(_train_reader("ir_learned", tr, args), _ablate_cues(te, rng), entailed)
                     for tr, te in _example_folds(cue, args.folds, args.seed) if te])

    invent = _rename_predicates(cue, "inv_")
    inv_rows: Dict[str, List[Row]] = {"untrained": [], "learned": []}
    for tr, te in _example_folds(invent, args.folds, args.seed):
        if not te:
            continue
        inv_rows["untrained"].append(_eval_reader(IrReader(lr=args.lr), te, entailed))
        inv_rows["learned"].append(_eval_reader(_train_reader("ir_learned", tr, args), te, entailed))

    return {
        "stats": {
            "examples": len(cue),
            "entities": len({e[0] for e in cue}),
            "predicates": predicates,
            "kernel_closure": len(entailed),
            "derived": len(entailed - {_fa(f) for f in list(hierarchy) + list(facts)}),
        },
        "arms": {a: _pool(v) for a, v in rows.items()},
        "macro_recall": {
            "ir_learned": macro_recall_at_1(_train_reader("ir_learned", cue, args), _triples(cue)),
            "majority": majority_baseline(_triples(cue)),
        },
        "cue_ablation": ablated,
        "realizer": {"roundtrip_at_3": realizer_hits / realizer_n if realizer_n else 0.0, "n": realizer_n},
        "invented_predicate": {a: _pool(v) for a, v in inv_rows.items()},
    }


# ============================================================================
# Part C. unexpected-behaviour probes
# ============================================================================
def probes_part(docs: Sequence, hierarchy: Sequence, args: argparse.Namespace) -> Dict[str, object]:
    facts = [f for d in docs for f in d.facts]
    edges = sorted((f.subj, f.obj) for f in hierarchy if f.pred == "subclass_of")
    edge_set = set(edges)
    cycles = sorted((a, b) for a, b in edge_set if a != b and (b, a) in edge_set)
    self_loops = sorted({a for a, b in edge_set if a == b})

    kb = KnowledgeBase()
    for f in list(hierarchy) + list(facts):
        kb.add_fact(_fa(f))
    unknown = Atom("born_in", (Const("zzz_unknown"), Const("qqq_unknown")))
    decision = solve(kb, Theory("probe", ()), [unknown])

    # compositional round-trip: a fact the *deduction* side derived is verbalised
    # by the conversation side and read back to the same relation.
    teacher_kb = KnowledgeBase()
    for r in _inheritance_rules():
        teacher_kb.add_rule(r)
    for f in list(hierarchy) + list(facts):
        teacher_kb.add_fact(_fa(f))
    base = {_fa(f) for f in list(hierarchy) + list(facts)}
    derived = sorted((a for a in closure(teacher_kb) - base if a.pred in ("occupation", "instance_of")),
                     key=str)[:30]
    preds = sorted({f.pred for f in facts})
    cue = _build_examples(docs, preds, "obj")
    reader = IrReader(lr=args.lr)
    IrSupervisor(reader=reader).fit_reader(_triples(cue), epochs=args.epochs, seed=args.seed)
    realizer = IrRealizer()
    IrSupervisor(reader=reader, realizer=realizer).fit_realizer(
        [e[2][0] for e in cue], predicates=preds, epochs=args.realizer_epochs, seed=args.seed)
    rt = roundtrip_rate(realizer, reader, derived, preds, k=3) if derived else 0.0

    return {
        "raw_graph": {
            "edges": len(edges),
            "two_cycles": len(cycles),
            "cycle_examples": cycles[:5],
            "self_loops": len(self_loops),
        },
        "abstain": {
            "candidate": str(unknown),
            "abstained": decision.abstained,
            "proved": decision.proof is not None,
            "prove_returned_none": prove(kb, unknown) is None,
        },
        "compositional_roundtrip": {
            "derived_atoms": len(derived),
            "roundtrip_at_3": rt,
            "examples": [str(a) for a in derived[:5]],
        },
    }


# ============================================================================
# verdict + driver
# ============================================================================
def verdict(out: Dict[str, object]) -> List[str]:
    lines: List[str] = []
    ded = out.get("deduction", {})
    arms = ded.get("arms", {})
    if arms:
        lines.append(
            "deduction held-out recovery: identity=%.3f oracle=%.3f learned=%.3f scrambled=%.3f"
            % (arms["identity"].get("recovery", 0.0), arms["oracle"].get("recovery", 0.0),
               arms["learned"].get("recovery", 0.0), arms["scrambled"].get("recovery", 0.0))
        )
        lines.append(
            "  transitivity rediscovered=%s  false-derivations learned=%d"
            % (ded.get("found_transitivity"), arms["learned"].get("false", 0))
        )
        rules = ded.get("invented_rules", [])
        lines.append("  invented rules (verbatim, first 3):")
        for r in rules[:3]:
            lines.append("    " + r)
    conv = out.get("conversation", {})
    c = conv.get("arms", {})
    if c:
        lines.append(
            "conversation recall@1: untrained=%.3f surface=%.3f ir_learned=%.3f scrambled=%.3f majority=%.3f"
            % (c["untrained"].get("recall_at_1", 0.0), c["surface"].get("recall_at_1", 0.0),
               c["ir_learned"].get("recall_at_1", 0.0), c["scrambled"].get("recall_at_1", 0.0),
               c["majority"].get("recall_at_1", 0.0))
        )
        lines.append("  cue ablation=%.3f  realizer round-trip@3=%.3f"
                     % (conv.get("cue_ablation", {}).get("recall_at_1", 0.0),
                        conv.get("realizer", {}).get("roundtrip_at_3", 0.0)))
        inv = conv.get("invented_predicate", {})
        if inv:
            lines.append("  invented-predicate control: learned=%.3f untrained=%.3f (harness has signal)"
                         % (inv["learned"].get("recall_at_1", 0.0), inv["untrained"].get("recall_at_1", 0.0)))
    probes = out.get("probes", {})
    rg = probes.get("raw_graph", {})
    if rg:
        lines.append("probes: two-cycles=%d self-loops=%d  abstain=%s  compositional round-trip@3=%.3f"
                     % (rg.get("two_cycles", 0), rg.get("self_loops", 0),
                        probes.get("abstain", {}).get("abstained", False),
                        probes.get("compositional_roundtrip", {}).get("roundtrip_at_3", 0.0)))
    return lines


def run(args: argparse.Namespace) -> Dict[str, object]:
    t0 = time.time()
    docs, hierarchy, stats = acquisition(args)
    parts = set(getattr(args, "parts", None) or {"deduction", "conversation", "probes"})
    out: Dict[str, object] = {
        "config": {
            "docs": args.docs, "seed": args.seed, "offline": not args.online,
            "folds": args.folds, "deduce_folds": args.deduce_folds,
            "deduce_edges": args.deduce_edges, "epochs": args.epochs,
            "parts": sorted(parts),
        },
        "acquisition": stats,
    }
    if "deduction" in parts:
        out["deduction"] = deduction_part(hierarchy, args)
    if "conversation" in parts:
        out["conversation"] = conversation_part(docs, hierarchy, args)
    if "probes" in parts:
        out["probes"] = probes_part(docs, hierarchy, args)
    out["verdict"] = verdict(out)
    out["wall_seconds"] = round(time.time() - t0, 2)
    return out


def _requested_parts(spec: str) -> List[str]:
    """Parse ``--part`` (``all`` or a comma list) into an ordered list."""
    if spec.strip() in ("all", ""):
        return ["deduction", "conversation", "probes"]
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    unknown = [p for p in parts if p not in ("deduction", "conversation", "probes")]
    if unknown:
        raise SystemExit("unknown --part: %s (use all|deduction|conversation|probes)" % ", ".join(unknown))
    return parts


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="DLM random-web dual-ability self-supervision (v0.0022)")
    ap.add_argument("--docs", type=int, default=60)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--online", action="store_true", help="fetch from the live web (default: cache only)")
    ap.add_argument("--offline", action="store_true", help="use the local cache only (this is the default)")
    ap.add_argument("--folds", type=int, default=4, help="entity folds for the conversation side")
    ap.add_argument("--deduce-folds", type=int, default=3, help="entity folds for the deduction side")
    ap.add_argument("--deduce-edges", type=int, default=60, help="cap on training edges (induce_clauses cost)")
    ap.add_argument("--deduce-positives", type=int, default=120)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--realizer-epochs", type=int, default=10)
    ap.add_argument("--realizer-atoms", type=int, default=60)
    ap.add_argument("--lr", type=float, default=0.1)
    ap.add_argument("--budget", type=int, default=20000)
    ap.add_argument("--no-scramble", action="store_true", help="skip the shuffled-label control (faster)")
    ap.add_argument("--subclass-depth", type=int, default=3)
    ap.add_argument("--summary-chars", type=int, default=1200)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--part", type=str, default="all",
                    help="which sub-experiment(s) to run: all (default), deduction, "
                         "conversation, probes, or a comma list")
    ap.add_argument("--quick", action="store_true", help="small fast smoke run")
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args(argv)
    args.parts = _requested_parts(args.part)
    if args.quick:
        # NB: keep --docs (the offline cache is keyed by n); shrink only the
        # expensive induction knobs so a smoke run finishes in seconds.
        args.deduce_edges = 40
        args.deduce_positives = 60
        args.deduce_folds = 2
        args.folds = 2
        args.epochs = 8
        args.no_scramble = True

    out = run(args)
    print(json.dumps(out["acquisition"], indent=2, ensure_ascii=False))
    print()
    for line in out["verdict"]:
        print("  " + line)
    print("\n  wall_seconds=%.1f" % out["wall_seconds"])
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
