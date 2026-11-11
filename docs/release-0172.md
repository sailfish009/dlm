# Release 0.0172 — MLIR search + proof pipeline (candidate)

- Date: 2026-11-08
- Predecessor: 0.0171. Candidate, not promoted.
- Scope: move automatic stride/pair **selection** and the held-out **proof gate**
  into MLIR-shaped ops, so the module expresses search → proof rather than only
  explicit seed/step construction.
- Analysis: `/research/analysis-synth-mlir-pipeline-0172.md`.

## Changes

`src/dlm/mlir.l`:

- `synth-search` — `(ID MODE FACTS POS NEG MAXK BUDGET)` selects a program via
  `s-stride-synthesize` or `s-pair-synthesize`
- `synth-proof` — `(ID PROGRAM_ID FACTS GOAL BUDGET)` runs `p-close` and stores
  `proof` or `fail`
- `ml-proof-result` — read back `(ID STATUS)`
- `ml-run` reports both `synth` and `proof` counts

## Experiment

`experiments/synth_mlir_pipeline_repl/` + `scripts/synth_mlir_pipeline.sh`:
the module contains only a search op and two proof ops (held positive, held
negative).

Stride module:

```text
MLIR search stride program=yes rules=2 coverage=1/1 conflict=clean
SAME stride yes
PROOF stride pos=proof neg=fail
MLIR result synth=1 proof=2
```

Pair module:

```text
MLIR search pair program=yes rules=2 coverage=1/1 conflict=clean
SAME pair yes
PROOF pair pos=proof neg=fail
MLIR result synth=1 proof=2
```

## Self-host

```text
compiler.sh reproduce
→ 20261109T091427Z-9099
compiler.sh verify 20261109T091427Z-9099
→ Verified
```

## Measured

```text
native normal   36 checks / 0 FAIL
native safety-2 36 checks / 0 FAIL
self-host       verified
```

## Still not

- `synth-search` is a wrapper around the direct synthesizer; search itself is
  not decomposed into MLIR passes.
- No dialect registry or source locations.
- The module chooses mode `stride` or `pair`; it does not search over modes.
- Proof remains the truth gate; MLIR orchestrates but does not certify truth.
