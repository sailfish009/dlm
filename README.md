# DLM v0.0069 -- embedded Maru compiler baseline

No vendor directory. Maru sources are in src/maru; model code is in src/dlm.
Maru's license is LICENSE.maru at the source root.

```sh
./scripts/run.sh repl
./scripts/run.sh test
./scripts/build.sh
./scripts/verify-compiler.sh
```

## Layout

- maru-compiler: Linux x86-64 evaluator with 57 baseline Maru Lisp payloads inside.
- src/maru/: minimal self-compile source set, including the experimental native
  memory-stream loader in source/evaluator/vm-with-file-support.l.
- src/dlm/: deduction, proof checking, learning, Experience, model REPL operations.
- bootstrap/maru-seed: ordinary evaluator for rebuilding modified embedding code.
- scripts/: compile/link, explicit rebuild, regression and payload verification.
- tests/: 15 DLM assertions plus demo.
- LICENSE.maru: upstream Maru license; NOTICE explains provenance.

## Execution vs rebuilding

REPL and DLM execution load boot.l from the binary; no external Maru Lisp files
are needed at runtime. DLM files remain external and use safe file fallback when
not present in the embedded baseline. Example:

```lisp
(dlm-status)
(define facts (list (dlm-atom 'edge 'a 'b) (dlm-atom 'edge 'b 'c)))
(define target (dlm-atom 'reach 'a 'c))
(dlm-observe (list (dlm-episode 'user facts (list target) ())))
(dlm-learn 64)
(dlm-ask target)
```

The compiler Lisp is interpreted from embedded payloads, not natively compiled
compiler functions. Current source contains a frozen baseline payload table.
Changes to external compiler files are NOT automatically incorporated into that
table. The modified loader's source can be rebuilt using the ordinary seed.
Do not confuse this with autonomous compiler-source learning or a fully
self-reproducing embedded compiler image: neither is implemented.

build.sh explicitly replaces maru-compiler after a successful compilation;
verify-compiler.sh does not promote anything. Back up accepted binaries before
experiments. A staged regression-gated promotion/rollback mechanism is pending.

## Verification

verify-compiler.sh runs the embedded compiler from an empty source directory,
emits the baseline LLVM twice, compares LLVM and stripped executable bytes,
and runs DLM tests on the embedded runtime. This proves deterministic embedded
baseline compilation, NOT reproduction of the modified compiler-image itself.

Building requires clang/linker; verification requires strip. Scripts use bash
and coreutils. No Python/PyTorch/GPU/LLM is needed to execute or build this release.
The runtime is not a hostile-code sandbox. DLM has no persistent journal or web
learning loop; fixpoint limits count passes rather than instructions.

The initial 57-file source set was 327466 bytes. Embedding those payloads in a
source table increases source size; fewer external files does not imply a smaller
implementation. License and DLM authorship must be reviewed before publication.
