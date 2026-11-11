# Release 0.0159 — MLIR-shaped fragment IR and self-host regression (candidate)

- Date: 2026-11-08
- Predecessor: 0.0158. Candidate, not promoted.
- Scope: extend the fresh minimal core with a Maru-native MLIR-shaped IR for
  fragment assembly/matching, then verify the existing functionality through a
  self-host compiler rebuild.
- Analysis: `/research/analysis-mlir-selfhost-0159.md`.

## MLIR-shaped IR

New `src/dlm/mlir.l`:

```text
(ml-module NAME OPS)
(ml-op KIND ARGS)
```

Ops:

```text
fragment id head body
combine  id left right
template id head body
program  id template-ids
task     name facts pos neg align
```

The IR is deliberately **not upstream MLIR**. It preserves Maru self-host and
lowers to the existing `fragment.l / assemble.l / match.l` core.

## REPL experiment

`experiments/mlir_repl/start.l`, launched by `scripts/mlir.sh`:

- 16 module operations
- 5 fragments
- 4 templates
- 3 programs
- 4 fixed tasks

Result:

```text
fragments 5, templates 4, programs 3, tasks 4
selected programs: p-rec, p-comp
tasks solved: 4/4
conflicts: 0
```

`p-rec` is reused for ancestor, reaches and inside; `p-comp` handles path.

## Self-host verification

`scripts/compiler.sh` now verifies the minimal core (not the removed d107 test):

```text
compiler.sh reproduce
compiler.sh verify 20261109T073112Z-22271
```

The verify step runs:

- native core tests through the rebuilt runtime
- the MLIR-shaped experiment through the rebuilt runtime
- asserts `done-mlir` and `tasks 4 solved 4` (not just process exit)
- next-generation and third-generation compiler builds
- LLVM text and stripped binary equality

Result: `Verified: 20261109T073112Z-22271`.

## Measured

```text
native normal   6 checks / 0 FAIL
native safety-2 6 checks / 0 FAIL
self-host       verified (reproduce + verify)
MLIR experiment 4/4 tasks, active 2 programs, conflicts 0
```

## Still not

- This is an internal MLIR-shaped IR, not upstream MLIR/LLVM dialect.
- Fragment ops are declarative and minimal; no full parser/bytecode.
- No provenance/qualifier/negation fields in the IR yet.
- No external MLIR lowering; self-host is preserved by avoiding that dependency.
