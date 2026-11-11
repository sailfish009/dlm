# Release 0.0171 — MLIR-shaped synthesis ops (candidate)

- Date: 2026-11-08
- Predecessor: 0.0170. Candidate, not promoted.
- Scope: express stride and two-predicate synthesis as MLIR-shaped module ops and
  lower them to the existing synth core.
- Analysis: `/research/analysis-synth-mlir-0171.md`.

## Changes

`src/dlm/mlir.l`:

- `synth-seed` — `(ID PRED TARGET STRIDE SUPPORT)` lowers to
  `s-seedk-rule`
- `synth-step` — `(ID PRED TARGET STRIDE SUPPORT)` lowers to `s-reck-rule`
- `synth-pair-seed` — `(ID P Q TARGET SUPPORT)` builds
  `R(x,z) :- P(x,y), Q(y,z)`
- `synth-pair-step` — `(ID P Q TARGET SUPPORT)` builds the recursive pair step
- `synth-program` — `(ID SEED STEP FACTS POS NEG BUDGET)` builds the program,
  evaluates coverage and negative conflict
- `ml-synth-result` — read back `(ID PROGRAM COVERAGE CONFLICT)`

`ml-run` now resets synthesis state and reports a `synth` count after the
existing `run` field.

`scripts/run.sh` loads `synth.l` before `mlir.l`, so MLIR synthesis ops lower to
already-defined synth functions. No forward reference is used.

## Experiment

`experiments/synth_mlir_repl/` + `scripts/synth_mlir.sh` builds two modules:

1. stride-3 `parent/ancestor`
2. two-predicate `up/down` block

and compares each lowered program with the direct synthesizer.

```text
MLIR stride result=1 program=yes
MLIR stride rules=2 coverage=1/1 conflict=clean
DIRECT stride rules=2 coverage=1/1
SAME stride yes
MLIR pair result=1 program=yes
MLIR pair rules=2 coverage=1/1 conflict=clean
DIRECT pair rules=2 coverage=1/1
SAME pair yes
done-mlir-synth
```

## Self-host

```text
compiler.sh reproduce
→ 20261109T090532Z-18554
compiler.sh verify 20261109T090532Z-18554
→ Verified
```

## Measured

```text
native normal   34 checks / 0 FAIL
native safety-2 34 checks / 0 FAIL
self-host       verified
```

## Still not

- Synthesis ops are explicit template ops, not a full pass pipeline.
- No source locations, dialect registry, or upstream MLIR.
- No automatic search lowering: stride/pair selection is still done by the
  direct synthesizer or explicitly chosen in the module.
- Proof checker remains the truth gate; MLIR only structures lowering.
