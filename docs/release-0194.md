# Release 0.0194 — persistent web observation/basis store (candidate)

- Date: 2026-11-10
- Predecessor: 0.0193. Candidate, not promoted.
- Scope: persist the in-process web observations and basis axioms to a Maru
  loadable file, then reload them in a fresh process and answer queries.
- Analysis: `/research/analysis-web-persist-0194.md`.

## Changes

`src/dlm/web.l`:

```text
w-save  writes (define *web-store* '...) and (define *web-basis* '...)
w-load  loads the file and returns (observation-count, rule-count)
```

## Experiment

Process 1:

```text
SAVE /tmp/dlm-web-store.l obs=3 rules=2
P1 proved
done-persist-p1
```

Process 2:

```text
LOAD (3 2)
P2 proved
P3 unknown
done-persist-p2
```

The second process has no in-memory setup: it loads observations and basis from
disk, proves `dog -> living thing`, and abstains on `dog -> plant`.

## Self-host

```text
compiler.sh reproduce
→ 20261110T095253Z-25297
compiler.sh verify 20261110T095253Z-25297
→ Verified
```

## Measured

```text
native normal   61 checks / 0 FAIL
native safety-2 61 checks / 0 FAIL
self-host       verified
```

## Still not

- full-store dump, no incremental journal or version history
- no atomic write/compare-and-swap
- no contradiction resolution across observations
- reload path is fixed in the experiment
- proof remains the truth gate
