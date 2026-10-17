# DLM v0.0067 -- Maru-native deductive model

Maru provides the Lisp language, evaluator, compiler and REPL. DLM adds only
model-specific deduction, proof checking, rule search and Experience lifecycle.
No Python, PyTorch, GPU or LLM service is required by this runtime.

## Run

```sh
cd /research/dlm_v0.0067
./scripts/run.sh test
./scripts/run.sh repl
```

Defaults: vendored `vendor/maru` sources and `bootstrap/maru-seed` evaluator.
Set `MARU_HOME` and `MARU` to override these paths. The launcher loads
Maru's own `boot.l` from its checkout, then the DLM modules by absolute path.
`dlm.l` is an alternative relative-path module manifest, for loading from this
project root after Maru has been booted.

## REPL example

```lisp
(define facts (list (dlm-atom 'edge 'a 'b) (dlm-atom 'edge 'b 'c)))
(define target (dlm-atom 'reach 'a 'c))
(dlm-observe (list (dlm-episode 'user facts (list target) ())))
(dlm-learn 64)
(dlm-ask target)
(dlm-status)
```

`confirmed` is supplied supervision, not a fact automatically added to closure.
`dlm-ask` returns a verified proof with its episode source or `unknown`.
It does not interpret unrestricted natural language or return false for unknown.

## Layout

- `src/kernel.l`: explicit variables, matching, safe Horn rules, fixpoint, proofs.
- `src/learning.l`: three candidate families, routing and finite-evidence evaluation.
- `src/experience.l`: pure model state, Ground/Experience, revision, transitions.
- `src/dialogue.l`: model operations on Maru's existing REPL.
- `tests/`: kernel/demo and model lifecycle tests.
- `maru.lock`: validated upstream revision and build configuration.

The v0.0066 Python implementation is a design/reference baseline, not a runtime
dependency. This is a scoped port, not feature parity. In particular, its web
acquisition, sparse learned scorer, journals and mechanism discovery are not ported.

## Trust and limits

Finite-evidence rules enter Experience, never Ground. Explicit counterexamples
retract conflicting Experience. Ground conflict abstains. Commit recomputes a
proposal against its before-state. Ordinary Lisp programs still have Maru's full
mutation authority: this is NOT a sandbox or a malicious-code security boundary.

Closure currently uses full relational joins, not indexed semi-naive execution.
A pass limit raises an error; it is not a VM instruction/memory budget. Proof
verification has a depth limit. Inputs are assumed to be well-formed finite
acyclic list values; hostile/malformed-input validation remains future work.
State/history are in memory only. An observation must be followed by a learning
step to retract Experience invalidated by new counterevidence.

DeepLog's algebraic separation is the next research direction: Boolean truth,
tropical cost and provenance must remain distinct. No probability or fuzzy truth
is inferred from counting derivations. Algebraic circuits are not yet implemented.

## Upstream policy

General Lisp/runtime improvements belong in the vendored Maru sources. Deductive
semantics and learning belong in DLM src. Compiler revision is part of the intended
learning loop: propose source patch, build in an isolated candidate tree, run gates,
measure held-out improvement, then explicitly promote. Self-hosting alone is not
correctness evidence. See docs/bootstrap.md. No autonomous patch proposer or
promotion policy is implemented yet.

## Distribution

Maru source and its LICENSE are in vendor/maru. Historical bootstrap stages are
preserved in bootstrap/maru.bundle; a Linux x86-64 seed evaluator is included with
a checksum. Generated candidate builds and runtime stores are not release sources.
Confirm the DLM source license and attribution before GitHub publication; no new
license grant is asserted by this port. See NOTICE.
