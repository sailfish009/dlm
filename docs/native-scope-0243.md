# Native scope — 0.0243

Release 0.0243 states a **scoped** native claim. This file defines the scope, so
the claim is checkable instead of rhetorical.

## In scope (PyTorch-free, native)

```text
src/dlm/*.l              trusted symbolic core (Maru)
src/maru/**              compiler/runtime sources
tests/core-tests.l       native core assertions
scripts/*.sh             release gates and experiments (Maru + shell)
experiments/native_integral/  C/LLVM IR kernel + Maru oracles (no Python)
experiments/teacher_transformer_repl/teacher_data.l
                         FROZEN observation artifact; verified by Maru only
```

Release verification (`scripts/verify_release.sh`) runs only this set plus the
frozen teacher data. It does **not** import Python packages beyond the standard
library (`python3` adapters under `adapters/` that use only stdlib are used by
web/axiom experiments that are not part of the release gate) and it does **not**
import torch. `scripts/teacher_transformer.sh` used to run a PyTorch model; since
0.0243 it verifies the frozen `teacher_data.l` with Maru, and the torch
regeneration lives in `scripts/teacher_transformer_generate.sh` (provenance
tooling, never a gate).

Checks in `scripts/verify_release.sh`:

```text
NATIVE-SCOPE-PASS   release sources import no torch (grep over the manifest)
SCOPE torch_files_outside_native_scope=<n> pinned by docs/research-snapshots.sha256
VERSION-MATCH       VERSION == capabilities.json version
```

## Out of scope (research snapshots, kept but not claimed)

These files import torch and are inherited research snapshots. They are pinned
in `docs/research-snapshots.sha256` (so they cannot drift silently), are not in
`docs/release.sources.sha256`, and are not executed by any release gate.

```text
adapters/teacher_transformer.py            offline teacher-data generator
experiments/tiny_transformer_maru/*.py     Q16 transformer port reference
experiments/dt1_*/*.py, experiments/dt4_selector/run.py,
experiments/dt5_query/run.py               DT selector prototypes
experiments/dt_full_port_no_mlir/*.py      DT port trainer
experiments/web_axiom_transformer_lab/proposer.py
experiments/m1_proof_state/*.py, experiments/m3_selfssl/*.py
```

Removed from the tree in 0.0243 as superseded (`experiments/structure_discovery/`
and `experiments/integral_learning/`, both PyTorch labs from 0.0239/0.0241).
They remain in their own worktrees.

## Why the split

The 0.0242 review found that the release *gate* itself required torch
(`scripts/compiler.sh verify` called the torch adapter), so a machine without
torch could not verify the release, even though the headline lab was native.
0.0243 fixes the gate and pins the boundary instead of claiming the whole tree.