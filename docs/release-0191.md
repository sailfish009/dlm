# Release 0.0191 — incremental web observation/basis store (candidate)

- Date: 2026-11-10
- Predecessor: 0.0190. Candidate, not promoted.
- Scope: accumulate web observations across ingest turns in one process; reuse
  previously learned basis rules for a later page/query.
- Analysis: `/research/analysis-web-store-0191.md`.

## Changes

`src/dlm/web.l`:

```text
*web-store* / *web-basis*
w-ingest / w-facts / w-rules / w-clear
```

`src/dlm/nl.l`:

```text
nl-split-article: accepts "Is a cat an animal?"
```

## Experiment

```text
STORE1 obs=3 rules=2 Q1=proved
STORE2 obs=4 rules=2 Q2=proved Q3=proved
A2 Yes, a cat is a living thing.
done-store
```

Page 1 adds a fact plus two universal rules. Page 2 adds only a cat fact; the
existing rules answer the new query.

## Self-host

```text
compiler.sh reproduce
→ 20261110T090343Z-15278
compiler.sh verify 20261110T090343Z-15278
→ Verified
```

## Measured

```text
native normal   60 checks / 0 FAIL
native safety-2 60 checks / 0 FAIL
self-host       verified
```

## Still not

- in-process only, no disk persistence
- observations are append-only with no contradiction handling
- basis is recomputed, not versioned per ingest
- no open-web extraction
