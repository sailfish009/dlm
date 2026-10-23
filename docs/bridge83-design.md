# DLM 0.0083: native REPL learning and Ground82 integration

## Contract and scope

This release connects the existing DLM77 `(dlm 'step)` and cooperative
`(dlm 'start ...)` loop to an optional grounded spatial cache. It is NOT a new
learner, an LLM, a learned embedding, an actual MLIR dialect or an efficiency
promotion. DLM77 recursive conservative relation-definition learning remains the
source of new operators. Space79 study/reasoning modes are unchanged; this bridge
is specifically for DLM77, not every legacy learning mode.

Routing is opt-in and OFF by default. Existing sessions without routing events
keep the previous enumeration policy. Previous version directories are preserved.

## Run in the original Maru REPL

```
./scripts/run.sh repl
```

```
(dlm 'open "/tmp/bridge83.sexp")
(dlm 'demo)                     ; explicit source fixture, not injected axioms
(dlm 'ground 'on)
(dlm 'step)
(dlm 'ground)
(dlm 'start 1000)               ; same process, original cooperative reader
(dlm 'pause)
(dlm 'query 'demo-a '(atom "c77-0" (a c)))
(dlm 'save)
(dlm 'close)
```

`./scripts/selfssl.sh /tmp/bridge83.sexp` also uses the same learner and bridge.
`(dlm 'ground 'off)` is an explicit ablation. Status includes cache readiness,
unit/source counts, ordering invocations, candidate hits and verified query hits.
Counters are diagnostic process-local values, not persisted learning statistics.

## Connection points

1. `a77-step` obtains its candidate facts through `a77-search-facts`. An optional
   callback may reorder them; the wrapper checks a same-length permutation with
   no introduced or omitted atoms. All pair-budget, cursor and certification
   logic remains in the native learner.
2. `d77-commit` rebuilds the bridge only AFTER the original model checkpoint
   succeeds. Rejected checkpoint/model updates do not publish a new bridge.
3. `d77-open` rebuilds after native snapshot replay/validation; reset clears the
   routing log and disables the bridge. Retraction rebuilds from remaining sources.
4. `d77-query` may retrieve a cached proof through complete spatial retrieval,
   restricted to the requested episode, and rechecks it with current facts/rules.
   Miss/unavailable/stale cache falls back to the native query implementation.

The previous cache is consumed by the next learning step before that step's
admission causes a rebuilt cache. This is actual feedback into candidate ordering,
not just printing a spatial visualization after independent learning.

## Provenance and proof boundary

`ground-bridge.l` builds an ephemeral Ground82-shaped index from the current
replay-verified DLM77 model. Only original episode facts call `g82-observe` with an
explicit source record. Their metadata is honestly labeled `unhashed-native-event`
and `replay-order`: no content hash or wall-clock attestation is fabricated.

Derived atoms must pass `dlm-verify-proof` against that episode's ORIGINAL facts
and the current certified conservative definition rules. They are inserted as
conditional supports referring to premise-unit IDs, with `(native83 proof)`
certificates. They are NEVER inserted as observations. Recursive proof premises
remain linked; no cross-episode knowledge is asserted. Definitions are not world
facts and remain available after supporting episodes are removed.

This native Horn admission path is deliberately distinct from `g82-derive`, whose
certificates remain G3c propositional sequents. Do not pass the bridge's private
state to `g82-snapshot`: Ground82's event codec does not encode native83 admission.
No claim is made that a Horn conclusion is a propositional tautology. Rebuilding
uses the native checker rather than trusting serialized cached supports.

The bridge currently retains one closure proof per atom, following the native
closure API; it does not collect every alternative proof. Source-isolated units
avoid merging independent episodes incorrectly. On retraction, the whole cache
is rebuilt, dropping stale claims but preserving independent episodes. This is
not an append-only long-term archival store. The durable model/events and learned
definitions are the authority.

## Spatial policy

Primitive and derived native atoms map to exact ground predicate formulas. The
projection supports string/symbol constants; other native terms remain legal for
the learner but mark this cache unavailable. Complete closure and <=256 cached
units are required; otherwise native learning/query continues without routing.

Placement starts from a deterministic integer-grid scatter, then applies two
local Ground82 relaxation iterations to each derived unit using dependency edges.
The spatial cell query selects nearby exact-formula candidates around the origin
with radius16. All original candidate atoms are retained; near matches receive
priority and remaining matches are ordered by distance. Scores are computed once
per ordering invocation. This is a deterministic heuristic, not a trained policy.
The origin/radius are fixed in this prototype; query-conditioned placement and
usage-weight learning are not implemented.

Cached IDs are opaque revision-local projections, not stable durable knowledge
IDs across model rebuilds. Native `(episode-id, atom)` is the semantic identity.
Canonical rebuild guarantees identical index/layout for an identical saved model.
No public bridge command mutates layout independently; arbitrary low-level edits
to globals are outside persistence guarantees.

## Persistence

`routing83 on/off` is a whitelisted data-only event, committed with the existing
checkpoint/lock pipeline. Sessions containing these events are explicitly tagged
`dlm-session83`, while unextended sessions keep `dlm-session77`. New code accepts
both; previous-version readers reject the new tag. Source/model data are not
silently migrated. Derived proof/layout caches are not serialized: they are
reconstructed and verified from the authoritative model after reopening.

Tests compare the ENTIRE rebuilt cache/mapping in a fresh process and the next
learning-step result. Checkpoints retain their previous atomic replacement and
lock behavior; no fsync/authentication/distributed transaction claim is added.

## Experiment

```
python3 adapters/bridge_experiment.py
```

Three shuffled versions of an explicit two-episode, four-edge chain fixture.
Each arm receives six rounds, with pair-check budget8 per round. Each arm uses a
fresh process. Wall time includes startup, closure, proof checking, spatial
routing and full cache rebuilds. Pair budget is not a primitive/time bound.

Recorded results: `docs/bridge83-experiment.json`.

| Seed | Routing OFF: learned path lengths | Routing ON: learned path lengths |
|---|---|---|
| 0 | 2,3,4 | 2,3,4 |
| 1 | 2,3,4 | 2,3,4 |
| 2 | 2,3,4 | 2,3 |

All six arms proved the evaluated depth-two query. ON consumed the cached
candidates in all six rounds (45/45/47 candidate hits by seed) and retrieved one
independently rechecked query proof. OFF had no spatial cache or routing hits.
Median observed total process time was about 0.355s OFF versus 0.665s ON.
These are small single-run-per-seed measurements, not statistical estimates.

**Negative result:** the bridge is functional, but this layout/routing policy does
not improve efficiency; it adds overhead and can delay a discovery under budget.
Default routing therefore remains OFF. No held-out generalization, neural
learning, better accuracy or speedup is claimed. Next work should reduce global
rebuild/table-scan cost and evaluate goal-conditioned or use-weighted policies,
not assume that three-dimensional proximity is inherently a good search order.

## Tests

Six new tests in `tests/test_bridge83.py` cover real next-round cache consumption,
proof retrieval/verification, source retraction, a fresh-process restart with
identical cache and next step, explicit mode ablation/rejection, numeric-term
fallback, and idle learning in the original REPL. Inherited Ground82 and native
learning/oracle/store tests remain required. See release-0083.md for final logs.
