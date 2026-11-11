# Release 0.0180 — dead-node elimination (candidate)

- Date: 2026-11-08
- Predecessor: 0.0179. Candidate, not promoted.
- Scope: remove graph nodes unreachable from explicit roots, while preserving
  values/edges needed by kept nodes and the graph run result.
- Analysis: `/research/analysis-graph-dce-0180.md`.

## Changes

`src/dlm/graph-ir.l`:

```text
mg-reach       backward reachability from roots via value producers
mg-dce         keep reachable nodes, their values, and their edges
mg-keep-node? / mg-keep-value? / mg-keep-edge?
```

`experiments/graph_dce_repl/` + `scripts/graph_dce.sh`.

## Experiment

```text
BEFORE nodes=5 edges=1
AFTER nodes=3 edges=1 check=ok topo=(seed p t)
DCE RUN (summary tasks 1 solved 1 active (p))
SAME yes
done-dce
```

An unused fragment is dropped; the live `seed → p` edge is retained; graph run
summary is unchanged.

## Self-host

```text
compiler.sh reproduce
→ 20261109T120246Z-7578
compiler.sh verify 20261109T120246Z-7578
→ Verified
```

## Measured

```text
native normal   50 checks / 0 FAIL
native safety-2 50 checks / 0 FAIL
self-host       verified
```

## Implementation note

`mg-keep-edge?` first compared the edge's **value ID** to kept node IDs. The edge
was therefore dropped even though its producer node was kept. It now resolves
the value and checks the producer:

```text
edge value → mg-value-by-id → mg-value-producer ∈ kept nodes
```

## Still not

- No CSE/fusion/canonicalization yet.
- Roots are explicit; no automatic root selection.
- DCE removes values/edges but does not rewrite IDs.
- No graph-level proof certificate yet.
- Truth remains with the proof checker.
