# Release 0.0232 — Real Web Axiom Decomposition Test

- Date: 2026-11-13
- Predecessor: 0.0231
- Type: candidate research release
- Runtime: `20261113T050935Z-15666`

## What changed

- Added `experiments/real_web_axiom_decomposition/`.
- Input contains actual Wikipedia text samples only (`id,url,text`).
- Gold axioms are authored separately and loaded only after extraction.
- Current Maru `nl-parse` is run on the raw text; no gold fields are provided.
- Metrics and Maru proof gate are evaluator-only.

## Result

```text
TEXT 15 EXTRACTED 4
TP 0 FP 4 FN 21
PRECISION 0/4 RECALL 0/21
GATE FACTS 4 RULES 0 PROOF fail
GOLD-FIELDS-IN-INPUT false
```

The current parser extracts four false candidates and matches none of the 21
hand-authored gold axioms. This is a negative capability result for the current
model on real web text.

## Verification

```bash
cd /research/dlm_v0.0232/experiments/real_web_axiom_decomposition
./run_all.sh
```

and:

```bash
cd /research/dlm_v0.0232
./scripts/verify_release.sh
```

## Limits

- 15 paragraphs, 21 gold axioms; small sample.
- Gold is author-decomposed, not multi-annotator.
- Current extractor is rule-based `nl-parse`; no learned transformer extractor.
- No MLIR.
