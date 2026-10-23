# Search85 — review fixes and isolated native search evaluation

## Scope

This extends the existing non-neural Search84 controller in the original DLM77
Maru REPL, not a separate Python learner. Indexed candidates, complete negative
transpositions, cost-aware ranking and fixed-point UCB remain optional. There is
no MCTS rollout tree, LLM, neural value function or new MLIR/compiler dependency.
The native proof/admission kernel is unchanged; source observations and derived
results remain distinct. Earlier directories, including v0.0084, are preserved.

## Review fixes

### Capacity restart equivalence

Previously, restore inferred terminal state from an empty frontier. Definition
capacity12 can occur with a nonempty frontier, so reopening returned capacity
again instead of waiting and could append needless events/checkpoints.

Replay now returns the last controlled-search reason explicitly. Pending commits
carry that reason; `s84-sync` restores it and derives the waiting flag from
`saturated/capacity`, not pool emptiness. Source/definition/mode changes reset the
reason; unchanged Ground83 configuration does not invent a new search result.
A fresh-process test reaches12 definitions with pending candidates, then compares
the next command with uninterrupted execution. Both return waiting without a new
search event. Capacity is still reported separately from logical saturation.

### Resource-limit preflight and pause

Before pool generation or certification, a controlled step checks:

- valid budget1..1000;
- log space below256 events;
- cumulative requested search budget <=100000.

Failure clears the native idle task, leaves controller/model/progress untouched,
and returns `(paused resource-limit REASON)` without incrementing the round.
Generic rejected commits now also pause, preventing repeated idle refusal after
a log-capacity race/configuration command. This does not grant permission to
accept a candidate or reinterpret resource exhaustion as refutation.

Resource pauses cannot be logged once the log is full; they are recomputed on the
next attempted step after reopen. A saved terminal search reason is reconstructed
from successful search events. Explicit reset archives no data by itself: save
first; reset clears the model/log. There is no automatic compaction. At request
capacity but with free log space, disabling the controller remains possible.

## Indexed-only ablation

`(dlm 'search 'indexed)` uses the same endpoint-indexed candidate pool, exact
composition deduplication, persistent frontier and FIFO ordering as cache mode,
but never stores or consumes negative transposition entries. It still records
outcomes/work statistics so the comparison does not conflate policy instrumentation
with the presence of the negative cache.

The five modes are:

1. `off` (experiment label legacy): original raw-pair enumeration;
2. `indexed`: indexed frontier, no negative cache;
3. `cache`: indexed frontier plus complete insufficient-reuse cache;
4. `rank`: cache plus reward/cost family ordering;
5. `ucb`: cache plus family exploration bonus.

Positive admissions always call `a77-certify`. Verification/incomplete failures
stay retryable and are never cached as logical impossibility. Statistics transfer
across model revisions; negative caches invalidate on every model change. Score
reward remains source coverage, not measured downstream wall-time savings.

Search85 still bypasses Ground83's spatial candidate-order callback. Its verified
query cache can coexist but adds costs; all experiments leave Ground83 OFF.
Separate space79 proof-study modes are not controlled by Search85.

## Persistence and compatibility

Public configuration now logs `(search85 MODE)` and uses `dlm-session85`.
The search-step event remains `(search84-run BUDGET)` because its deterministic
search transition format is unchanged. Old77/83/84 snapshots remain readable.
New indexed/configuration events cannot masquerade under an old snapshot tag;
old binaries reject session85. Tests verify both cases.

The snapshot stores authoritative native model/events, not trusted serialized
controller tables. Replay reconstructs controller statistics, frontier and stop
reason, checks the native model, and restores before the next learning step.
The existing lock/atomic checkpoint path and rollback contract remain in use.
There is no fsync, source authentication or unlimited-duration curriculum claim.

## Experiment protocol

`python3 adapters/search85_experiment.py` produces
`docs/search85-experiment.json` using90 fresh native processes:

- mixed-relationship fixed-six-round study: 3 structurally varied seeds x5 modes
  x2 repeats =30 runs;
- distractor time-to-two-definitions study: 3 seeds x5 modes x2 storage settings
  x2 repeats =60 runs;
- all arm executions shuffled with a fixed scheduling seed;
- budget8 per step, time-to-target cap128 steps;
- useful facts are shuffled too; graph/path lengths and noise counts vary;
- mixed relation patterns vary between seeds, creating different candidate families.

