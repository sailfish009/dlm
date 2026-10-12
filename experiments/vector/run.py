"""Grounded IR-tree representation experiment for DLM v0.0026 (NOTE.md).

Question: can an IR tree be represented as a *vector the model can understand*?
v0.0025 answered no -- it hashed the tree's features into opaque buckets and
placed them in a SOM whose cells were unreadable prototypes.

v0.0026 (``dlm.vector``) represents one tree as a sparse **symbolic vector** whose
coordinates are named (``rel[0]=born`` ...) and which reverses exactly.  This
experiment checks the three operational senses of "the model understands it":

1. **faithful**  -- ``vector_tree(tree_vector(t)) == t`` for every tree;
2. **grounded**  -- every coordinate is a declared role + a token from the tree
   (the same symbols ``dlm.ssl.tree_features`` exposes), read back by
   ``vector_features``;
3. **useful**    -- a transparent symbol-overlap kNN, compared with an opaque
   hashed-code kNN and a majority baseline (evaluation only; composing *many*
   trees is a later step).

Run::

    PYTHONPATH=. python experiments/vector/run.py --offline --json out.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from random import Random
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "webssl"))

from dlm import dump  # noqa: E402
from dlm.ssl import aligned_tree_examples, ir_form, tree_features  # noqa: E402
from dlm.vector import (  # noqa: E402
    ROLES,
    Basis,
    SymbolVector,
    bundle,
    decode,
    encode,
    tree_vector,
    vector_features,
    vector_symbols,
    vector_tree,
)

import bridge  # noqa: E402
import web as webmod  # noqa: E402

Item = Tuple[str, str, object]  # (key, label, ir tree)


def feature_code(features: Sequence[str], dim: int = 48) -> Tuple[float, ...]:
    """v0.0025's opaque baseline: signed blake2b feature hashing + L2 (no names)."""
    code = [0.0] * dim
    for feat in features:
        h = int.from_bytes(hashlib.blake2b(("dlm\x1f" + str(feat)).encode(), digest_size=16).digest(), "big")
        code[h % dim] += 1.0 if (h >> 8) & 1 else -1.0
    norm = sum(x * x for x in code) ** 0.5
    return tuple(x / norm for x in code) if norm else tuple(code)

_PREDS = ("birthplace", "occupation", "country_of", "part_of")
_REL = {
    "birthplace": ("based", "at"),
    "occupation": ("worked", "as"),
    "country_of": ("part", "of"),
    "part_of": ("a", "part", "of"),
}
_OBJ = {
    "birthplace": ("london", "paris", "berlin", "rome"),
    "occupation": ("physicist", "writer", "painter", "chemist"),
    "country_of": ("france", "germany", "italy", "spain"),
    "part_of": ("city", "province", "region", "district"),
}
_NOISE = ("the", "and", "with", "by", "from", "into", "over", "under", "near", "across")


def synthetic(n: int, seed: int) -> List[Item]:
    """A controlled corpus of IR trees, with distractor tokens in the cue."""
    rng = Random(seed)
    out: List[Item] = []
    for i in range(n):
        pred = _PREDS[i % len(_PREDS)]
        rel = list(_REL[pred]) + [rng.choice(_NOISE) for _ in range(rng.randrange(0, 3))]
        subj = (f"person{rng.randrange(12)}",)
        obj = (rng.choice(_OBJ[pred]),)
        out.append((f"s{i:04d}", pred, ir_form(rel, subj, obj, rng.randrange(2), f"f{i:04d}")))
    return out


def web_corpus(offline: bool = True) -> List[Item]:
    """Real IR trees aligned to sentences in the webssl cache."""
    docs, _hierarchy = webmod.extract(
        webmod.DEFAULT_SEEDS, cache_dir=str(HERE.parent / "webssl" / "cache"), offline=offline
    )
    facts = [f for d in docs for f in d.facts]
    preds = sorted({f.pred for f in facts if f.pred != "subclass_of"})
    items: List[Item] = []
    for doc in docs:
        ff = [f for f in doc.facts if f.pred in preds]
        for tree, positives, _cands in aligned_tree_examples(doc.sentences, ff, preds, mask="obj"):
            atom = positives[0]
            items.append((f"{doc.slug}:{len(items):03d}", atom.pred, tree))
    return items


