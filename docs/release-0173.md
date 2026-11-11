# Release 0.0173 — MLIR automatic mode selection (candidate)

- Date: 2026-11-08
- Predecessor: 0.0172. Candidate, not promoted.
- Scope: remove the requirement to name `stride` or `pair` in the MLIR module.
  `synth-search` mode `auto` evaluates both and records the selected mode.
- Analysis: `/research/analysis-synth-mlir-auto-0173.md`.

## Changes

`src/dlm/mlir.l`:

- `synth-search` accepts mode `auto`
- `ml-synth-quality` evaluates coverage and negative conflict
- `ml-synth-mode` reads the selected mode
- synthesis results now carry a fifth field: `explicit`, `stride`, or `pair`
- selection prefers higher coverage, then a clean negative state

`experiments/synth_mlir_auto_repl/` + `scripts/synth_mlir_auto.sh`.

## Experiment

Two modules, both with mode `auto`:

1. single-predicate parent chain
2. alternating `up/down` chain

```text
AUTO parent mode=stride coverage=1/1 rules=2
AUTO parent same-stride yes
AUTO alt mode=pair coverage=1/1 rules=2
AUTO alt same-pair yes
done-mlir-auto
```

The module no longer chooses the synthesis family; the `synth-search` op does.

## Self-host

```text
compiler.sh reproduce
→ 20261109T092340Z-21415
compiler.sh verify 20261109T092340Z-21415
→ Verified
```

## Measured

```text
native normal   38 checks / 0 FAIL
native safety-2 38 checks / 0 FAIL
self-host       verified
```

## Implementation note

Maru does not accept `#t`; the true branch uses `(not ())`. An earlier
explicit-pair path also selected the empty stride candidate; selection now uses
an explicit `pick-pair` branch.

## Still not

- `auto` chooses between two named modes; it does not invent a new synthesis
  family.
- No dialect registry, source locations, or decomposed pass pipeline.
- Proof remains the truth gate.
