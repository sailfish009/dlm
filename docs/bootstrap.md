# Compiler evolution as learning

The language/runtime is part of the system under study, not an immutable external
service. DLM proposes revisions; compiler acceptance must use independent evidence.

## Included materials

- vendor/maru: tracked source snapshot, including boot.l, build.l, source, tests,
  platform layers, compiler backends and upstream LICENSE.
- bootstrap/maru.bundle: Git histories of maru.11 and maru.10 needed by upstream
  bootstrap worktrees. A source-only snapshot cannot satisfy those worktree steps.
- bootstrap/maru-seed: previously built eval1, Linux x86-64 LLVM/linux target.
- bootstrap/seed.sha256: checksum, not a proof of trusted provenance.

Runtime source revision: see maru.lock. Building also requires the native host
build tools/LLVM described in vendor/maru/README.md. The historical bootstrap
rebuilds the preceding stage; it does not use the seed as a universal standalone
bootstrap image. No claim of source-only or diverse-double-compilation trust.

## Commands

```sh
./scripts/bootstrap.sh
./scripts/verify-compiler.sh
MARU="$PWD/vendor/maru/build/llvm-linux/x86_64-unknown-linux-gnu/eval2" \
  ./scripts/run.sh repl
```

bootstrap.sh hydrates a local Git repository from the bundled history if needed,
without overwriting working source changes. eval0-phase=false makes bootstrap use
the modified working sources. Generated .git and build directories are ignored.

## Admission protocol (design, not yet autonomous)

1. Retain an immutable baseline source/binary and identify source changes by hash.
2. Apply each proposed patch to a separate candidate checkout, never the active VM.
3. Compile with the baseline bootstrap chain; require eval1/eval2 equality.
4. Run upstream evaluator/compiler regressions and DLM soundness/falsification tests.
5. Compare candidate and baseline on held-out semantic fixtures and equal-budget
   resource measurements. Compilation success or self-consistency is not reward.
6. Record patch, evidence, failures, metrics, before/after source and binary hashes.
7. Explicitly promote by selecting the accepted binary and retain rollback artifacts.

verify-compiler.sh currently provides only bootstrap equality, upstream evaluator
checks and DLM regression checks. It does not implement steps 1/2/5/6/7 or prove
compiler correctness. Run upstream's wider AGENTS.md gate for runtime-wide changes.
Untrusted patches need OS isolation and resource limits, not just Lisp conventions.
