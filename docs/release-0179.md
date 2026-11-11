# Release 0.0179 — embedding-prioritized graph scheduling (candidate)

- Date: 2026-11-08
- Predecessor: 0.0178. Candidate, not promoted.
- Scope: use advisory node embeddings to choose among currently-ready nodes in a
  topological schedule; graph execution results must remain unchanged.
- Analysis: `/research/analysis-graph-schedule-0179.md`.

## Changes

`src/dlm/graph-ir.l`:

```text
mg-node-score       query/node dot product, -1 when missing
mg-ready-best       highest-scoring currently-ready node
mg-topo-ranked      dependency-respecting, embedding-prioritized order
mg-to-module-ranked graph → linear module in ranked topo order
```

`experiments/graph_schedule_repl/` + `scripts/graph_schedule.sh`.

## Experiment

```text
GRAPH ok
EMBED ok
BASE (fseed seed p t1 t2 t3)
RANKED (t3 seed p fseed t1 t2)
BASE RUN (summary tasks 3 solved 3 active (p))
RANK RUN (summary tasks 3 solved 3 active (p))
SAME yes
done-schedule
```

The embedding changes the ready-node order, but dependency order is preserved
(`seed` before `p`), and the graph run summary is identical.

## Self-host

```text
compiler.sh reproduce
→ 20261109T115310Z-11755
compiler.sh verify 20261109T115310Z-11755
→ Verified
```

## Measured

```text
native normal   49 checks / 0 FAIL
native safety-2 49 checks / 0 FAIL
self-host       verified
```

## Implementation note

`mg-ready-best` initially seeded `best-s` to `-1`. A negative dot product then
looked worse than an empty candidate, so scheduling stopped early and looked
like a cycle. The condition is now:

```text
(or (not best) (> s best-s))
```

`mg-last-order` was used only for debugging and was removed.

## Still not

- Embedding only reorders ready nodes; no candidate proof selection yet.
- Scores are fixed-point integers from the offline sidecar.
- No random/degree baseline comparison yet.
- No cost model (proof probes, cache cost) in scheduling.
- Truth remains with the proof checker.
