# Release 0.0129 — explicit think-state machine for resumable nondeterministic execution

- Date: 2026-11-08
- Predecessor: 0.0128. Candidate, not promoted.
- Input: `/research/analysis-screamer-dlm-execution.md`.
- Scope: first explicit execution adapter. Continuation is data, not a captured
  VM stack. No macro DSL, CSP propagation, web acquisition or commit is added.

## State shape

```text
(think107 STATUS WORK BUDGET CONTEXT TARGET BRANCHES ANSWERS FAILURES DEFS)
```

- STATUS: `running | suspended | exhausted | invalid`
- CONTEXT: exact serialized observations, definitions and rules
- BRANCHES: `(branch107 STATUS DEF BIND REST CANDIDATE REASON)`
- ANSWERS: `(answer107 CANDIDATE DEF BIND REST BODY-KEY)`
- FAILURES: `(fail107 REASON REST)`
- DEFS: the frozen basis used for every checker call

## Operations

```text
p107-think-start    state + target pattern + budget
p107-think-next     yield next answer | exhausted | suspended
p107-think-step     one branch of work
p107-think-run      drain until exhausted/suspended
p107-think-resume   raise the budget and resume
p107-think-form / p107-think-of-form   exact data round-trip
p107-think-stale?   context changed?
```

Commands:

```lisp
(dlm 'think PATTERN [BUDGET])
(dlm 'think-next)
(dlm 'think-status)
(dlm 'think-resume BUDGET)
```

## First adapter: bounded unit composition

- target: 4 atom pattern
- alternative: an active 3-atom unit + the remaining target atom
- require: the callee itself is freshly checked (`p107-def-ok?` and
  `p107-def-executable?`), alignment succeeds, and the candidate definition
  passes `p107-def-ok?`
- yield: a proposal candidate plus its callee, binding, remaining atom and
  exact body key
- reject: the branch is recorded in FAILURES and the machine resumes

The checker gate is re-run at yield. A yielded proposal is **not committed**;
callers must use the normal durable transition/publish path.

## Measured

4-fact fixture with b1/b2 active:

```text
start: running, 4 branches
next:  yield, 4 total answers
after: exhausted
```

- multiple yields followed by `exhausted`
- budget 1 -> suspended; resume with budget 8 -> exhausted with the same 4 answers
- state round-trips through its data form
- context becomes stale after retraction
- a forged active callee produces recorded failures while valid alternatives
  still yield
- observations and definitions are unchanged by thinking

```text
native normal      293 ok / 0 FAIL
native safety-2    293 ok / 0 FAIL
Python             16 tests OK
contract oracle    256/256 PASS
```

## Limits

- The first adapter is unit composition, not a generic goal/obligation engine.
- AND obligations are the composition requirements (callee check, alignment,
  coverage, candidate check), not an arbitrary goal stack.
- Branch-local assumptions/bindings are stored; general hypothetical reasoning
  (`H ⊢ q`) is not yet exposed as a public proof form.
- No `define-form` macro DSL, no resumable CSP, no web pipeline.
- A yielded proposal is not learned; checked commit and later reuse remain
  outside the machine.
