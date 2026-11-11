# Release 0.0175 — dependency-aware proof cache (candidate)

- Date: 2026-11-08
- Predecessor: 0.0174. Candidate, not promoted.
- Scope: reuse a checked proof across queries when its goal, rules, and used
  facts are still live; unrelated fact additions should not invalidate it.
- Analysis: `/research/analysis-proof-cache-0175.md`.

## Changes

`src/dlm/proof.l`:

- `p-proof-givens` — collect given fact IDs from a proof tree
- `p-used-facts` — resolve used IDs to fact records
- `p-cache-live?` — all used facts must still be present exactly
- `p-cache-get` / `p-cache-put` — goal + rules + used-fact cache
- `p-clear-proof-cache`
- `p-prove` now checks the cache before search

`experiments/proof_cache_repl/` + `scripts/proof_cache.sh`.

## Experiment

```text
FIRST status=proof probes=13
CACHED status=proof probes=0 scans=0
UNRELATED status=proof probes=0
REMOVED status=fail
CHECK ok
done-proof-cache
```

- first proof: 13 probes
- same goal/facts: 0 probes, 0 scans
- unrelated fact added: still 0 probes
- a used fact removed: cache miss and proof fails
- cached proof still passes `p-proof-check`

## Self-host

```text
compiler.sh reproduce
→ 20261109T100345Z-4062
compiler.sh verify 20261109T100345Z-4062
→ Verified
```

## Measured

```text
native normal   42 checks / 0 FAIL
native safety-2 42 checks / 0 FAIL
self-host       verified
```

## Implementation note

`p-used-facts` initially used `(l-append out f)` instead of
`(l-append out (list f))`, flattening fact records into their fields. The live
check then failed. The fix makes the used-fact list structurally correct.

## Still not

- In-memory per-process cache; no disk persistence.
- Rules are compared whole; any rule change invalidates the entry.
- New unrelated facts do not invalidate, deliberately: the cached proof remains
  a valid witness.
- No cache for negative/failed goals yet.
- No proof-size/budget policy for eviction.