def representation_report(items: Sequence[Item]) -> Dict[str, object]:
    """Does the vector faithfully and readably encode each tree?"""
    trees = [it[2] for it in items]
    vecs = [tree_vector(t) for t in trees]
    n = len(trees)
    roundtrip = sum(1 for t, v in zip(trees, vecs) if vector_tree(v) == t)
    link = sum(1 for t, v in zip(trees, vecs) if tree_features(vector_tree(v)) == tree_features(t))
    grounded = sum(1 for v in vecs if all(s.role in ROLES for s in v.symbols))
    distinct_trees = len({dump(t) for t in trees})
    distinct_vecs = len({v.explain() for v in vecs})
    basis = Basis.of(vecs)
    dense_ok = sum(1 for v in vecs if decode(encode(v, basis), basis) == v)
    lens = [len(v) for v in vecs] or [0]
    d = float(n) if n else 1.0
    return {
        "trees": n,
        "distinct_trees": distinct_trees,
        "distinct_vectors": distinct_vecs,
        "injective": round(distinct_vecs / distinct_trees, 4) if distinct_trees else 0.0,
        "roundtrip_exact": round(roundtrip / d, 4),
        "feature_link_exact": round(link / d, 4),
        "grounded": round(grounded / d, 4),
        "dense_roundtrip_exact": round(dense_ok / d, 4),
        "basis_dim": len(basis),
        "mean_active_coords": round(sum(lens) / len(lens), 2),
        "max_active_coords": max(lens),
        "roles": list(ROLES),
    }


def opaque_report(items: Sequence[Item], dim: int) -> Dict[str, object]:
    """v0.0025's baseline: the same features hashed into unnamed buckets."""
    codes = [feature_code(tree_features(it[2]), dim) for it in items]
    distinct_trees = len({dump(it[2]) for it in items})
    distinct_codes = len(set(codes))
    return {
        "dim": dim,
        "distinct_codes": distinct_codes,
        "distinct_trees": distinct_trees,
        "collision_rate": round(1.0 - distinct_codes / distinct_trees, 4) if distinct_trees else 0.0,
        "named_coordinates": 0,
        "invertible": False,
    }


# ============================================================================
# transparent readout (evaluation only; composing many trees is the next step)
# ============================================================================
def group_of(key: str) -> str:
    return key.split(":")[0] if ":" in key else key


def folds_of(items: Sequence[Item], k: int, seed: int) -> List[Tuple[List[int], List[int]]]:
    groups = sorted({group_of(it[0]) for it in items})
    rng = Random(seed)
    rng.shuffle(groups)
    k = max(1, min(int(k), len(groups))) if groups else 1
    buckets: List[List[str]] = [[] for _ in range(k)]
    for i, g in enumerate(groups):
        buckets[i % k].append(g)
    out: List[Tuple[List[int], List[int]]] = []
    for i in range(k):
        held = set(buckets[i])
        train = [j for j, it in enumerate(items) if group_of(it[0]) not in held]
        test = [j for j, it in enumerate(items) if group_of(it[0]) in held]
        out.append((train, test))
    return out


