# DLM 0.0088 — integrated native contract curriculum

Promoted release: `20261023T121713Z-27384`.
Previous directory `/research/dlm_v0.0087` is preserved.

## Delivered integration

- Original `(dlm 'step/start)` selects relation and/or contract work using one
  native curriculum; mixed mode alternates runnable domains.
- Persistent explicit contract goals, partial candidate frontiers, unresolved
  diagnostics, retry contexts, learned procedure library and scheduler turn.
- Actual existing space79 choose/verify87/accept execution for each candidate
  page, followed by exact-goal matching and an independent certificate gate.
- Later contract goals reuse earlier checked operators. The demo's stronger
  goal is solved by `((call setx88) (call sety88))`.
- One `dlm-session88` transaction/checkpoint contains BOTH domains. Manual87
  library publication also crosses this boundary; `dlm save/close` is sufficient.
- Fresh-process restoration preserves both contract and plain native relation
  incomplete cursors, native nondeterministic feedback, configuration and next
  work item. A failed joint checkpoint publishes neither staged state nor round.
- Existing relation-only workflows retain their codecs/fast path; old77/83/84/
  85/86 files migrate lazily on a first88 event. Live contract state cannot be
  silently erased by opening an older file.
- The existing single recursive experiment shell gains `--contracts-demo`,
  `--curriculum`, `--contract-batch`, and `--contract-fuel`. Existing source
  observations/goals/libraries and restored budgets are not overwritten by demo
  reinjection or default flags.

Main source: `src/dlm/contracts88-curriculum.l`, `contracts88-session.l`, plus
existing REPL/session/search/publication seams. No compiler/platform source or
new bootstrap dependency was added.

## Run

Use a fresh demo path:

```sh
./scripts/recursive-selfssl.sh --demo --contracts-demo --rounds 12 --budget 4 /tmp/fresh88.sexp
./scripts/recursive-selfssl.sh --rounds 1 /tmp/fresh88.sexp
# Interactive original REPL instead of a finite run:
./scripts/recursive-selfssl.sh --demo --contracts-demo /tmp/another88.sexp
```

The mixed demo reaches three native relation definitions and three checked
procedures by step10; subsequent steps wait without adding learning events.
A native nonpersistent example is `experiments/space/curriculum88.l`; its checked
output is `docs/curriculum88-demo.sexp`. The source driver filename
`experiments/repl/recursive86.l` remains for compatibility; it is the extended88
single-process driver, not an independent old learner.

## Final verification

`compiler.sh reproduce`, `verify 20261023T121713Z-27384`, and `promote` completed.

- **115 Python tests passed in167.877 seconds** under the verified candidate.
- Fifteen new tests in `tests/test_contracts88.py` cover both-domain recursive
  learning, complete fresh-process next-step equality, partial cursors, lazy
  migration, budget/library retry, nonvacuity, forged positive tickets/weaker
  specs/serialized state, rollback, public library publication/reset, restore
  conflict, resource preflight, finite shell restart and original idle REPL.
- The existing independent200-program Boolean interpreter oracle reports zero
  mismatches. Other independent logic/interpolation/definition oracles passed.
- Native, store, runtime and graph-store suites passed.
- Sibling0066 graph/Horn differential checks passed.
- Candidate/next/third LLVM outputs and stripped executables matched.
- `src/maru` matches v0.0087; no Scala/SMT/LLM dependency was introduced.
- `docs/release.sources.sha256` and `docs/release.tests.sha256` match the final
  implementation, including the native example.

Evidence: `docs/verification.log`, `python-tests.log`, `release.sources.sha256`,
`release.tests.sha256`, `release.txt`, and the promoted runtime directory.

## Cost diagnostic: integration is not a speedup

Six fresh-process runs, three per arm in randomized seed88 order, ran the same
explicit ten-step mixed workload and checked the same three native definitions
and three procedures. Startup, admissions, full-library checking and final close
were included. Median wall time:

| Arm | Seconds |
|---|---:|
| In-memory joint state, no attached store | 0.617014 |
| Per-event durable joint checkpoint | 6.848223 |

Final attached snapshots were5523 bytes. Repeated full journal replay/proof
revalidation dominates this small workload; durable execution is substantially
slower. Operator reuse is shown semantically, not as a performance gain. This
three-run local diagnostic is exploratory, not a broad or statistically powered
comparison. Raw records: `docs/curriculum88-costs.json`.

The diagnostic uses `test_contracts88.SETUP`, ten `dlm step` calls, assertions of
three definitions/three modules plus `contracts check-library`, and `dlm close`;
one arm first calls `dlm open` on a fresh temporary path, the other does not.

## Scope boundaries

This integrates scheduling, ownership and storage; it does NOT silently equate
native observations with modeled Boolean transitions. Procedures never become
external facts. Explicit typed goal templates are still required: automatic goal
invention, natural-language question grounding and web-to-small-axiom extraction
remain unimplemented.

The verifier remains the finite87 subset: <=6 Boolean variables,128 statements,
8 acyclic modules and16 generated candidates per goal context; the agenda is
bounded at16 goals and the journal at256 events. Unsatisfiable Pre is inapplicable,
not learned. Unknown or exhausted finite generation is not proof of impossibility.
The shell waits on blocked/saturated work rather than inventing progress. Logical
fuel/reservations are not preemption or wall-time guarantees. No full Silicon
compatibility, integer/loop/heap verification, arbitrary Maru-program proof,
registered MLIR dialect, speedup or GitHub commit/push is claimed.

Detailed state machine, replay, migration and trust boundary:
`docs/contracts88-design.md`. Earlier retained reports describe their historical
versions, including87's formerly separate contract persistence.
