# DLM 0.0081 implementation status

## Implemented

- Optional MLIR-shaped SSA front-end: `adapters/space_dialect.py`.
- Structural verifier, conservative effect metadata, canonical text formatter,
  whitelisted Maru lowering and CLI execution: `scripts/dialect.sh`.
- Runnable example: `experiments/space/dialect.mlir`.
- Seven new tests, including direct-vs-lowered entire persistent state comparisons
  and 30 seeded event slices: `tests/test_space_dialect.py`.
- Existing Maru direct-execution path, proof kernel and source tree unchanged.
- Prior version directory `/research/dlm_v0.0080` preserved.

## Verified

Release `20261022T023153Z-6952`, reproduced from active Maru and promoted after
`compiler.sh verify` passed. Full evidence is `docs/verification.log` and
`runtime/releases/20261022T023153Z-6952/verify.log`.

- 55 Python tests passed in 78.762 seconds.
- Native, store, runtime and graph-store suites passed.
- Optional sibling0066 Horn/graph differential oracles passed.
- Candidate/next/third LLVM outputs matched.
- Candidate/next/third stripped executable images matched.
- `src/maru` matches v0.0080 exactly; no external MLIR dependency in bootstrap.

Source/test manifests: `docs/release.sources.sha256`,
`docs/release.tests.sha256`. Extra dialect/example manifest:
`docs/dialect.sources.sha256` (the inherited compiler manifest glob excludes
`.mlir` examples).

## Not implemented — important scope limitation

This is **not yet the requested native LLVM MLIR dialect implementation**.
There is no registered dialect, TableGen ODS, MLIR plugin/toolchain build,
MemoryEffectOpInterface, typed region/control-flow representation or MLIR pass.
There is also no independent reference event interpreter: Maru supplies semantics;
translation tests compare manually written direct calls with lowered calls.
No snapshot↔dialect codec, optimizer, or automatic trace equivalence proof is
claimed. The `!space79.space` type currently carries the whole state, not separate
unit/job/certificate types.

See `docs/space-dialect.md` for the concrete grammar, resource contracts and
remaining steps. Existing self-host is preserved; the optional Python adapter
itself is not self-hosted.

Earlier review/evidence and implementation documents retained in this directory
are historical v0.0079/v0.0080 records. This release note and the current verified
release logs identify what was checked for v0.0081.
