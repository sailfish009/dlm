# DLM v0.0065 — executable language + persistent Experience

v0.0065 makes the candidate language and learned controller part of the model,
not hidden host-side configuration. **One immutable typed `(model-state ...)`
IR-TREE remains the authoritative model.** Python objects, JSON, and indexes are
views; every durable change is a replayable, kernel-checked IR transition.

```text
Wikipedia / GitHub / web search / local text
  -> cached bounded transport
  -> candidate-blind text or Python-AST lowering
  -> typed source-document + claims + provenance IR
  -> validated ingest transition
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
  (documents
    (source-document
      (provenance (provider "wikipedia") (uri "...")
                  (source-group "wikipedia:123") (trust "acquired")
                  (revision "7") (content-hash "..."))
      (content "...") (normalized "...")
      (document-tree ...) (claims ...)))
  (agenda
    (acquisitions
      (acquisition-record
        (need (information-need ...))
        (status "acquired") (document-ids "@doc-..."))))
  (evidence (episode ... (document-id "@doc-...")))
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

## Heterogeneous external input → IR-TREE

The v0.0062 acquisition ideas were adapted to the current typed model-state
rather than copying its obsolete tuple/StoreState representation:

- `dlm/web.py`: bounded cached stdlib transport plus Wikipedia, GitHub repository
  README, Stack Exchange web-search, and direct URL providers;
- `dlm/ingest.py`: HTML/Markdown/plain-text normalization, sentence tree,
  conservative relation extraction, and AST-only Python projection;
- `ingest_transition`: deterministically recomputes the document/evidence update
  before the Store journals it.

Every payload becomes a `(source-document ...)` carrying raw content, normalized
text, structural tree, claims, content hash, URI, revision, trust, and
`source-group`. Raw content is authoritative input: validation reruns the internal
projection and rejects edited normalized text, trees, or claims. Extractors
receive only the document—never a candidate theory or current prediction. Exact
mirrored content is assigned one source group so it cannot fake independent
corroboration.

Only non-uncertain claims above the confidence gate become episode facts.
Uncertain and `guessed` claims remain inspectable IR but never enter kernel
closure. External text never directly creates Ground or Experience rules.
The lexical reducer is deliberately conservative and limited; unrecognized prose
is still retained in the document tree and causes no assertion.

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

## Recursive self-study with model-owned acquisition

```bash
# Default: assess needs and fetch Wikipedia/GitHub/web-search evidence each round
./experiments/selfssl/selfssl.sh --max-concepts 40
# Deterministic replay/test mode: use the response cache only
./experiments/selfssl/selfssl.sh --offline --max-concepts 40
# Ctrl-C is the normal stop mechanism
```

External ingestion is now inside the recursive round rather than a separate
preprocessing requirement. Each round:

1. parses `dlm/*.py` with `ast.parse` only into typed PyIR;
2. derives `(information-need ...)` forms from unresolved source symbols,
   explicit unknowns, and confirmed targets with no kernel proof;
3. selects the next need using persisted acquisition history;
4. selects a provider order by need kind (for example, GitHub first for an
   unresolved source symbol), constructs its own query, and queries the allowed
   providers (default) or only their cache (`--offline`);
5. lowers returned text into canonical source-document IR and commits an
   `acquire` transition; a miss is an explicit, retryable abstention;
6. extracts the bounded public learning call graph and independent held-out BFS
   evidence;
7. runs persisted candidate programs and native ranking;
8. admits at most one Experience rule through the kernel gate;
9. appends both acquisition and learning transitions to the journal.

Thus the next round consumes prior documents, acquisition history, Experience,
and learned ranking state. The caller controls transport policy and resource
limits, but does not supply the query or label. Natural language is emitted only
for measured held-out improvement or repaired contradiction; saturation is
silent. This improves the symbolic self-model and search policy. It does not
rewrite Python source and does not treat its own prediction as a label.

## Commands

```bash
./test.sh
# Local Markdown/Python/text input
./experiments/ingest/ingest.sh --file README.md --store /tmp/dlm65-store --fresh
# Heterogeneous web acquisition (omit --offline for a fresh fetch)
./experiments/ingest/ingest.sh --query 'deductive logic model' \
  --providers wikipedia,github,web-search --store /tmp/dlm65-store
./experiments/axiom/axiom.sh
./experiments/repl/repl.sh --fresh
./experiments/repl/repl.sh --eval '(run-programs)'
./experiments/selfssl/selfssl.sh --rounds 4 --interval 0 \
  --store /tmp/dlm65-store --fresh
./experiments/selfssl/selfssl.sh --providers wikipedia,github,web-search \
  --store /tmp/dlm65-store
```

Inside the REPL:

```lisp
ir> (run-programs)
ir> (stop-status)
ir> (step 64)
```

Tests cover canonical IR round-trip, heterogeneous document conversion,
provenance/content integrity, candidate-blind extraction, guessed-data exclusion,
web-provider normalization, executable persisted programs, native contrast
state, exact proof verification, fixed evidence, unknown handling,
Ground immutability, counterexample lifecycle memory, stale/forged transition
refusal, append-only replay and tamper refusal, TreeLisp capability boundaries,
PyIR validation, held-out learning, event-only speech, and restart behavior.
