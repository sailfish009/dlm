# DLM 0.0109 — Maru string-compare fix; safety-2 gate green

A new, small implementation. The previous trees (`dlm_v0.0088` … `dlm_v0.0102`)
were **reference only**; nothing from their `src/dlm` was copied. What is kept is
the DLM structure on top of Maru: a trusted kernel, untrusted reduction, one
session, and a leveled reading.

```text
L0 observation   provenance (source, record, span) + scope
L1 kernel        form · closure + proof term · independent checker
L2 adapter       Python source -> ground facts (untrusted, hash-pinned)
L3 session       one state, one event log, replay-checked snapshot
L4 agenda        step / run / query / read
L5 reading       N1 relation, N2 meaning, N3 idiom; support or abstain
```

## Run

```sh
./scripts/run.sh repl                 # original Maru REPL
./scripts/run.sh northstar            # the M1 experiment (fixed input)
./scripts/run.sh test                 # native core assertions
python3 -m unittest discover -s tests -p 'test_d107.py' -v
```

## Review fixes (0.0104 and 0.0105)

0.0104 closed nine defects from the 0.0103 review: derived facts posing as
`given`, rank-as-justification, extensional rule heads, an order-insensitive rule
digest, a SIGSEGV on malformed input, transitions that were not durable, lost
updates across sessions, stale overwrites, and read errors treated as a missing
file.

0.0105 closed the remaining P1/P2 items: proofs are now validated as a **DAG**
(every child's own proof must check, with a bounded walk), the digest is a proper
order-sensitive hash (FNV-1a 32-bit), proof indices and dotted structures are
validated instead of faulting, snapshot identity is a **content digest** rather
than an epoch, negation is evaluated after all positives are bound (literal order
irrelevant), empty-body rules fire, re-opening without closing is refused, and
`reduce.py --check` verifies the facts body. `tests/oracle107.py` compares the
closure with an independent reference on 150 generated programs.

One limitation remains: Maru's reader aborts the process on syntactically invalid
bytes, so damaged snapshots cannot be rejected in-language (we never write on a
read failure and keep `.previous`).

## What is actually implemented (M1)

- Ground atoms, rules with **negation restricted to extensional predicates**, so
  every program is stratified by construction.
- Forward closure with a **proof term per derived atom**, a budget, and
  `unknown` on exhaustion (never `false`).
- An **independent proof checker**: it recomputes the head instance and requires
  every positive body atom to be present and every negated one to be absent.
- Observations with `(source, record, scope)`; queries and closures are
  **scope-isolated**; retraction removes facts and their interpretation.
- A **single** `state107` with a bounded event log; snapshots are validated by
  **replaying the log** and comparing the state; the background-law checksum is
  part of the snapshot, so changing rules invalidates old files.
- Atomic save (`lock`, `.next`, readback, `.previous`, replace), corrupt-file
  rejection.
- Reading emits **N1/N2/N3** sentences only when the support proof checks; level
  counts are reported. Unreadable predicates produce no sentence.
- `adapters/reduce.py` reduces `experiments/northstar/input/main.py`
  (PyTorch MNIST example, pinned bytes) to 209 facts with a pinned
  `facts-sha256`. It is untrusted and developer-side; the kernel decides.

## Measured M1 result

`./scripts/run.sh northstar` (log: `docs/northstar-m1.log`):

```text
reduced facts: 209
status=complete facts=231 sentences=157 skipped=0
levels ((level 1 135) (level 2 10) (level 3 12))
library-only view: 121 sentences, levels ((1 99) (2 10) (3 12))
```

All 157 sentences carry a proof that the checker accepts (`skipped=0`).

## Learning: the data stays, the basis moves (0.0107)

`(dlm 'rules ...)` only configures laws and resets state; it is not learning.
0.0107 adds the direction the review asked for:

```text
(dlm 'step)   interpret an observation, then try to move the basis
(dlm 'learn)  one learning step: propose, check, admit
(dlm 'defs)   units with support, active flag, plan steps
(dlm 'plan PATTERN)     raw steps vs planned steps and the covering unit
(dlm 'answer 'scope PATTERN)   rows and witness ids
(dlm 'revise ID PATTERN)       replace a unit; dependents are re-validated
```

A unit is `(def107 ID VARS PATTERN BODY)`; `BODY` may `(call106 ID ...)` an
earlier unit. Admission is expansion equality (alpha-renaming and atom order),
never a score. Support counts distinct records, so retracting data lowers support
and the unit becomes inactive while the definition stays in the basis.

Measured on `experiments/learn/run.l` (three records, one owner, three calls):

| before | after |
|---|---|
| basis 0 | basis 2 (`b2` calls `b1`) |
| plan 3 steps | plan 2 steps |
| 18 answers, 0 unit calls | 18 identical answers, 1 real unit call |

The plan is **executed**: a `call` step runs the unit's own body and is counted,
so removing the basis changes the execution path (the review's P1 finding).

The observations are byte-identical before and after learning. This is a
planning/inference-unit change, **not** a speedup: a call expands to its body.

## What this is not

- **No learning yet.** There is no definition formation, no lemma promotion, no
  hypothesis layer, no revision. `run` only interprets observations.
- **N4–N9 are not implemented** (composition, architecture, causal, purpose,
  analogy, certified absence).
- The comparison with 0.0062 is **not** parity: 0.0062 emitted 42 *selected*
  sentences across N1–N9; this release emits *all* readable facts over its own
  reduction, so counts are not comparable one-to-one. What is comparable is:
  every sentence is support-checked, and N1–N3 exist from a real code input.
- The reduction is an **untrusted Python adapter**; there is no native Maru
  Python parser yet. Integrity rests on pinned source/facts hashes, not on the
  kernel re-parsing Python.
- No SMT, integers, heaps, loops, concurrency, LLM or GPU. No natural-language
  generation beyond fixed templates.
- `start`/cooperative idle scheduling is not implemented; `run N` is explicit.

## Layout

| file | lines | role |
|---|---:|---|
| `src/dlm/d107-util.l` | 50 | lists, strings, checksum |
| `src/dlm/d107-form.l` | 75 | atoms, rules, substitutions |
| `src/dlm/d107-close.l` | 105 | closure, proof terms, checker |
| `src/dlm/d107-session.l` | 138 | state, events, replay, storage |
| `src/dlm/d107-read.l` | 59 | N1–N3 realization |
| `src/dlm/d107-agenda.l` | 17 | one agenda |
| `src/dlm/d107-command.l` | 130 | `(dlm ...)` |
| `adapters/reduce.py` | 117 | untrusted reduction |
| `tests/core-tests.l` | 95 | 26 native checks |

## Verification

Fifteen Python tests and 72 native checks pass; the compiler was reproduced,
verified and promoted with three-generation
LLVM/stripped equality. See `docs/release-0103.md`.

`src/maru` is the Maru compiler baseline, unchanged. No new bootstrap
dependency. Previous version directories are untouched.