Parent-observed stdout markers bound the learning interval and durable close.
`search_seconds` includes per-step checkpoint replay when attached. Workflow time
includes process startup, store open, source/configuration commits, search and
close. Diagnostic serialization and held-out evaluation occur AFTER these markers.
No Python candidate selection or training is used.

A cold graph is presented only after timing/training. Every resulting native
proof is rechecked, and the number of derived instances is independently compared
with flattened primitive-path semantics. This is a small formal transfer probe,
not natural-language/world reasoning or a broad generalization benchmark.

Parent marker timestamps have scheduling/pipe-resolution noise; timings are not
hard-time guarantees. Only two repeats per condition and three seeds were used.
VmHWM sampling is a whole-process high-water proxy (including post-search probe),
not an equal-memory budget or precise search-only peak. Process samples were
15796..16004 KiB; serialized controller state42..1178 bytes.

## Results

Values below are medians across all seed/repeat runs for that row.

### Six rounds, mixed relationships, in memory

| Mode | Definitions by seed | Held-out proved instances by seed | Certification calls by seed | Search seconds |
|---|---|---|---|---|
| Legacy | 2,2,2 | 3,0,2 | 5,3,3 | 0.1988 |
| Indexed | 3,3,6 | 5,2,4 | 11,8,12 | 0.2667 |
| Cache | 3,3,6 | 5,2,4 | 8,8,11 | 0.2589 |
| Rank | 3,3,6 | 5,2,4 | 7,10,13 | 0.2941 |
| UCB | 3,3,6 | 5,2,4 | 8,8,16 | 0.2921 |

Cache versus indexed-only isolates a real reduction of repeated certification
(3,0,1 negative hits by seed in cache mode). More definitions/held-out instances
were found than legacy within six rounds, but more total work was performed.
Rank/UCB did not improve held-out coverage or final definition count over cache;
some seeds increased certification calls. This does not support a UCB advantage.

### Same target: two definitions, varied distractors

All arms reached the target. Legacy took6/12/13 rounds by seed; all indexed modes
needed2 rounds per seed. Budget units differ (raw pairs vs indexed candidates),
so fewer rounds alone is not an elapsed-time or equal-work claim.

| Mode | In-memory search s | In-memory workflow s | Attached search s | Attached workflow s |
|---|---|---|---|---|
| Legacy | 0.1991 | 0.3553 | 0.2232 | 0.6369 |
| Indexed | 0.1688 | 0.3563 | 0.2282 | 0.6621 |
| Cache | 0.1450 | 0.3241 | 0.2377 | 0.6955 |
| Rank | 0.1477 | 0.3190 | 0.2236 | 0.6908 |
| UCB | 0.1464 | 0.3206 | 0.2402 | 0.6972 |

In-memory cache/rank/UCB workflows were modestly faster on this fixture, but
negative caches are not consumed in the target-two case; do not attribute those
small timing differences to transposition learning or UCB. Attached workflow was
slower for indexed/controller arms. Median certification invocations, including
checkpoint/close replay, rose from2 in-memory to15 attached in every arm.
Checkpoint replay/initialization costs dominate the persistent result. Legacy
partial steps do not have the same persistence guarantees as controlled partial
steps, another reason to avoid interpreting this as a universal algorithm ranking.

## Interpretation and next priority

- Review boundary bugs are fixed and regression-tested.
- Matching/indexed frontiers and negative reuse are useful mechanisms.
- UCB/ranking have not demonstrated a separate benefit on these workloads.
- Persistent deployment is not faster overall in this experiment.
- Search remains OFF by default; cache/indexed are explicit investigation modes.

Next work should target validated incremental checkpoint/replay and finer
cache invalidation, then evaluate more predictive utility/cost signals. Adding a
full MCTS tree before addressing these costs is not supported by these results.

## Verification

Five new tests in `test_search85.py` cover nonempty-pool capacity restart,
actual idle pause at event exhaustion, valid-history request exhaustion,
indexed-only versus negative-cache behavior, and explicit old/new snapshot tags.
All inherited tests remain, with the public-command snapshot expectation updated
from84 to85. Final release logs/manifests and three-generation reproduction are
recorded in `docs/release-0085.md`.
