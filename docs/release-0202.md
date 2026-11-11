# Release 0.0202 — basis CSE in self-supervision loop (candidate)

- Date: 2026-11-10
- Predecessor: 0.0201. Candidate, not promoted.
- Scope: deduplicate identical basis axioms between self-supervision rounds.
- Analysis: `/research/analysis-selfssl-cse-0202.md`.

## Changes

`src/dlm/basis.l`:

```text
b-key   rules + evidence + support
b-cse   keep first axiom per identical key
```

`src/dlm/selfssl.l` applies `b-cse` after adding each round's axiom.

## Experiment

Before:

```text
ROUND 1 pos=8 new=5 rules=2
ROUND 2 pos=8 new=0 rules=2
ROUND 3 pos=8 new=0 rules=2
FINAL pos=8 rules=6 HELD 3/3 NEG fail
```

After:

```text
ROUND 1 pos=8 new=5 rules=2
ROUND 2 pos=8 new=0 rules=2
ROUND 3 pos=8 new=0 rules=2
FINAL pos=8 rules=2 HELD 3/3 NEG fail
```

The loop still saturates, but duplicate axioms no longer inflate the active
rule set from 2 to 6.

## Self-host

```text
compiler.sh reproduce
→ 20261110T115812Z-20855
compiler.sh verify 20261110T115812Z-20855
→ Verified
```

## Measured

```text
native normal   67 checks / 0 FAIL
native safety-2 67 checks / 0 FAIL
self-host       verified
```

## Still not

- full basis graph CSE/DCE in the loop
- no version/history merge policy
- no proof/coverage check that dedup preserves semantics
- batch loop, not REPL resident
- truth remains with the proof checker
