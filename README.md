# DLM 0.0088 — one native recursive relation/contract curriculum

The v0.0087 finite Boolean verifier is now connected to the **original
`(dlm 'step/start)` loop and the same native session checkpoint**. No second
learner process, Python runtime scheduler, LLM, Scala, Viper or SMT dependency.
Previous version directories remain unchanged.

## Run the integrated experiment

```sh
# One original interactive Maru REPL; learning runs at reader idle points.
./scripts/recursive-selfssl.sh --demo --contracts-demo /tmp/recursive88.sexp

# Finite, checkpointed demonstration of both domains.
./scripts/recursive-selfssl.sh --demo --contracts-demo --rounds 12 --budget 4 /tmp/recursive88.sexp

# A fresh process restores the agenda, libraries, budgets and next scheduler turn.
./scripts/recursive-selfssl.sh --rounds 1 /tmp/recursive88.sexp
```

Use a fresh path for the first demo. `--demo` adds explicit relation observations;
`--contracts-demo` queues three explicit Boolean goals, not preverified solutions.
Neither overwrites an existing corresponding domain. The mixed demo learns three
relation definitions and setx88/sety88/both88; the last procedure is
`((call setx88) (call sety88))`. Exhausted domains wait without synthetic updates.
Ctrl-C preserves already completed checkpoints, not an interrupted transaction.

The shell keeps its single original reader driver at
`experiments/repl/recursive86.l` for CLI compatibility; that driver is extended,
not a separate old learning process. Relation-only invocations still work.

## Use the same REPL manually

```sh
./scripts/run.sh repl
```

```lisp
(dlm 'open "/tmp/my88.sexp")
(dlm 'goal '(contract87 setx (x y) (bool 1) () (var x) (x)))
(dlm 'goal '(contract87 sety (x y) (bool 1) () (var y) (y)))
(dlm 'goal '(contract87 both (x y) (bool 1) () (and (var x) (var y)) (x y)))
(dlm 'contract-budget 4 2000) ; candidate batch, verification fuel per candidate
(dlm 'curriculum 'contracts) ; or 'mixed / 'relations
(dlm 'step)                 ; same entry point as relation learning
(dlm 'start 1000)           ; same cooperative idle scheduler
(dlm 'pause)
(dlm 'goals)                ; pending/solved/blocked/inapplicable, frontier, diagnostics
(dlm 'curriculum)           ; scheduler/configuration/request counters
(contracts 'library)
(contracts 'check-library)
(dlm 'close)                ; BOTH domains saved; no second save required
```

In a fresh REPL, `(dlm 'open "/tmp/my88.sexp")` restores both domains.
Manual `(contracts 'learn/admit/restore/load/reset ...)` publications also cross
the same transaction boundary. `contracts save/load` remain optional standalone
library export/import, not the main session workflow. `dlm reset` resets both
domains. `contracts reset` clears only procedures and reopens affected goals.

Scheduling mode is explicit: the default remains `relations` for compatibility.
Registering a goal alone does not change it; use `contracts` or `mixed` once.
Mixed mode alternates runnable domains and skips a domain that has no work.
Blocked finite searches are retried on a changed library/fuel context or an
explicit `(dlm 'retry-goal 'NAME)`, not endlessly on every idle poll.
`(dlm 'relation-budget 4)` persists the relation decision budget too.

## What approval means

The existing independently implemented Maru Boolean `assign/assert/if/call`
verifier still checks **all inputs satisfying Pre**, complete trace coverage,
Post, old-state references and the write frame. Calls use checked dependency-bound
procedure tables. Candidate OR search is not universal program verification.

A curriculum admission additionally checks exact requested-goal identity and
independently checks the proposed certificate. A provisional success ticket or a
proof of a weaker goal cannot admit a procedure. Empty Pre is inapplicable, not
success; unknown/bounded generation is not logical refutation. Learned procedures
never become native source observations or external world axioms.

`dlm-session88` includes the native model, event history, contract goals and
frontiers, checked library, scheduler turn and configuration. Untrusted load
replays both domains, rebuilds the search controller, rechecks proofs and compares
the reconstructed state. Existing77/83/84/85/86 codecs remain readable. A failed
checkpoint does not publish the staged goal, library, policy or step round.

## Scope and verification

The model remains limited to6 Boolean variables,128 statements,8 acyclic modules,
16 generated candidates per goal context and16 queued goals. Generation can miss
solutions. Logical fuel and cumulative request limits are not hard wall-time
limits. Mixed scheduling is cooperative, not parallel or preemptive. Proof rows
establish only the stated finite model. There is no integer/loop/heap verification,
arbitrary Maru-program verification, autonomous web axiom extraction or automatic
natural-language question grounding. Goal templates are explicitly supplied;
useful goal invention and cross-domain fact grounding are not claimed.

```sh
./scripts/run.sh proof experiments/space/curriculum88.l
python3 -m unittest discover -s tests -p 'test_contracts88.py' -v
./scripts/run.sh test
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Fifteen new tests cover joint learning/reuse, fresh-process next-step equality,
both native/plain and contract partial frontiers, migration, budget retry,
forged tickets/specs/caches, rollback, reset/import and real interactive idle use.
The independent200-program finite semantic oracle remains in the suite.

Design and boundaries: [contracts88-design.md](docs/contracts88-design.md).
Final verification and matching manifests: [release-0088.md](docs/release-0088.md).
Maru compiler sources are unchanged; earlier release documents are historical.
No speedup, full Silicon compatibility or GitHub publication is claimed.
