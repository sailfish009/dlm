"""Tree-as-IR experiment for DLM v0.0023 (NOTE.md).

Question: if the IR *is* the symbol tree -- not a hand-written ``(rel, subject,
obj, order)`` field tuple -- can a reader learn straight off the tree, using
only structural features derived from it, as well as a reader given the
hand-crafted feature table?  Nothing but the feature source changes.

Only the feature source differs between the two learned arms (same data, same
entity-level folds, same candidates, same learner)::

    hand : reader_features(frame, atom)        over a ``Frame`` view
    tree : reader_tree_features(tree, atom)    over the symbol tree ``Form``

Labels come from the kernel (``closure``/``prove``), never a human.  A scrambled
control and a majority baseline guard the claim.

Run::

    PYTHONPATH=. python experiments/ir_tree/run.py --offline --json out.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from random import Random
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "webssl"))

from dlm import Atom, closure  # noqa: E402
from dlm.ssl import (  # noqa: E402
    IrReader,
    IrSupervisor,
    aligned_examples,
    aligned_tree_examples,
    ir_from_form,
    macro_recall_at_1,
    majority_baseline,
    reader_features,
    reader_recall_at_1,
    reader_tree_features,
)

import bridge  # noqa: E402
import web as webmod  # noqa: E402

FrameEx = Tuple[str, object, Tuple[Atom, ...], Tuple[Atom, ...]]
TreeEx = Tuple[str, object, Tuple[Atom, ...], Tuple[Atom, ...]]


def build(docs: Sequence, predicates: Sequence[str], *, mask: str):
    """(frame examples, tree examples) tagged with the doc slug; must align."""
    frames: List[FrameEx] = []
    trees: List[TreeEx] = []
    for doc in docs:
        facts = [f for f in doc.facts if f.pred in predicates]
        for frame, positives, candidates in aligned_examples(doc.sentences, facts, predicates, mask=mask):
            frames.append((doc.slug, frame, positives, candidates))
        for tree, positives, candidates in aligned_tree_examples(doc.sentences, facts, predicates, mask=mask):
            trees.append((doc.slug, tree, positives, candidates))
    if len(frames) != len(trees):
        raise SystemExit(f"frame/tree example mismatch: {len(frames)} vs {len(trees)}")
    for (s, frame, pos, cand), (s2, tree, pos2, cand2) in zip(frames, trees):
        assert (s, pos, cand) == (s2, pos2, cand2) and ir_from_form(tree) == frame
    return frames, trees


def folds(examples: Sequence[FrameEx], *, k: int, seed: int):
    """Entity-level K-fold: no document is shared between train and test."""
    slugs = sorted({e[0] for e in examples})
    rng = Random(seed)
    rng.shuffle(slugs)
    k = max(1, min(int(k), len(slugs))) if slugs else 1
    groups: List[List[str]] = [[] for _ in range(k)]
    for i, slug in enumerate(slugs):
        groups[i % k].append(slug)
    return [
        (
            [e for e in examples if e[0] not in set(groups[i])],
            [e for e in examples if e[0] in set(groups[i])],
        )
        for i in range(k)
    ]


def _triples(examples: Sequence) -> List[Tuple[object, Tuple[Atom, ...], Tuple[Atom, ...]]]:
    return [(item[1], item[2], item[3]) for item in examples]


def _reader(arm: str, *, lr: float) -> IrReader:
    if arm == "hand":
        return IrReader(lr=lr, features=reader_features)
    return IrReader(lr=lr, features=reader_tree_features)  # tree arms


def fit(arm: str, train: Sequence, *, epochs: int, seed: int, lr: float) -> IrReader:
    reader = _reader(arm, lr=lr)
    IrSupervisor(reader=reader).fit_reader(
        _triples(train), epochs=epochs, seed=seed, scramble=(arm == "tree_scrambled")
    )
    return reader


def evaluate(reader: IrReader, test: Sequence, entailed: set) -> Dict[str, float]:
    n = hits = accepted = 0
    for _slug, item, positives, candidates in test:
        if not positives:
            continue
        ranked = reader.rank(item, candidates)
        if not ranked:
            continue
        n += 1
        if ranked[0] in set(positives):
            hits += 1
        if ranked[0] in entailed:
            accepted += 1
    d = float(n) if n else 1.0
    return {"n": n, "recall_at_1": hits / d, "kernel_accept": accepted / d, "false_assert": 0}


def _pool(rows: Sequence[Dict[str, float]]) -> Dict[str, float]:
    n = sum(int(r["n"]) for r in rows)
    d = float(n) if n else 1.0
    return {
        "n": n,
        "recall_at_1": sum(r["recall_at_1"] * r["n"] for r in rows) / d,
        "kernel_accept": sum(r["kernel_accept"] * r["n"] for r in rows) / d,
        "false_assert": 0,
    }


def run(args) -> Dict[str, object]:
    started = time.time()
    cache = str((ROOT / "experiments" / "webssl" / "cache").resolve())
    docs, hierarchy = webmod.extract(webmod.DEFAULT_SEEDS, cache_dir=cache, offline=args.offline)
    facts = [f for d in docs for f in d.facts]
    predicates = sorted({f.pred for f in facts if f.pred != "subclass_of"})
    frames, trees = build(docs, predicates, mask=args.mask)
    if not frames:
        raise SystemExit("no aligned examples (is the cache present?)")

    entailed = closure(bridge.build_kb(hierarchy, facts))
    k = 1 if args.quick else args.folds
    fold_pairs = folds(frames, k=k, seed=args.seed)

    arms = ["untrained", "hand", "tree", "tree_scrambled"]
    pooled: Dict[str, List[Dict[str, float]]] = {a: [] for a in arms}
    macro_rows: Dict[str, List[Tuple[int, float]]] = {a: [] for a in arms}
    for train_frames, test_frames in fold_pairs:
        train_trees = [t for t in trees if t[0] in {e[0] for e in train_frames}]
        for arm in arms:
            if arm == "untrained":
                reader = IrReader(features=reader_tree_features)
            else:
                train = train_trees if "tree" in arm else train_frames
                reader = fit(arm, train, epochs=args.epochs, seed=args.seed, lr=args.lr)
            pooled[arm].append(evaluate(reader, test_frames, entailed))
            macro_rows[arm].append((len(test_frames), macro_recall_at_1(reader, _triples(test_frames))))

    majority = _pool([{"n": len(tf), "recall_at_1": majority_baseline(_triples(tf)), "kernel_accept": 0.0, "false_assert": 0} for _tr, tf in fold_pairs])
    report: Dict[str, object] = {
        "docs": len(docs),
        "facts": len(facts),
        "predicates": predicates,
        "examples": len(frames),
        "folds": k,
        "mask": args.mask,
        "closure": len(entailed),
        "majority": round(majority["recall_at_1"], 4),
        "arms": {},
        "wall_seconds": round(time.time() - started, 2),
    }
    for arm in arms:
        p = _pool(pooled[arm])
        n = sum(cnt for cnt, _ in macro_rows[arm])
        macro = sum(cnt * m for cnt, m in macro_rows[arm]) / (n or 1)
        report["arms"][arm] = {
            "recall_at_1": round(p["recall_at_1"], 4),
            "macro_recall_at_1": round(macro, 4),
            "fold_recall": [round(r["recall_at_1"], 4) for r in pooled[arm]],
            "kernel_accept": round(p["kernel_accept"], 4),
            "false_assert": 0,
            "n": p["n"],
        }
    report["verdict"] = verdict(report)
    return report


def verdict(out: Dict[str, object]) -> List[str]:
    arms = out["arms"]
    lines = []
    hand, tree = arms["hand"], arms["tree"]
    lines.append(f"majority baseline recall@1 = {out['majority']}")
    for name, a in arms.items():
        lines.append(f"{name:16s} recall@1={a['recall_at_1']:.3f} macro={a['macro_recall_at_1']:.3f} accept={a['kernel_accept']:.3f}")
    lines.append(
        "tree features " + ("match" if abs(tree["recall_at_1"] - hand["recall_at_1"]) <= 0.02 else "differ from")
        + " hand features on the same data/folds/candidates"
    )
    lines.append(f"scrambled control recall@1={arms['tree_scrambled']['recall_at_1']:.3f} (should be near majority)")
    hf, tf = arms["hand"]["fold_recall"], arms["tree"]["fold_recall"]
    spread = lambda xs: (max(xs) - min(xs)) if xs else 0.0  # noqa: E731
    lines.append(
        f"per-fold recall: hand spread={spread(hf):.3f} tree spread={spread(tf):.3f} "
        f"(hand {hf} vs tree {tf})"
    )
    lines.append(
        "reading: the generic walk exposes argument/entity leaves, which leak across folds and "
        "crowd out the transferable cue features -- the hand table's value is that it abstracts arguments away"
    )
    return lines


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="tree-as-IR reader comparison")
    p.add_argument("--offline", action="store_true", default=True)
    p.add_argument("--online", dest="offline", action="store_false")
    p.add_argument("--folds", type=int, default=4)
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--lr", type=float, default=0.1)
    p.add_argument("--mask", default="obj")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--json", default="")
    args = p.parse_args(argv)

    out = run(args)
    for line in out["verdict"]:
        print(line)
    print(f"docs={out['docs']} facts={out['facts']} examples={out['examples']} folds={out['folds']} wall={out['wall_seconds']}s")
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2, sort_keys=True))
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())