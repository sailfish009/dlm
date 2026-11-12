# Release 0.0226 — Maru-Native Web → Axiom Transformer

- Date: 2026-11-12
- Predecessor: 0.0225
- Type: candidate research release
- Runtime: `20261112T101258Z-31878`

## What changed

- Added `experiments/maru_web_axiom_transformer_lab/`:
  - static web observations;
  - Maru-native word tokenization and one-hot Q16 token vectors;
  - existing Q16 `dt.l` transformer block applied to text+candidate tokens;
  - exact baseline extractor and Maru proof gate.
- No Python is used in the lab.

## Result

```text
TRANSFORMER_TOP1 0/4
BASELINE_TOP1 4/4
GATE FACTS 6 RULES 2 PROOF proof
```

The Maru-native Q16 transformer did not generalize to held-out text
candidates. The exact baseline and Maru gate work.

## Verification

```bash
cd /research/dlm_v0.0226/experiments/maru_web_axiom_transformer_lab
./run_all.sh
```

and:

```bash
cd /research/dlm_v0.0226
./scripts/verify_release.sh
```

## Limits

- The transformer uses one Q16 block and an untrained/text-mismatched model;
- token vectors are one-hot lexical hashes, not a learned tokenizer;
- 4/4 split is tiny;
- this is a Maru-native negative result, not an extraction claim;
- MLIR not used.
