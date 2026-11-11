# Release 0.0196 — minimal atomic axioms + subset search (candidate)

- Date: 2026-11-10
- Predecessor: 0.0195. Candidate, not promoted.
- Scope: decompose a learned recursive program into individual rule axioms with
  dependencies, enumerate closed subsets, and select a minimal covering set.
- Analysis: `/research/analysis-axiom-0196.md`.

## Changes

New `src/dlm/axiom.l`:

```text
a-axiom ID RULE EVIDENCE SUPPORT DEPS VERSION STATUS HISTORY
a-from-program   one axiom per rule; dependency on earlier same-head rules
a-deps / a-closed?
a-subsets
a-rules-for
a-select         maximize coverage, then minimize axiom count
```

## Experiment

Actual web recursive self-supervision program:

```text
AX 2 SUBSETS 4 CLOSED 3
SEL (A-0 A-1) COV 3
HELD 3/3
done-axiom
```

The seed axiom alone has no two-hop coverage; the recursive step cannot be used
without its seed dependency. The search selects the two-axiom closed set, which
proves all three held-out web paths.

## Self-host

```text
compiler.sh reproduce
→ 20261110T103246Z-3815
compiler.sh verify 20261110T103246Z-3815
→ Verified
```

## Measured

```text
native normal   62 checks / 0 FAIL
native safety-2 62 checks / 0 FAIL
self-host       verified
```

## Still not

- dependency rule is simple same-head body matching
- no weighted cost/MDL across axiom combinations
- no per-rule evidence splitting (program support is copied)
- activation lifecycle is not yet integrated into subset search
- proof remains the truth gate
