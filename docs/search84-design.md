# Search84 — symbolic Go-inspired search control in native Maru

## What this release implements

A bounded candidate search controller for the existing DLM77 recursive learning
loop. It implements transposition-style negative reuse, outcome/cost-based move
ordering, and integer fixed-point UCB family selection. It does NOT implement
MCTS rollouts, a game tree, neural policy/value networks or LLM inference.
The native Horn kernel and conservative-definition certification remain decisive.

Routing is opt-in: `(dlm 'search 'cache)`, `'rank`, `'ucb`, or `'off` (default).
`(dlm 'search)` reports diagnostics. All execute in the original Maru REPL and
its cooperative `start/pause` loop. Python is only a developer experiment driver.

## Candidate construction and state

`search-control.l` defines immutable `(control84 mode model-key pool
rejection-cache family-stats total-trials certify-calls cache-hits joined-pairs
complete? inspected-proof-entries)`.

The candidate pool indexes each episode closure's right-hand facts by starting
entity, joining only endpoint-compatible left/right pairs. Candidates are
conservative relation definitions of primitive path length <=4, with the same
composition grammar and native `a77-certify` gate as before. Exact `(word,
compose-operands)` candidates are deduplicated across episodes. Each candidate
retains its split lengths for policy-family assignment.

The pool is built once for an exact model revision and consumed across budgeted
steps; it is not rebuilt from the beginning for each partial step. A new model
(observation, retraction or admitted definition) invalidates pool and rejection
cache on next use. This is stricter than minimal dependency invalidation but
avoids stale outcomes. Cache keys have no dependence on 3D distance.

Maximum pool512. If construction overflows or closure is incomplete, emptying the
retained pool returns capacity, NOT saturation. Table lookups and joins use
bounded association lists, not constant-time hash maps. Building closures/pools
is synchronous and not bounded by a primitive/time budget.

## Transpositions and the trust boundary

Only `(rejected insufficient-reuse)` from complete native certification is cached.
It means the primitive path has fewer than the two source instances required by
the learner's admission policy; it is NOT logical unprovability.

The key is the complete model plus exact flattened primitive word. A complete
insufficient-reuse judgment can be shared across different composition splits:
reference path instance count depends on the word and source episodes, not the
split. Other failures (including verification/incompleteness) are never cached;
the candidate is deferred for retry and the result stays incomplete. Successful
admissions are never authorized from cache: they always run the native checker.
Changed evidence or definitions invalidates negative results.

A consumed cache hit still costs a candidate decision from the per-step budget.
This prevents unrestricted cache traversal within a bounded slice. Separate
counters report actual certification calls, negative hits and proof entries.

## Policy and work estimate

Families are `(primitive-length, left-length, right-length)`, at most six shapes
in the current grammar. Statistics `(trials, reward, cost)` persist across model
revisions, unlike rejection caches. Reward is the admitted definition's number
of source instances, capped256; rejection reward is0. This is a source-coverage
proxy, not measured future task utility or actual downstream reuse credit.

Cost is1 plus the number of closure-proof entries encountered in certification,
plus1 per inspected episode. This is deterministic instrumentation, not elapsed
time or a count of all primitive operations. It excludes candidate-generation
work, cache scans and recursive proof-check internals; wall-clock experiments
include all those costs separately.

- `cache`: indexed pool + negative cache + FIFO selection.
- `rank`: same mechanisms, highest `1024 * reward / (cost+1)` family score first.
- `ucb`: same exploitation score plus integer approximation
  `floor(sqrt(65536 * floor(log2(total+2)) / family_trials))`.
  Untried families receive score1000000. Ties preserve pool order.

No floating-point library is required. Scores guide priority only; no logical
premise or candidate is eliminated by a low score. There is no claim that this
modified cost-aware UCB has the regret guarantees of textbook UCB1.

## REPL and persistence

`search-session.l` wraps the original step while preserving its result shape.
Every controlled step logs `(search84-run budget)`, including unsuccessful and
partial steps, so policy statistics/frontier progress can be reconstructed.
`(search84 mode)` changes the policy and invalidates the frontier key. Source,
retraction, learned-definition and optional Ground83 events remain data-only.

