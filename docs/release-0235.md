# Release 0.0235 — Decomposition Stage 0

- Date: 2026-11-13
- Predecessor: 0.0234
- Type: candidate research release
- Runtime: `20261113T093958Z-17955`

## What changed

- Added `experiments/decomposition_stage0/`:
  - text-only web input and evaluator-only gold;
  - span n-gram generator;
  - full-predicate and web-derived-predicate candidate spaces;
  - predicate coverage, span coverage and candidate recall;
  - oracle upper bound.

## Result

```text
WEB 15 SPANS 39 PREDS-FULL 11 PREDS-WEB 1
GOLD 22 CANDIDATE-SPACE-FULL 16731
PRED-COVERAGE-FULL 22/22 PRED-COVERAGE-WEB 6/22
SPAN-COVERAGE 0/22
CANDIDATE-RECALL-FULL 0/22 CANDIDATE-RECALL-WEB 0/22
ORACLE-SPAN-PRED 22/22 (upper bound)
```

Stage 0 diagnoses the bottleneck: predicate inventory is sufficient, but the
current text-span generator recovers none of the gold subject/object spans.
The oracle upper bound is 22/22, so the loss is in candidate generation, not
the kernel or predicate vocabulary.

## Verification

```bash
cd /research/dlm_v0.0235/experiments/decomposition_stage0
./run_all.sh
```

and:

```bash
cd /research/dlm_v0.0235
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

## Limits

- Span generator is naive n-grams; normalization is insufficient.
- No ranking/training yet.
- Gold is author-decomposed.
- MLIR not used.
