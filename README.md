# DLM v0.0070 -- verified compiler lifecycle

Maru supplies the Lisp runtime/compiler; src/dlm supplies the deductive model.
No vendor directory. Maru's license is LICENSE.maru. No GPU, PyTorch or LLM.

## Run

```sh
./scripts/run.sh test
./scripts/run.sh repl
```

The active maru-compiler is a symlink to a retained release binary. Initial runtime
is included under runtime/releases/initial. DLM code is loaded externally.

## Compiler lifecycle

```sh
ID=$(./scripts/compiler.sh rebuild)     # current source; ordinary seed; Python build tool
# Or: ID=$(./scripts/compiler.sh reproduce)  # active embedded snapshot; no Python
./scripts/compiler.sh verify "$ID"
./scripts/compiler.sh promote "$ID"     # explicit, never automatic
./scripts/compiler.sh rollback
```

rebuild includes current src/maru files and regenerates payloads. reproduce uses
only the active image's embedded generator/snapshot; it does NOT incorporate
external edits. Both use external clang/linker. Verification also needs strip.
The Python payload assembler is build-only, not a DLM runtime dependency.

Each release retains source manifest, parent binary SHA-256, build mode, LLVM,
binary hashes, build/verification logs and a verification marker bound to artifacts
and test inputs. verify performs DLM regressions plus next-generation self-build,
LLVM and stripped-binary equality. promote checks recorded artifacts/test inputs;
rebuild promotion also rejects changed source manifests. Previous runtime is kept
for rollback. These are local integrity checks, NOT signatures or a hostile-code
security boundary. Run candidate code under OS isolation for untrusted patches.

## DLM changes

- Observation revises Experience immediately, preventing queries through stale
  counterexample-invalidated rules before the next learning step.
- Observation conflicting with Ground abstains and preserves prior state.
- Rule/atom/proof shape checks reject tested malformed inputs.
- Bounded derivation exposes complete/incomplete; legacy closure raises on
  incomplete rather than treating exhaustion as false.
- Optional developer reference check: `python tests/differential.py` compares
  20 seeded graph closures, including cycles, to sibling dlm_v0.0066.

Tests cover 22 assertions. This is not full malformed-input validation. Resource
limits still count fixpoint passes, not unifications, CPU instructions or memory;
strict operation/memory budgets remain future work. No persistent model journal,
web loop, autonomous compiler patch learner or independent compiler-performance
benchmark is claimed. Fixed-point equality is reproducibility, not correctness.

## Research boundary

Compiler-source improvement belongs in src/maru; model learning in src/dlm.
A compiler candidate must preserve semantics and improve independently measured
held-out tasks/resources before being called a learning improvement. Current
verification is a regression gate only. DeepLog-style algebra/provenance work is
still pending. Review DLM authorship/license before publishing.