Extended logs are explicitly tagged `dlm-session84`. Older unextended 77/83
snapshots remain accepted; older binaries reject the new84 tag. Restore replays
source events and controlled search from empty, then checks the stored native
model. Controller statistics, frontier and caches are reconstructed from the
same deterministic event sequence; they are not trusted serialized state.
Tests compare the full controller and next-step output in a fresh process.

The native checkpoint happens before publishing model/controller updates.
A pending pure result avoids repeating the live search in the commit hook;
checkpoint replay still validates the complete history. Rejected saves leave
model/controller unchanged. Live and replay both cap search requests at100000
and log length256. A saturated/waiting poll does not manufacture learning events.

Search84 uses its own candidate-pool selector, bypassing Ground83's spatial
fact-order callback. If Ground83 is also enabled its independently checked query
cache may still operate and incur rebuild costs, but spatial ordering does not
control Search84. Experiments leave Ground83 OFF to isolate this controller.
No integration with space79's separate study/machine reasoning loop is claimed.

## Experiments

Run `python3 adapters/search_experiment.py`.
Evidence: `docs/search84-experiment.json`. Fixed-round study: two workloads,
three seed permutations, four modes, three fresh-process repeats per condition.
Each receives six rounds with budget8. Legacy budgets raw pair visits, new modes
budget indexed candidate decisions; these are NOT equal primitive-work units.
All reported wall times include startup, full pool generation and in-memory
cache/controller maintenance. Persistent checkpoint replay is tested separately,
not timed in these experiments.

### Six-round results (median of per-seed median wall times)

| Workload/mode | Definitions by seed | Certification calls by seed | Seconds |
|---|---|---|---|
| Rare path / legacy | 2,2,2 | 4,3,5 | 0.3367 |
| Rare path / cache | 2,2,2 | 3,3,4 | 0.3285 |
| Rare path / rank | 2,2,2 | 3,3,4 | 0.3328 |
| Rare path / UCB | 2,2,2 | 3,3,4 | 0.3314 |
| Distractors / legacy | 1,1,1 | 1,1,1 | 0.3519 |
| Distractors / cache | 3,3,3 | 3,3,3 | 0.4720 |
| Distractors / rank | 3,3,3 | 3,3,3 | 0.4429 |
| Distractors / UCB | 3,3,3 | 3,3,3 | 0.4582 |

Rare-path cache mode avoids two repeated checks per seed across alternative
splits. On distractors, indexed search discovers more definitions within six
rounds, but doing more certification work increases total elapsed time.

### Same target: two definitions, distractor workload

All arms reached the target for all seeds. A128-round cap was applied.

| Mode | Rounds per seed | Median process seconds |
|---|---|---|
| Legacy | 7,7,7 | 0.3863 |
| Cache | 2,2,2 | 0.3431 |
| Rank | 2,2,2 | 0.3292 |
| UCB | 2,2,2 | 0.3421 |

This supports a modest observed time-to-target improvement (~11% for cache)
on this toy distractor fixture, not a broad speed claim. It does not establish
an independent UCB advantage: most of the structural difference is indexed
candidate generation, persistent frontier and cache. Family ordering differences
need richer workloads. No statistical significance or held-out generalization
claim is made from three seeds/repeats with process startup included.

Serialized controller size in the six-round runs was42 bytes for legacy versus
roughly479..1420 bytes for enabled controllers. This is a serialization proxy,
NOT resident-memory accounting, peak allocation, or an equal-memory experiment.
Caches add bounded retained state; faster search is not free storage.

## Verification

Nine new tests in `test_search84.py` cover native recursive admissions with
budget1, negative split reuse and evidence invalidation, deferred verification
failures, integer UCB exploration, full controller/next-step and saturated-wait restart, checkpoint
rollback, live/replay budget-cap agreement and actual original-REPL idle execution.
Existing proof/store/replay oracles remain enabled. Compiler/platform sources
are unchanged and must pass three-generation self-reproduction before promotion.
