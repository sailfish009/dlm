# array_view_join_maru (DLM v0.0216)

Maru array-view ABI + persistent C/LLVM indexed join.

## Source

In this tree:

- `src/maru/source/c/array_view.h`
- `src/maru/source/c/array_view_join.c`
- `src/maru/source/evaluator/arrays.l` (VM wrappers)
- `src/maru/tools-for-build/build-compiler-image.sh` (compiles/links C)

Runtime release:

```text
20261112T064515Z-17410
```

## Self-host verify

```bash
cd /research/dlm_v0.0216
./scripts/compiler.sh verify 20261112T064515Z-17410
```

## Verify

```bash
cd /research/dlm_v0.0216/experiments/array_view_join_maru
./verify_v0216.sh
```

Expected:

```text
V0216-ARRAY-VIEW-JOIN-PASS
V0216-ALL-PASS
```

## Files

- `src/aj_common.l` — fixture and pure Maru reference join.
- `src/array_join.l` — full correctness checks.
- `src/ref_only.l`, `src/join_only.l` — timing slices.
- `c/` — ABI, C kernel and standalone C benchmark.
- `docs/array-view-abi.md` — ABI and detailed results.

The experiment scripts use the tree's `maru-compiler` symlink by default and
can be overridden with `MARU=/path/to/maru`.
