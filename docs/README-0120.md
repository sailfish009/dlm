# DLM 0.0205 — sanitized release (DT proof-state + research snapshots)

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

## Contract layer (0.0113–0.0120) and resident loop (0.0121)

`(c107 NAME VARS PRE BODY POST FRAME)` is verified universally over every
Boolean input that satisfies Pre. 0.0114 added `if` with both branches checked.
0.0116 adds `(call NAME)`:

- a unit is `(unit107 NAME CONTRACT CASES)`; `CASES` must equal the table the
  verifier recomputes under the units before it;
- `p107-c-lib-check` validates a library strictly in prefix order, so forged
  summaries, duplicate names, forward/self calls and interface mismatches are
  rejected;
- `run` / `scan` / `check` take an **explicit** checked library (no ambient
  global); a call applies one summary row and never re-executes the callee body;
- `(refuted call-precondition NAME)` is preserved through run, scan and
  verify-lib instead of being wrapped as `invalid`;
- evidence is `(evidence CONTRACT RESULT LIB)`; only `(verified CASES)` is
  admissible and the checker recomputes the whole result under LIB, so a changed
  callee reports `stale-library` and a refuted/unknown/fabricated result is
  rejected;
- a Shen-inspired surface expander (`d107-surface.l`) reads
  `(contract NAME (VARS) (pre E) (body S...) (post E) (frame V...))` and
  `(unit NAME CONTRACT CASES)`, then re-validates the canonical `c107`/`unit107`
  data; `(define NAME (VARS) (pattern ...) (body ...))` expands to `def107`
  with `(call ...)` sugar for `call107`. It is notation, not a new trust
  boundary;
- public `answer`/`plan`/`revise` validate the whole query pattern before
  traversal (malformed → `(rejected107 pattern)`), and admission/execution share
  one exact call-arity rule;
- `(assert E)` is a proof obligation inside a body or `if` branch: true
  continues, false is `(refuted IN assert E)`;
- `(dlm 'start/pause/stop)` runs the existing bounded agenda while the original
  Maru reader waits; saturation unregisters the idle task, and only a `waiting`
  loop is reactivated by new evidence. This is **resident definition learning**,
  not self-generated-observation learning; the idle interval is not a work-time
  bound;
- evidence routing is **sparse and CPU-native** (`d107-index.l`): predicate/
  arity/position/value indexes, indexed joins, record-scoped support, and
  `incomplete107` when candidate/join bounds are exceeded;
- checked definitions compile to plans (`p107-def-plan`) and active 2-atom views
  (`p107-views`); plans are cached by exact body and never become evidence facts;
- candidate ranking uses a small CPU routing policy over support/atoms/vars/cost
  (`(dlm 'route)`); it only orders candidates and never bypasses `p107-def-ok?`;
- answer witnesses pass an independent proof check, symbol/string observation IDs
  cannot collide, nested admitted calls preserve raw/planned rows, and public
  query patterns are bounded before canonicalization (0.0110 F1/F2/F8);
- canonicalization is bounded on query, admission, learner and views; admission
  depth/size matches runtime expansion; execution calls and validation
  expansions have separate counters; exact keys and theory identity are
  injective/content-exact (0.0110 F4/F9);
- a checked 3-atom unit composes with one atom into a bounded 4-atom unit
  (`p107-try4`); ports and dependency body keys are explicit;
- `(dlm 'residual)` reports the read-only frontier (inactive units, grammar
  ceiling, record size, last search); proposals do not update routing weights
  until a durable commit;
- budget N permits exactly N join steps (never N+1), and proof validation
  memoizes shared DAG nodes while rejecting cycles (0.0110 F6/F7);
- `(dlm 'think PATTERN [BUDGET])` runs an explicit resumable think-state over
  bounded unit composition; continuation/answers/failures are data, and
  `think-next`/`think-resume` yield alternatives until exhausted or suspended;
- web claims carry source/version/scope/trust provenance; only corroborated,
  non-conflicted claims become observations, and single-source claims stay
  hypotheses (`d107-web.l`, `adapters/web_cache.py`);
- `d107-self.l` reports ability/weak predicates/gaps; a cached-source recursive
  experiment runs one DLM session per arm across rounds and shows learned b1/b2
  moving from a 3-step to a 2-step held plan, with no-web/single-source/
  scrambled/frozen controls;
- claim order no longer changes logical records, observation IDs are injective,
  the cache adapter loads natively, guessed/scope policy is enforced, self
  reports preserve the public budget, and terminal fan-out cannot overshoot;
- the verifier is **bounded**: at most 8 variables (256 states), 32
  statements/branch, 512 IR nodes, depth 16, 16 library units and 256 summary
  rows. Over-limit input is `(invalid unsupported-limit KIND)`, not a stack
  overflow. `unknown` is propagated but no budget scheduler produces it.

See `docs/release-0116.md` for the review-to-fix mapping. Release
`20261107T064706Z-31624`; the 0.0114 runtime is kept as `runtime/previous`.

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

- **The contract layer does not learn.** Definition formation/revision is the
  separate 0.0107 loop (`dlm 'step/learn/revise`); the finite contract verifier
  only checks and reuses summaries. It does not invent lemmas from contracts.
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
| `src/dlm/d107-util.l` | 90 | lists, strings, checksum, key codec |
| `src/dlm/d107-form.l` | 84 | atoms, rules, substitutions |
| `src/dlm/d107-close.l` | 191 | closure, proof terms, memoized checker |
| `src/dlm/d107-match.l` | 48 | Shen-shaped pattern matching |
| `src/dlm/d107-contract.l` | 450 | bounded finite contracts, call summaries, assert |
| `src/dlm/d107-surface.l` | 117 | Shen-inspired surface expander |
| `src/dlm/d107-def.l` | 229 | definitions, limits, depth, admission |
| `src/dlm/d107-session.l` | 189 | state, events, replay, content identity |
| `src/dlm/d107-index.l` | 265 | sparse indexes, joins, quads, bounds |
| `src/dlm/d107-plan.l` | 301 | plans, views, deep expansion, counters |
| `src/dlm/d107-learn.l` | 378 | learning, 4-atom composition, residual, routing |
| `src/dlm/d107-read.l` | 60 | N1–N3 realization |
| `src/dlm/d107-agenda.l` | 33 | one agenda, incomplete propagation |
| `src/dlm/d107-command.l` | 338 | `(dlm ...)`, loop, route, residual, think |
| `src/dlm/d107-think.l` | 139 | explicit resumable think-state |
| `src/dlm/d107-search.l` | 12 | search surface macros |
| `src/dlm/d107-web.l` | 151 | web claims, corroboration, conflict |
| `src/dlm/d107-self.l` | 44 | ability, weak predicates, gaps |
| `adapters/reduce.py` | 122 | untrusted reduction |
| `tests/core-tests.l` | 1313 | 311 native checks |

## Verification

Seventeen Python tests and 311 native checks pass (normal and safety-2), and the
independent review contract oracle still passes 256/256. This candidate reuses
the promoted 0.0116 runtime `20261107T064706Z-31624` (three-generation
LLVM/stripped equality); it has not been promoted itself. The resident loop is
bounded definition learning: 2→3 atom grammar, no self-generated observations,
and the loop control state is not persisted. The contract checker
recomputes with the same library; it is not a separately implemented second
verifier.

`src/maru` is the Maru compiler baseline, unchanged. No new bootstrap
dependency. Previous version directories are untouched.