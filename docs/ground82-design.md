# Ground82: grounded-support graph and independent 3D placement

## Scope

This is a native Maru reference prototype, not a neural latent model or a registered
MLIR dialect. It implements the first design stage: provenance, proof-checked
conditional supports, retraction, independent integer-grid placement, a rebuildable
cell index, local layout relaxation, bounded candidate queries and replay-verified
snapshot data. No LLM, Python model, GPU or new runtime dependency is used by it.
Existing space79 and the optional v0.0081 Python dialect remain separate APIs.
There is no automatic import of their stores or claims into Ground82.

## State and trust

`(ground82 signature evidence units placements cells semantic-revision layout-revision)`

IDs are stable names (string or symbol). A unit binds an ID permanently to a
formula in an explicit classical-propositional signature. Unit fields are:
`id, formula, evidence-ids, supports, active`. Each support stores dependency IDs
and its checked G3c certificate. Formula and provenance identity never depend on
coordinates. There are at most 256 units and 256 evidence records.

Evidence records have `id, source, method, content-digest, observed-at, active`.
They are **explicit caller observations**, not independently established world
truth. Digest/time are caller-supplied metadata, not computed/attested by this
module. Evidence is append-only by identity; payload replacement is rejected.
The prototype has no web/sensor acquisition, confidence calibration, evidence
content blob store, source authentication or acquisition-policy enforcement.

`g82-observe` accepts an observation under a recorded evidence ID. `g82-derive`
requires an independently accepted `sq-verify` certificate proving the conclusion
from exactly the dependency formulas. It retains assumptions: it does not promote
a conditional derivation into an unconditional axiom. Alternative evidence and
alternative certified supports are preserved. Opposing observed claims may coexist;
this layer does not supply a consistency-admission policy. Classical derivation
from inconsistent premises remains possible; source provenance is not a claim
of global consistency.

## Retraction

Retraction disables evidence, then recomputes the least active fixed point from
scratch. A unit is active iff some active evidence supports it OR some certified
support has all dependencies active. Empty-dependency checked theorems are active.
Resetting activation before recomputation ensures unsupported cycles cannot keep
themselves alive. Independent supports survive. Dependency certificates stay
stored while their activation changes. Recompute is deliberately bounded/global,
not an incremental reverse-dependency algorithm.

## Geometry and search

Points are integer triples in `[0,63]^3`. One integer point is one grid cell;
multiple units can occupy it. `g82-place` changes placement/layout revision only;
semantic graph and semantic revision remain identical. Unplaced units are legal.
`g82-reindex` deterministically rebuilds the cell-to-ID association lists from
placements. Placement is not an inference rule.

`g82-query state formula center radius complete?` returns:
`(query82 complete|incomplete matching-active-ids unit-checks cell-checks)`.
Local mode uses cells within Euclidean radius and exact formula equality/active
status. Its result is always marked incomplete, even if no hit was found.
Complete mode appends all remaining units, including unplaced units, and therefore
returns all active exact-formula matches regardless of geometry. This is exact
formula retrieval, not general unification or arbitrary theorem search.

The prototype cell table is a bounded association list and queries scan occupied
cells. There is no O(1) hash lookup, octree, predicate index or proven latency gain.
Counters include both candidate unit checks and scanned cells, but not every
primitive table traversal. Cost should not be inferred from candidate count alone.

## Adaptive layout

`g82-relax state id budget` performs up to 64 local iterations. Each iteration
considers six axis neighbors; the score is incident support-edge squared distance
plus 8 per other unit in the destination cell plus a unit move penalty. Only a
strictly improving move is committed. Coordinates and layout revision can change;
logical content, evidence and proofs cannot. The graph provides structural
weights through support incidence, not learned co-use statistics. This is a
heuristic local objective, not a global optimum or learned semantic embedding.
There is no global repulsion, hardware-aware partitioner or measured net gain.

## API example

```
./scripts/run.sh proof experiments/space/ground82.l
```

The example reports cost 400 -> 1, placement `(20 0 0)` -> `(1 0 0)`, improved
local recall for its two units, unchanged complete matches, and both units
unsupported after their sole evidence is retracted. This tiny example is an
invariant demonstration, not an efficiency/generalization benchmark.

## Persistence

`g82-event` accepts only a fixed data-only command set: evidence, observe, derive,
retract, place, relax. `g82-snapshot signature events` builds
`(ground-session82 1 signature events full-state)` by replay. `g82-restore`
replays at most 1024 events from empty and compares the entire graph, layout,
cell index and revisions. Forged state/layout or unknown commands are rejected.
No `eval` is used. Native dump/read can transport this data; no new file writer,
locking, atomic-save launcher, automatic migration or crash durability is provided.
This codec is separate from existing space-session79.

## Verification and next steps

`tests/test_ground82.py` checks six contracts: independent evidence retraction,
alternative supports/unsupported cycles, coordinate invariance and complete
fallback, local relaxation, forged proofs/input rejection, and snapshot replay.
All inherited tests and compiler self-reproduction remain required.

Next work: equal-budget full/random/adaptive layout experiments with wall-time,
index maintenance and memory accounting; incremental reverse-dependency updates;
real provenance acquisition policy; registered MLIR ops/types/effects only after
these semantics are stable. MLIR is optional and must not enter Maru bootstrap.
