"""Matched-arm grounding evaluation (v0.0003, branch L4).

Question: does the ~3.5M MeowLLM-arch encoder + CLM-style contrastive head (T2)
ground unseen natural-language paraphrases better than (a) the deterministic T1
grammar and (b) a trivial character-n-gram retrieval baseline?

Design
------
* 4 relations x several surface phrases each. Phrases are split:
  train (T1/T2 see them), val (threshold tuning), test (reported).
* Both halves share ONE candidate atom set (all ordered entity pairs for all
  relations), so no test atom is absent from the index. This removes the
  "unwinnable test item" confound found while building L3.
* Every arm faces the same sentences and the same candidate set. The retrieval
  threshold is chosen on VAL only, then frozen for TEST.

Arms (matched)
--------------
  t1_train    deterministic grammar over TRAIN phrases only (abstains on unseen)
  lexical     char-3gram cosine nearest prototype (no learning)
  t2_trained  encoder + projection head trained end to end on TRAIN pairs
  t2_frozen   same head, encoder frozen at random init (CLM-style control)

Honest reporting: coverage, exact-atom accuracy (overall and when covered),
relation-only accuracy when covered, abstention rate. Ties are ties. No
"advantage" language; 6GB stays a constraint, not a claim.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import torch

from dlm import ByteTokenizer
from dlm.grounding import GrammarGrounder, Pattern
from dlm.grounder_learn import CharNgramGrounder, LearnedGrounder, synthesize_pairs
from dlm.interpreter import parse_atom

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

ENTITIES = ("alice", "bob", "carol", "dave")

# train: seen; val: threshold tuning; test: reported. All keep argument order.
FAMILY: Dict[str, Dict[str, object]] = {
    "parent": {
        "template": "parent({x},{y})",
        "train": ["is {x} a parent of {y}", "{x} is a parent of {y}"],
        "val": ["is {x} the parent of {y}"],
        "test": ["is {x} a parent to {y}", "does {x} have {y} as their child"],
    },
    "grandparent": {
        "template": "grandparent({x},{y})",
        "train": ["is {x} a grandparent of {y}", "{x} is a grandparent of {y}"],
        "val": ["is {x} the grandparent of {y}"],
        "test": ["is {x} a grandparent to {y}", "is {x} the mother or father of a parent of {y}"],
    },
    "ancestor": {
        "template": "ancestor({x},{y})",
        "train": ["is {x} an ancestor of {y}", "{x} is an ancestor of {y}"],
        "val": ["is {x} the ancestor of {y}"],
        "test": ["does {x} come before {y} in the family tree", "is {x} above {y} in the family tree"],
    },
    "sibling": {
        "template": "sibling({x},{y})",
        "train": ["is {x} a sibling of {y}", "{x} is a sibling of {y}"],
        "val": ["is {x} the sibling of {y}"],
        "test": ["is {x} a brother or sister of {y}", "are {x} and {y} siblings"],
    },
}

canon = lambda atom: str(parse_atom(atom))  # noqa: E731


def patterns(rel: str, split: str) -> List[Pattern]:
    spec = FAMILY[rel]
    return [
        Pattern(ph, spec["template"], name=f"{rel}:{split}:{i}")
        for i, ph in enumerate(spec[split])  # type: ignore[arg-type]
    ]


def all_patterns(split: str) -> List[Pattern]:
    out: List[Pattern] = []
    for rel in FAMILY:
        out.extend(patterns(rel, split))
    return out


def pairs_for(split: str, seed: int = 0) -> List[Tuple[str, str]]:
    return synthesize_pairs(all_patterns(split), ENTITIES, seed=seed)


def phrase_label(sentence: str, entities: Sequence[str] = ENTITIES) -> str:
    s = sentence.lower()
    for e in entities:
        s = s.replace(e, "{e}")
    return s


def per_phrase(grounds, pairs) -> Dict[str, Dict[str, float]]:
    groups: Dict[str, list] = {}
    for g, (s, a) in zip(grounds, pairs):
        groups.setdefault(phrase_label(s), []).append((g, (s, a)))
    return {
        ph: metrics([g for g, _ in items], [p for _, p in items])
        for ph, items in groups.items()
    }


def metrics(grounds, pairs) -> Dict[str, float]:
    n = len(pairs)
    cov = sum(g.ok for g in grounds) / n
    exact = sum(g.ok and canon(str(g.atom)) == canon(a) for g, (_, a) in zip(grounds, pairs))
    rel = sum(
        g.ok and parse_atom(str(g.atom)).pred == parse_atom(a).pred
        for g, (_, a) in zip(grounds, pairs)
    )
    return {
        "coverage": round(cov, 4),
        "exact_accuracy": round(exact / n, 4),
        "exact_when_covered": round(exact / max(1, sum(g.ok for g in grounds)), 4),
        "relation_when_covered": round(rel / max(1, sum(g.ok for g in grounds)), 4),
        "abstention_rate": round(1.0 - cov, 4),
    }


def tune_threshold(
    score: Callable[[Sequence[str], float], List],
    val_pairs: List[Tuple[str, str]],
    grid: Sequence[float] = tuple(round(0.05 * i, 2) for i in range(19)),
) -> Tuple[float, Dict[str, float]]:
    """Pick the threshold maximising val exact hits; tie-break to more coverage."""
    sentences = [s for s, _ in val_pairs]
    best, best_key = 0.0, (-1.0, -1.0)
    for th in grid:
        m = metrics(score(sentences, th), val_pairs)
        key = (m["exact_accuracy"], m["coverage"])
        if key > best_key:
            best, best_key = th, key
    return best, metrics(score(sentences, best), val_pairs)


def grammar_scorer(g: GrammarGrounder):
    def score(sentences, threshold=None):
        return [g.ground(s) for s in sentences]
    return score


def learned_scorer(g: LearnedGrounder):
    def score(sentences, threshold):
        return g.ground_batch(list(sentences), threshold=threshold)
    return score


def ngram_scorer(g: CharNgramGrounder):
    def score(sentences, threshold):
        return [g.ground(s, threshold=threshold) for s in sentences]
    return score


def eval_arm(score, test_pairs, threshold) -> Dict[str, object]:
    grounds = score([s for s, _ in test_pairs], threshold)
    return {"threshold": threshold, "test": metrics(grounds, test_pairs),
            "by_phrase": per_phrase(grounds, test_pairs)}


def main() -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=150)
    ap.add_argument("--proj-dim", type=int, default=128)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--quick", action="store_true", help="smoke run: few epochs")
    args = ap.parse_args()
    if args.quick:
        args.epochs = 20

    ARTIFACTS.mkdir(exist_ok=True)
    train_pairs = pairs_for("train")
    val_pairs = pairs_for("val")
    test_pairs = pairs_for("test")
    atoms = sorted({canon(a) for _, a in train_pairs})

    report: dict = {
        "version": "0.0.3",
        "design": "matched-arm paraphrase grounding; threshold tuned on val only",
        "config": {
            "entities": list(ENTITIES),
            "relations": list(FAMILY),
            "n_candidate_atoms": len(atoms),
            "n_train_pairs": len(train_pairs),
            "n_val_pairs": len(val_pairs),
            "n_test_pairs": len(test_pairs),
            "epochs": args.epochs,
            "proj_dim": args.proj_dim,
            "lr": args.lr,
            "seed": args.seed,
        },
        "chance_exact": round(1.0 / len(atoms), 4),
        "majority_relation_accuracy": None,
        "arms": {},
        "timing_seconds": {},
    }

    # majority-relation reference (predict the most common predicate)
    from collections import Counter

    counts = Counter(parse_atom(a).pred for _, a in test_pairs)
    report["majority_relation_accuracy"] = round(counts.most_common(1)[0][1] / len(test_pairs), 4)

    # --- arm: T1 over train phrases -------------------------------------
    t0 = time.time()
    t1 = GrammarGrounder(all_patterns("train"))
    t1_score = grammar_scorer(t1)
    arm = eval_arm(t1_score, test_pairs, None)
    arm["val"] = metrics(t1_score([s for s, _ in val_pairs]), val_pairs)
    report["arms"]["t1_train"] = arm
    report["timing_seconds"]["t1_train"] = round(time.time() - t0, 2)

    # --- arm: lexical control -------------------------------------------
    t0 = time.time()
    lex = CharNgramGrounder(train_pairs)
    lex_th, lex_val = tune_threshold(ngram_scorer(lex), val_pairs)
    arm = eval_arm(ngram_scorer(lex), test_pairs, lex_th)
    arm["val"] = lex_val
    report["arms"]["lexical"] = arm
    report["timing_seconds"]["lexical"] = round(time.time() - t0, 2)

    # --- arms: T2 trained / frozen --------------------------------------
    tokenizer = ByteTokenizer(max_len=64)
    for arm_name, trainable in (("t2_trained", True), ("t2_frozen", False)):
        t0 = time.time()
        torch.manual_seed(args.seed)
        learner = LearnedGrounder(
            tokenizer, proj_dim=args.proj_dim, seed=args.seed,
            trainable_encoder=trainable, pool="mean", causal=False,
        )
        fit = learner.fit(
            train_pairs, epochs=args.epochs, lr=args.lr,
            batch_size=len(train_pairs), seed=args.seed,
        )
        th, val_m = tune_threshold(learned_scorer(learner), val_pairs)
        learner.default_threshold = th
        arm = eval_arm(learned_scorer(learner), test_pairs, th)
        arm["val"] = val_m
        arm["n_trainable_params"] = fit.n_trainable_params
        arm["final_info_nce_loss"] = round(fit.final_loss, 4)
        arm["final_logit_scale"] = round(fit.final_logit_scale, 3)
        report["arms"][arm_name] = arm
        report["timing_seconds"][arm_name] = round(time.time() - t0, 2)
        if arm_name == "t2_trained":
            path = ARTIFACTS / "learned_grounder.pt"
            learner.save(str(path))
            report["saved_model"] = str(path.relative_to(ROOT))

    (ARTIFACTS / "grounding_eval.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    # --- console table ---------------------------------------------------
    rows = [("arm", "thr", "cov", "exact", "exact|cov", "rel|cov", "abstain")]
    for name, a in report["arms"].items():
        m = a["test"]
        rows.append((
            name, "-" if a["threshold"] is None else f"{a['threshold']:.2f}",
            f"{m['coverage']:.3f}", f"{m['exact_accuracy']:.3f}",
            f"{m['exact_when_covered']:.3f}", f"{m['relation_when_covered']:.3f}",
            f"{m['abstention_rate']:.3f}",
        ))
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    for r in rows:
        print("  ".join(c.ljust(widths[i]) for i, c in enumerate(r)))
    print(f"\nchance exact = {report['chance_exact']}, "
          f"majority-relation = {report['majority_relation_accuracy']}")
    print(f"wrote {ARTIFACTS / 'grounding_eval.json'}")
    return report


if __name__ == "__main__":
    main()