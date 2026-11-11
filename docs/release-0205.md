# Release 0.0205 — sanitized release packaging

- Date: 2026-11-11
- Predecessor: 0.0204 (candidate)
- Type: packaging / release-preparation release
- Runtime: built from this 0.0205 source tree, self-host verified.

## What changed

- Version bumped to 0.0205.
- Release metadata made consistent:
  - `VERSION` = 0.0205
  - `docs/release.txt` = the runtime built from this tree
  - `maru-compiler` points at that runtime
- Added `scripts/verify_release.sh` for a fresh-tree check:
  - version/symlink consistency
  - no files > 5 MB outside `runtime/`
  - native core tests
  - self-host verify of the recorded runtime
- Added a release `.gitignore`:
  - only one promoted runtime under `runtime/`
  - no MNIST `.npz`, checkpoints, caches, debug dumps, or per-run logs
- Added the DT × MNIST research snapshot as code + small results:
  - `experiments/deductive_transformer_maru/`
  - `experiments/tiny_transformer_maru/`
  - large data/checkpoints are intentionally excluded and must be regenerated.

## Verification

```text
./scripts/verify_release.sh
VERSION=0.0205 RUNTIME=20261111T094802Z-19215
runtime symlink: ok
tree size: ok
ALL-CORE-TESTS-PASSED
Verified: 20261111T094802Z-19215
RELEASE-VERIFY-PASS version=0.0205 runtime=20261111T094802Z-19215
```

## Still not

- DT × MNIST 9/10 is a research result, not a core claim.
- Training uses MNIST labels as observations; no label-free deductive learning.
- Case 0 ceiling: perception + rule-pool failure.
- No `runtime/safety2` or `runtime/previous` in the release.

## Merge note (important)

This 0.0205 tree is the **minimal-core line** (0.0204 lineage). It is not a
superset of the current git `main` 0.0120:

- 0.0120 `scripts/run.sh` loads 13 `src/dlm/d107-*.l` contract-layer files;
- 0.0205 has no `d107-*.l` and loads the 0.0204 proof/axiom/DT core instead.

Therefore a blind `rsync --delete` into `main` would delete the d107 contract
layer and its tests. Do not replace `main` until one of these is chosen:

1. publish 0.0205 as a new minimal-core release (intentional d107 removal), or
2. port/merge d107 into 0.0205 and re-run both test suites, or
3. keep `main` 0.0120 and publish 0.0205 separately.

Recommended: option 2 if d107 is still a supported capability; otherwise option 1
with an explicit release note. The staging tree has been verified only as a
standalone 0.0205 tree.

## A-variant decision (minimal core)

Chosen: publish 0.0205 as a **new minimal-core release**. The 0.0120 d107
contract layer is intentionally removed, not merged.

Breaking changes:

- no `src/dlm/d107-*.l`;
- no d107 contract/unit/surface/plan/session modules;
- no d107 tests;
- `scripts/run.sh` loads the 0.0204 proof/axiom/DT core instead.

Historical 0.0120 documentation is kept as `docs/README-0120.md`; it does not
describe the 0.0205 runtime.
