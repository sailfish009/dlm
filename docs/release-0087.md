# DLM 0.0087 — finite Maru-native contracts and procedure reuse

Promoted release: `20261023T113237Z-21704`.
Previous directory `/research/dlm_v0.0086` is preserved.

## Delivered

Independent Maru implementation of a small Silicon-inspired contract verifier:

- Boolean finite-state assign/assert/if/call IR, pre/post/old and write-frame checks.
- Universal checking of all applicable modeled inputs, not one successful path.
- An explorer that proposes complete-case trace certificates and a separate
  local checker that verifies coverage/transitions without calling the explorer.
- Independently checked finite counterexamples, separate unknown/inapplicable/
  invalid statuses; inconsistent Pre is not a useful learned solution.
- Acyclic verified procedure tables, caller preconditions and effect checks,
  full-prefix dependency binding and stale-summary refusal.
- Actual space79 choose/verify87/accept program generation and a final proof gate.
- Original-REPL `(contracts ...)` API for verify/admit/synth/learn/check-library.
- Native proof-carrying contract-store87 save/load with advisory lock,
  readback/previous/atomic replacement and certificate revalidation on restore.

Source modules: `src/dlm/contracts87-ir.l`, `contracts87-check.l`,
`contracts87-runtime.l`. No Silicon Scala source or external SMT toolchain copied.

## Demonstrated behavior

`./scripts/run.sh proof experiments/space/contracts87.l` generates setflag,
reuses it via call, generates setready, and solves the stronger conjunction using
checked procedure composition. A missing feasible else is refuted with input
flag0/ready0. A toggle verifies while preserving ready and old-state meaning.
Native output is `docs/contracts87-demo.sexp`.

The independent Python interpreter agreed on200 seeded finite programs over
four possible input valuations each, with zero status mismatches. Other tests
exercise forged coverage/traces/provisional tickets, precondition/effect failure,
dependency changes, library load/corrupt-store refusal and real original-REPL use.

## Final verification

`compiler.sh reproduce`, `verify 20261023T113237Z-21704`, and `promote` completed.

- 100 Python tests passed in131.084 seconds under the verified candidate.
- Native, store, runtime and graph-store suites passed.
- Sibling0066 Horn/graph differential checks passed.
- Candidate/next/third LLVM outputs and stripped executables matched.
- `src/maru` matches v0.0086; no new compiler/bootstrap dependency.
- Current `docs/release.tests.sha256` verifies against the source tree.

Evidence: `docs/verification.log`, `docs/python-tests.log`,
`docs/release.sources.sha256`, `docs/release.tests.sha256`, and the runtime release
directory. Eleven new tests are in `tests/test_contracts87.py`.

## Important scope limits

This is complete finite Boolean enumeration, not full Silicon/Viper compatibility
or SMT symbolic arithmetic. Explorer and checker share small Boolean/store/typing
primitives; the implementation itself is not formally proven correct. The domain
is <=6 Boolean variables,128 statements,8 modules, acyclic calls and16 generated
candidates. Fuel is logical work, not a hard time bound. Generation may miss plans.
No loops, arbitrary Maru code, heap aliasing, fractional permission, real I/O effect
verification, unrestricted math or natural-language reasoning is claimed.

Contract learning is an explicit goal API using the original REPL/shared machine.
The old relation idle learner and shell continue unchanged; they do not autonomously
select contract goals. Contract libraries require explicit `contracts save/load`
and are not included in `dlm save`. No new autonomous web-grounding functionality,
speedup, neural model, registered MLIR dialect or GitHub publication is claimed.

Detailed grammar, proof boundary and persistence contracts:
`docs/contracts87-design.md`. Earlier retained reports are historical.
