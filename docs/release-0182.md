# Release 0.0182 — CSE for duplicate graph nodes (candidate)

- Date: 2026-11-08
- Predecessor: 0.0181. Candidate, not promoted.
- Scope: merge duplicate fragment/template nodes, rewrite IDs/value references,
  and preserve the graph run result.
- Analysis: `/research/analysis-graph-cse-0182.md`.

## Changes

`src/dlm/graph-ir.l`:

```text
mg-cse-key        kind + attrs + inputs
mg-cse-eligible?  fragment / template only
mg-cse-maps       old-id → canonical-id, old-value → canonical-value
mg-rewrite        recursive ID/value rewrite in attrs/inputs/outputs
mg-cse            merged graph
```

`experiments/graph_cse_repl/` + `scripts/graph_cse.sh`.

## Experiment

```text
BEFORE nodes=6 values=6
AFTER nodes=4 values=4 check=ok
OPS ... program (p (s1 s1))
BASE RUN (summary tasks 1 solved 1 active (p))
CSE RUN (summary tasks 1 solved 1 active (p))
SAME yes
done-cse
```

Two duplicate fragments and two duplicate templates collapse to one each. The
program reference `("s1" "s2")` is rewritten to `("s1" "s1")`; the run summary
is unchanged.

## Self-host

```text
compiler.sh reproduce
→ 20261109T230607Z-11295
compiler.sh verify 20261109T230607Z-11295
→ Verified
```

## Measured

```text
native normal   52 checks / 0 FAIL
native safety-2 52 checks / 0 FAIL
self-host       verified
```

## Implementation note

`mg-rewrite` first checked only list structure and returned atoms unchanged.
String IDs such as `"s2"` were therefore never rewritten. It now checks the
rewrite map for atomic values before recursing. `mg-cse-hit` was also inlined to
avoid a Maru forward-reference failure.

## Still not

- CSE only merges fragment/template nodes.
- No cost/benefit gate; duplicates always merge.
- No fusion/canonicalization.
- No graph-level proof certificate.
- Truth remains with the proof checker.
