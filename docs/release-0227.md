# Release 0.0227 — Integrity-First Web Text → Axiom Extraction Benchmark

- Date: 2026-11-12
- Predecessor: 0.0226
- Type: candidate research release
- Runtime: `20261112T102838Z-27336`

## What changed

- Added `experiments/web_text_extraction_benchmark/`:
  - input text only (`id`, `url`, `text`); no subj/obj/kind/gold fields;
  - gold in a separate evaluator-only file;
  - actual `nl-parse` baseline over the text;
  - distractor documents that produce false candidates;
  - TP/FP/FN, precision/recall and Maru proof gate.
- Removed the fake `gold==gold` baseline and the field-copying path from the
  benchmark.

## Result

```text
TEXT 11 EXTRACTED 11
TP 8 FP 3 FN 0
PRECISION 8/11 RECALL 8/8
GATE FACTS 9 RULES 2 PROOF proof
GOLD-FIELDS-IN-INPUT false
```

The extractor is the actual Maru text parser. The three distractor documents
produce false positives, so precision is measured rather than tautological.

## Verification

```bash
cd /research/dlm_v0.0227/experiments/web_text_extraction_benchmark
./run_all.sh
```

and:

```bash
cd /research/dlm_v0.0227
./scripts/verify_release.sh
```

## Limits

- Small hand-written corpus; no live fetch.
- No transformer extraction yet; this version establishes a valid benchmark.
- The parser is rule-based; MLIR is not used.
