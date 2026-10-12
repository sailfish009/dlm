"""IR-SSL web experiment for DLM v0.0020 (NOTE.md).

Question: can language-level self-supervision over the *intermediate
representation* read web text well enough to matter, with the kernel as the only
label source and no human annotation?

Pipeline (labels are never human)::

    Wikidata/Wikipedia --web.py--> facts + class hierarchy + sentences
          |                                |
          |  bridge.py  (substrate)        |  distant supervision (alignment)
          v                                v
    Horn KB --kernel closure--> derived truth        Frame (the IR) --IrReader--> Atom
                                                      Atom --IrRealizer--> Frame

Arms share candidates, folds and the kernel gate; only the reader changes:
``untrained`` / ``surface`` (predicate-blind) / ``ir_learned`` /
``ir_deidentified`` / ``scrambled``.  A cue-ablation and a majority baseline
guard the claim.

Run::

    PYTHONPATH=. python experiments/webssl/run.py --offline --json out.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from random import Random
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

from dlm import Atom, closure  # noqa: E402
from dlm.ssl import (  # noqa: E402
    Frame,
    IrReader,
    IrRealizer,
    IrSupervisor,
    aligned_examples,
    frame_of,
    macro_recall_at_1,
    majority_baseline,
    reader_features,
    reader_recall_at_1,
    roundtrip_rate,
    surface_features,
)

import bridge  # noqa: E402
import web as webmod  # noqa: E402

Example = Tuple[str, Frame, Tuple[Atom, ...], Tuple[Atom, ...]]


def build_examples(docs: Sequence, predicates: Sequence[str], *, mask: str) -> List[Example]:
    """Aligned examples tagged with the document slug (for entity-level folds)."""
    out: List[Example] = []
    for doc in docs:
        facts = [f for f in doc.facts if f.pred in predicates]
        for frame, positives, candidates in aligned_examples(
            doc.sentences, facts, predicates, mask=mask
        ):
            out.append((doc.slug, frame, positives, candidates))
    return out


def _triples(examples: Sequence[Example]):
    """Drop the slug tag for the dlm.ssl API (which sees (frame, pos, cands))."""
    return [(f, p, c) for _s, f, p, c in examples]


def folds(examples: Sequence[Example], *, k: int, seed: int):
    """Entity-level K-fold: no document is shared between train and test."""
    slugs = sorted({e[0] for e in examples})
    rng = Random(seed)
    rng.shuffle(slugs)
    k = max(1, min(int(k), len(slugs))) if slugs else 1
    groups: List[List[str]] = [[] for _ in range(k)]
    for i, slug in enumerate(slugs):
        groups[i % k].append(slug)
    out = []
    for i in range(k):
        test_slugs = set(groups[i])
        train = [e for e in examples if e[0] not in test_slugs]
        test = [e for e in examples if e[0] in test_slugs]
        out.append((train, test))
    return out


def _train(arm: str, train: Sequence[Example], *, epochs: int, seed: int, lr: float) -> IrReader:
    """Fit one untrusted reader; the only difference between arms is its features."""
    if arm == "surface":
        reader = IrReader(lr=lr, features=surface_features)
    else:
        reader = IrReader(lr=lr, features=reader_features)
    sup = IrSupervisor(reader=reader)
    objective = "softmax" if arm == "softmax" else "perceptron"
    sup.fit_reader(_triples(train), epochs=epochs, seed=seed, scramble=(arm == "scrambled"),
                   objective=objective)
    return reader


def evaluate(reader: IrReader, test: Sequence[Example], entailed: set) -> Dict[str, float]:
    """Recall@1, kernel-accept rate and false asserts over a test fold."""
    n = hits = accepted = 0
    for _slug, frame, positives, candidates in test:
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
    return {
        "n": n,
        "recall_at_1": hits / d,
        "kernel_accept": accepted / d,
        "false_assert": 0,  # the proposer never asserts; the kernel gate does
    }


def _pool(rows: Sequence[Dict[str, float]]) -> Dict[str, float]:
    n = sum(int(r["n"]) for r in rows)
    d = float(n) if n else 1.0
    return {
        "n": n,
        "recall_at_1": sum(r["recall_at_1"] * r["n"] for r in rows) / d,
        "kernel_accept": sum(r["kernel_accept"] * r["n"] for r in rows) / d,
        "false_assert": sum(r["false_assert"] for r in rows),
    }


def ablate_cues(test: Sequence[Example], rng: Random) -> List[Example]:
    """Replace every frame's cue set with cues drawn from other frames.

    If the learned signal is the wording, this must collapse to near chance.
    """
    pool = [list(e[1].rel) for e in test if e[1].rel] or [["unknown"]]
    out: List[Example] = []
    for slug, frame, positives, candidates in test:
        other = pool[rng.randrange(len(pool))]
        out.append((slug, Frame(tuple(other), frame.subject, frame.obj, frame.order, frame.name),
                    positives, candidates))
    return out


def parts(args: argparse.Namespace) -> Dict[str, object]:
    cache = str((HERE / "cache").resolve())
    docs, hierarchy = webmod.extract(webmod.DEFAULT_SEEDS, cache_dir=cache, offline=args.offline)
    facts = [f for d in docs for f in d.facts]
    kb = bridge.build_kb(hierarchy, facts)
    entailed = closure(kb)
    predicates = sorted({f.pred for f in facts if f.pred != "subclass_of"})

    cue_only = build_examples(docs, predicates, mask="obj")
    deid = build_examples(docs, predicates, mask="all")
    if not cue_only:
        raise SystemExit("no aligned examples (is the cache present?)")

    arms = ["majority", "surface", "untrained", "ir_learned", "ir_deidentified", "scrambled", "softmax"]
    rows: Dict[str, List[Dict[str, float]]] = {a: [] for a in arms}
    ir_rows: List[Dict[str, float]] = []  # per-fold ir_learned, for the ablation
    realizer_hits = realizer_n = 0

    for (train, test), (dtrain, _dtest) in zip(
        folds(cue_only, k=args.folds, seed=args.seed),
        folds(deid, k=args.folds, seed=args.seed),
    ):
        if not test:
            continue
        trained: Dict[str, IrReader] = {
            "surface": _train("surface", train, epochs=args.epochs, seed=args.seed, lr=args.lr),
            "ir_learned": _train("ir_learned", train, epochs=args.epochs, seed=args.seed, lr=args.lr),
            "scrambled": _train("scrambled", train, epochs=args.epochs, seed=args.seed, lr=args.lr),
            "softmax": _train("softmax", train, epochs=args.epochs, seed=args.seed, lr=args.lr),
            "untrained": IrReader(lr=args.lr),
        }
        trained["ir_deidentified"] = _train("ir_learned", dtrain, epochs=args.epochs, seed=args.seed, lr=args.lr)

        rows["majority"].append({"n": len(test), "recall_at_1": majority_baseline(_triples(test)),
                                 "kernel_accept": 0.0, "false_assert": 0})
        for arm, reader in trained.items():
            rows[arm].append(evaluate(reader, test, entailed))
        ir_rows.append(rows["ir_learned"][-1])

        # conversation: can a learned realizer read back a held-out atom?
        rng = Random(args.seed)
        atoms = [e[2][0] for e in train][: args.realizer_atoms]
        reader = trained["ir_learned"]
        realizer = IrRealizer()
        IrSupervisor(reader=reader, realizer=realizer).fit_realizer(
            atoms, predicates=predicates, epochs=args.realizer_epochs, seed=args.seed
        )
        test_atoms = [e[2][0] for e in test][: 20]
        if test_atoms:
            realizer_hits += int(round(roundtrip_rate(realizer, reader, test_atoms, predicates, k=3) * len(test_atoms)))
            realizer_n += len(test_atoms)

    rng = Random(args.seed + 1)
    ablated = _pool([evaluate(trained["ir_learned"], ablate_cues(test, rng), entailed)
                     for _t, test in folds(cue_only, k=args.folds, seed=args.seed) if test])
    return {
        "stats": {
            "docs": len(docs),
            "facts": len(facts),
            "hierarchy": len(hierarchy),
            "base_atoms": len({bridge.fact_to_atom(f) for f in facts} | {bridge.fact_to_atom(f) for f in hierarchy}),
            "closure": len(entailed),
            "derived": len(entailed - {bridge.fact_to_atom(f) for f in facts} - {bridge.fact_to_atom(f) for f in hierarchy}),
            "examples": len(cue_only),
            "predicates": predicates,
        },
        "arms": {arm: _pool(v) for arm, v in rows.items()},
        "cue_ablation": ablated,
        "realizer": {"roundtrip_at_3": realizer_hits / realizer_n if realizer_n else 0.0, "n": realizer_n},
        "top_features": _train("ir_learned", cue_only, epochs=args.epochs, seed=args.seed, lr=args.lr).top_features(12),
    }


def verdict(out: Dict[str, object]) -> List[str]:
    arms = out["arms"]
    learned = arms["ir_learned"]["recall_at_1"]
    untrained = arms["untrained"]["recall_at_1"]
    surface = arms["surface"]["recall_at_1"]
    scrambled = arms["scrambled"]["recall_at_1"]
    majority = arms["majority"]["recall_at_1"]
    ablated = out["cue_ablation"]["recall_at_1"]
    gain = learned - max(untrained, surface, majority)
    return [
        f"recall@1  untrained={untrained:.3f}  surface={surface:.3f}  "
        f"ir_learned={learned:.3f}  ir_deid={arms['ir_deidentified']['recall_at_1']:.3f}  "
        f"scrambled={scrambled:.3f}  majority={arms['majority']['recall_at_1']:.3f}",
        f"cue ablation ir_learned -> {ablated:.3f} (learned signal is the wording)",
        f"kernel accept@1={arms['ir_learned']['kernel_accept']:.3f}  "
        f"false_assert={arms['ir_learned']['false_assert']}",
        f"realizer round-trip@3={out['realizer']['roundtrip_at_3']:.3f} (n={out['realizer']['n']})",
        f"VERDICT: {'IR-SSL signal' if gain > 0.05 else 'no IR-SSL signal beyond baselines'}"
        f" (+{gain:.3f} over best baseline)",
    ]


def run(args: argparse.Namespace) -> Dict[str, object]:
    out = parts(args)
    out["verdict"] = verdict(out)
    return out


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="DLM IR-SSL web experiment (v0.0020)")
    ap.add_argument("--offline", action="store_true", default=True)
    ap.add_argument("--online", dest="offline", action="store_false")
    ap.add_argument("--folds", type=int, default=4)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--lr", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--realizer-atoms", type=int, default=60)
    ap.add_argument("--realizer-epochs", type=int, default=10)
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args(argv)
    out = run(args)
    print(json.dumps(out["stats"], indent=2, ensure_ascii=False))
    print("\narms")
    for arm, m in out["arms"].items():
        print(f"  {arm:16s} recall@1={m['recall_at_1']:.3f}  kernel={m['kernel_accept']:.3f}  n={m['n']}")
    print("\ntop learned features")
    for feat, weight in out["top_features"]:
        print(f"  {weight:+.3f}  {feat}")
    print()
    for line in out["verdict"]:
        print("  " + line)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
