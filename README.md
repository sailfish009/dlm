# DLM 0.0086 — generated nondeterministic programs and recursive self-supervision

Rule-based candidate generation, Screamer-inspired branch execution, native
proof checking and recursive relation learning now share ONE execution loop in
the original Maru REPL. No LLM, neural network or external Screamer runtime.

## One experimental shell entry point

Watch learning in the original native REPL:

```sh
./scripts/recursive-selfssl.sh --demo /tmp/recursive86.sexp
```

Run a finite, durably closed experiment:

```sh
./scripts/recursive-selfssl.sh --demo --rounds 4 --budget 4 /tmp/recursive86.sexp
# Reopen the same store without reinjecting observations:
./scripts/recursive-selfssl.sh --rounds 1 /tmp/recursive86.sexp
```

`--demo` is an explicit two-episode observation fixture, not hidden axioms or
human proof labels. Without it, new stores contain no observations. The loop is
bounded: saturation waits for new evidence and never invents learning progress.
Ctrl-C ends the process; only completed checkpoints are durable.

Interactive commands:

```lisp
(dlm 'pause)
(dlm 'observe 'my-source '((atom edge (a b)) (atom edge (b c)) (atom edge (c d))))
(dlm 'step)
(dlm 'search)                 ; branch records and policy statistics
(dlm 'query 'demo-a '(atom "c77-0" (a c)))
(dlm 'start 1000)
(dlm 'stop)
(dlm 'close)
```

Use `./scripts/recursive-selfssl.sh --help` for interval/budget/round bounds.
The script execs one Maru process, not a Python-driven product loop. Relative
snapshot paths resolve from the caller's working directory.

## What is integrated

```
current observations + learned operators
 -> rule-based candidate pool and symbolic priority
 -> generated (choose ...) program with candidate branches
 -> branch-local certify86 actions and failure/accept results
 -> outcome/work statistics from checked branches, including nonchosen ones
 -> independent recheck of the chosen definition
 -> checkpointed library update
 -> next round generates using earlier learned definitions
```

`accept` alone is provisional and cannot authorize admission. Derived results
are never converted into external observations. Unknown verification remains
retryable; only complete insufficient-reuse results enter the negative cache.
New sessions use explicit `dlm-session86`; old77/83/84/85 stores remain readable.
History replay reconstructs branch execution, policy statistics and stop state.
Previous version directories and user stores are preserved.

Manual mode selection in any normal DLM REPL:

```lisp
(dlm 'search 'nd-cache)       ; generated branches, FIFO proposal order
(dlm 'search 'nd-ucb)         ; generated branches, family UCB proposal order
(dlm 'search 'ucb)            ; prior direct sequential checking control
(dlm 'search 'off)            ; original enumeration
```

The new launcher opts into nd-ucb unless an nd mode is already restored. The
ordinary legacy launcher still defaults to the earlier behavior.

## Evidence and limits

The explicit chain demo learns paths of lengths2,3,4 recursively; later definitions
reference earlier ones. It executes batches of1/3/3 actual branches, collects7
branch labels, and performs10 certification calls including3 admission rechecks.
A fourth step saturates; reopening preserves the next waiting result.

A36-run comparison found the same learned definitions and held-out formal probe
coverage, but generated batches performed more checks and were slower than direct
sequential checking. This is integration evidence, NOT an efficiency promotion.
See [recursive86-design.md](docs/recursive86-design.md) and
[recursive86-experiment.json](docs/recursive86-experiment.json).

Generation remains a bounded binary-relation composition grammar, not arbitrary
program synthesis, natural-language answer generation or web-axiom extraction.
There is no full MCTS, learned neural latent space, registered MLIR dialect,
physical parallel execution or hard per-event time guarantee.

## Verification and self-host

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
./scripts/run.sh test
./scripts/compiler.sh reproduce
./scripts/compiler.sh verify RELEASE_ID
./scripts/compiler.sh promote RELEASE_ID
```

Eight new integration/launcher tests bring the Python suite to89. Kernel,
store/replay, source retraction, capacity/resource boundaries and independent
logic oracles remain enabled. Final release evidence:
[release-0086.md](docs/release-0086.md).

Maru compiler/platform sources are unchanged and retain three-generation
self-reproduction via external clang/linker. Existing Ground82/83 and optional
MLIR-shaped front-end remain available but are not substitutes for this proof
loop. No GitHub commit/push is performed. Older retained documents are historical.
