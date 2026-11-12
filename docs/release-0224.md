# Release 0.0224 — Web Knowledge → Axiom Transformer Probe

- Date: 2026-11-12
- Predecessor: 0.0223
- Type: candidate research release
- Runtime: `20261112T093428Z-12672`

## What changed

- Added `experiments/web_axiom_transformer_lab/`:
  - cached MNIST-related web observations;
  - a tiny PyTorch transformer candidate proposer (untrusted adapter);
  - a baseline exact extractor;
  - a Maru-side provenance/NL/proof gate.
- The transformer is trained on four observations and tested on four held-out
  observations. It is a probe, not a production extractor.

## Result

```text
TRANSFORMER_TOP1 0/4
BASELINE_TOP1 4/4
GATE OBS 4 FACTS 2 RULES 2 RULES-USED 2 PROOF proof
```

The transformer did not generalize to the held-out observations. The
rule-based baseline did. This is an honest negative result for the transformer
proposer; the Maru gate succeeds on the baseline candidates.

## Verification

```bash
cd /research/dlm_v0.0224/experiments/web_axiom_transformer_lab
./pipeline.sh
```

and:

```bash
cd /research/dlm_v0.0224
./scripts/verify_release.sh
```

## Limits

- Transformer training is PyTorch adapter-only; the DLM core remains Maru.
- Tiny fixture: 8 observations, 4 train / 4 test.
- Baseline is rule-based exact extraction.
- The transformer candidate gate is not yet used for truth.
- MLIR is not used.
