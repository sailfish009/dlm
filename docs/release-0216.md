# Release 0.0216 — Maru array-view C/LLVM backend

- Date: 2026-11-12
- Predecessor: 0.0205 minimal core
- Type: candidate feature release
- Runtime: built from this 0.0216 source tree; self-host verified.

## What changed

- Added a reusable array-view ABI:
  `src/maru/source/c/array_view.h`.
- Added a C/LLVM indexed-join kernel:
  `src/maru/source/c/array_view_join.c`.
- Compiler image build now compiles and links the array-view kernel in
  `rebuild` and self-host `verify` paths.
- Added VM wrappers in `src/maru/source/evaluator/arrays.l`:

```lisp
(mb-index-build block n stride elem maxkey)
(mb-index-size handle)
(mb-join-many handle left n stride elem reps)
(mb-join-checksum handle left n stride elem reps)
(mb-index-free)
```

- Added `experiments/array_view_join_maru/` with:
  - pure Maru reference join;
  - C indexed-join parity;
  - standalone C benchmark;
  - rerunnable verification.

## Correctness

Fixture: 300 keys/relation, keys `0..31`, 4096 repetitions.

```text
REF        2820
REFSUM     421590
SIZE       300
JOIN1      2820
JOIN64     180480
JOIN4096   11550720
CHECK1     421590
CHECK64    26981760
AFTERFREE  -1
```

## Performance

Standalone C `-O3`:

```text
C-BUILD      0.000007 s
C-JOIN4096   0.000701 s
C-CHECK4096  0.004263 s
```

Maru end-to-end (startup ~62 ms):

```text
ref only     ~167-179 ms
build only   ~61-63 ms
join4096     ~67-70 ms
```

## Verification

```bash
./scripts/verify_release.sh
VERSION=0.0216 RUNTIME=20261112T064515Z-17410
ALL-CORE-TESTS-PASSED
Verified: 20261112T064515Z-17410
RELEASE-VERIFY-PASS version=0.0216 runtime=20261112T064515Z-17410
```

Array-view check:

```bash
cd experiments/array_view_join_maru
./verify_v0216.sh
V0216-ARRAY-VIEW-JOIN-PASS
V0216-ALL-PASS
```

## Scope / limits

- Keys in this release are byte elements (`elem_size=1`); the getter accepts
  1/2/4/8-byte elements for future kernels.
- Static index limits: `n <= 4096`, `maxkey <= 256`.
- The C kernel accelerates search/scoring. The Maru proof checker remains the
  truth gate.
- This is a candidate; it is not a promoted release.
- The historical 0.0205 release note remains in `docs/release-0205.md`.
