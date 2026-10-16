# DLM v0.0065 — executable language + persistent Experience

v0.0065 makes the candidate language and learned controller part of the model,
not hidden host-side configuration. **One immutable typed `(model-state ...)`
IR-TREE remains the authoritative model.** Python objects, JSON, and indexes are
views; every durable change is a replayable, kernel-checked IR transition.

```text
fixed evidence + current IR state
  -> persisted TreeLisp rule programs              C_t = L(S_t)
  -> native sparse state/action scorer             π_t = rank_N(S_t, C_t)
  -> Horn closure + explicit evidence gate         V_t = K(S_t, π_t)
  -> deterministic transition validation           S_(t+1) = Commit(S_t, V_t)
  -> append-only IR journal
```

There is no CLM, strands-decider, transformer, LLM, tokenizer, embedding,
PyTorch, external scorer callback, or model HTTP service. The implementation is
stdlib-only; pytest is the sole test dependency.

## One model language

The persistent tree contains evidence, executable programs, retractable theory,
native learned weights, contrast replay, lifecycle memory, and the lowered
subject:

```lisp
(model-state
  (version "0.0.65")
  (round 2)
  (evidence (episode ...))
  (theory (ground ...) (experience ...))
  (memory (experience-record ...))
  (language
    (programs
      (program "unary-project" (rule-template ...))
      (program "binary-chain" (rule-template ...))
      (program "binary-join-right" (rule-template ...)) ...)
    (controller
      (pipeline "retract" "run-programs" "rank" "kernel-test"
                "contrast" "admit" "record"))
    (program-stats (program-stat "binary-chain" 12 3) ...))
  (decision
    (lr 0.2) (margin 1.0)
    (weights (weight "feature" 1.0) ...)
    (updates 4)
    (replay (contrast ...)))
  (candidates ...)
  (verdicts ...)
  (events ...)
  (metrics ...)
  (subject (source-subject ...)))
```

Terms are explicit and lossless:

```lisp
(atom edge (const "New York") (const "x(y)"))
(atom reach (var "x") (var "z"))
```

`node_id` assigns canonical content IDs. `dag_index` and `index.json` are
rebuildable caches, never independent authorities.

## Persisted TreeLisp program layer

`dlm/language.py` interprets the programs in `(language ...)` against typed
evidence schemas. Meta-predicates are expanded only when arity and head/body
roles agree. The default language expresses unary projection, copy/inverse,
and several binary relational joins, including chain composition. Candidate
provenance (`program=<name>`) is a native scorer feature; per-program tried/won
statistics accumulate in the same tree.

This is intentionally not a Python `synthesize()` grammar disguised as Lisp:
removing `binary-chain` from the model tree removes that logic family from
candidate generation. `synthesize()` is only a projection of
`execute_programs(state)`.

TreeLisp adds:

```lisp
(run-programs)
(rank)
(choice)
(test-rule RULE)
(step BUDGET)
```

It cannot assert a fact/rule, commit a transition, import, access files or the
network, launch subprocesses, or call Python FFI. Evaluation is fuel-bounded.
Self-hosting (`lambda`, `letrec`, evaluator rewriting) remains deliberately out
of scope.

## Native neuro-symbolic control

The native learner is a small sparse state/action ranker over structural rule
features, predicate roles, and program origin. It performs margin-based
positive/negative contrast updates when the kernel identifies a useful winner
and checked alternatives. Learned weights, update count, and a bounded replay
buffer are all IR state and survive restart.

The scorer controls search order only. It has no assertion authority. A high
score cannot bypass exact unification, semi-naive predicate-indexed closure,
safety, contradiction, source support, or transition verification.

## Fixed evidence, moving axioms

Evidence is partitioned into:

```text
facts / confirmed / contradicted / unknown
```

Unknown is not negative. A candidate is admitted only if it:

1. is a safe typed Horn rule;
2. adds confirmed coverage;
3. derives no explicitly contradicted atom;
4. satisfies the independent-source support gate.

Learned finite-data rules enter retractable `Experience`, never immutable
`Ground`. New counterevidence appends a `retracted` lifecycle record and a
tombstoned transition; Ground conflict causes abstention. Proofs are typed IR
and verification checks theory membership plus substitution consistency.

## Snapshot + append-only journal

`dlm/store.py` uses:

```text
store/
  snapshot.ir.json       # one authoritative model-state expression
  experience.irlog       # one canonical transition expression per line
  index.json             # disposable summary cache
  experience.N.irlog     # immutable audit segments after checkpoint
```

Loading validates the snapshot and deterministically replays every transition.
A stale, edited, forged, or semantically inconsistent journal line is rejected.
Derived closure is never persisted as truth. `checkpoint()` writes the current
state atomically and retains the old journal as an audit segment.

## Recursive self-study

```bash
./experiments/selfssl/selfssl.sh --max-concepts 40
# Ctrl-C is the normal stop mechanism
```

Each round:

1. parses `dlm/*.py` with `ast.parse` only into typed PyIR;
2. extracts a bounded public learning call graph;
3. obtains held-out dependency evidence from an independent BFS oracle;
4. runs the persisted candidate programs;
5. lets the native scorer order candidates;
6. admits at most one Experience rule through the kernel gate;
7. appends the transition to `experiments/selfssl/store/`.

The next round consumes both prior Experience and learned ranking state.
Natural language is emitted only for measured held-out improvement or repaired
contradiction; saturation is silent. This improves the symbolic self-model and
search policy. It does not rewrite Python source and does not treat its own
prediction as a label.

## Commands

```bash
./test.sh
./experiments/axiom/axiom.sh
./experiments/repl/repl.sh --fresh
./experiments/repl/repl.sh --eval '(run-programs)'
./experiments/selfssl/selfssl.sh --rounds 4 --interval 0 \
  --store /tmp/dlm65-store --fresh
```

Inside the REPL:

```lisp
ir> (run-programs)
ir> (stop-status)
ir> (step 64)
```

Tests cover canonical IR round-trip, executable persisted programs, native
contrast state, exact proof verification, fixed evidence, unknown handling,
Ground immutability, counterexample lifecycle memory, stale/forged transition
refusal, append-only replay and tamper refusal, TreeLisp capability boundaries,
PyIR validation, held-out learning, event-only speech, and restart behavior.