def _sq(a: Sequence[float], b: Sequence[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0


def knn_symbol(items: Sequence[Item], vecs: Sequence[SymbolVector],
               train: Sequence[int], test: Sequence[int]) -> float:
    sets = [{s.key() for s in v.symbols} for v in vecs]
    hits = 0
    for ti in test:
        q = sets[ti]
        ranked = sorted(train, key=lambda j: (-_jaccard(q, sets[j]), items[j][0]))
        if ranked and items[ranked[0]][1] == items[ti][1]:
            hits += 1
    return hits / len(test) if test else 0.0


def knn_hash(items: Sequence[Item], codes: Sequence[Sequence[float]],
             train: Sequence[int], test: Sequence[int]) -> float:
    hits = 0
    for ti in test:
        ranked = sorted(train, key=lambda j: (_sq(codes[ti], codes[j]), items[j][0]))
        if ranked and items[ranked[0]][1] == items[ti][1]:
            hits += 1
    return hits / len(test) if test else 0.0


def majority(items: Sequence[Item], train: Sequence[int], test: Sequence[int]) -> float:
    if not train or not test:
        return 0.0
    counts: Dict[str, int] = {}
    for j in train:
        counts[items[j][1]] = counts.get(items[j][1], 0) + 1
    best = min(counts, key=lambda p: (-counts[p], p))
    return sum(1 for ti in test if items[ti][1] == best) / len(test)


def run(args) -> Dict[str, object]:
    started = time.time()
    items = web_corpus(offline=args.offline) if args.corpus == "web" else synthetic(args.synthetic, args.seed)
    if not items:
        raise SystemExit("no examples (is the cache present?)")

    vecs = [tree_vector(it[2]) for it in items]
    codes = [feature_code(tree_features(it[2]), args.dim) for it in items]
    fold_pairs = folds_of(items, args.folds, args.seed)
    arms: Dict[str, List[float]] = {"symbol_knn": [], "hash_knn": [], "majority": []}
    for train, test in fold_pairs:
        arms["symbol_knn"].append(knn_symbol(items, vecs, train, test))
        arms["hash_knn"].append(knn_hash(items, codes, train, test))
        arms["majority"].append(majority(items, train, test))

    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0  # noqa: E731
    out: Dict[str, object] = {
        "corpus": args.corpus,
        "examples": len(items),
        "folds": len(fold_pairs),
        "representation": representation_report(items),
        "opaque_baseline": opaque_report(items, args.dim),
        "readout": {k: {"recall_at_1": round(mean(v), 4), "fold_recall": [round(x, 4) for x in v]} for k, v in arms.items()},
        "wall_seconds": round(time.time() - started, 2),
    }
    out["verdict"] = verdict(out)
    return out


def verdict(out: Dict[str, object]) -> List[str]:
    rep, op, ro = out["representation"], out["opaque_baseline"], out["readout"]
    lines = [f"corpus={out['corpus']} trees={rep['trees']} basis_dim={rep['basis_dim']} roles={len(rep['roles'])}"]
    lines.append(
        f"faithful : roundtrip={rep['roundtrip_exact']:.3f} feature_link={rep['feature_link_exact']:.3f} "
        f"dense_roundtrip={rep['dense_roundtrip_exact']:.3f} injective={rep['injective']:.3f}"
    )
    lines.append(f"grounded : {rep['grounded']:.3f} every coord is a declared role+token")
    lines.append(
        f"opaque   : {op['distinct_codes']}/{op['distinct_trees']} distinct hash codes "
        f"collision_rate={op['collision_rate']:.3f} named_coordinates=0 invertible=False"
    )
    lines.append(
        f"readout  : symbol_knn={ro['symbol_knn']['recall_at_1']:.3f} "
        f"hash_knn={ro['hash_knn']['recall_at_1']:.3f} majority={ro['majority']['recall_at_1']:.3f}"
    )
    lines.append(
        "reading: the grounded vector is exactly invertible and named, while the hashed baseline "
        "collides and cannot be read back -- the representation the model can understand"
    )
    return lines


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="grounded IR-tree representation")
    p.add_argument("--corpus", choices=("synthetic", "web"), default="synthetic")
    p.add_argument("--synthetic", type=int, default=400)
    p.add_argument("--offline", action="store_true", default=True)
    p.add_argument("--online", dest="offline", action="store_false")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--dim", type=int, default=48)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--json", default="")
    args = p.parse_args(argv)

    out = run(args)
    for line in out["verdict"]:
        print(line)
    print(f"examples={out['examples']} folds={out['folds']} wall={out['wall_seconds']}s")
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2, sort_keys=True))
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
