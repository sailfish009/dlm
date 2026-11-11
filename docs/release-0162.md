# Release 0.0162 — frontier-driven rule synthesis and recursive curriculum (candidate)

- Date: 2026-11-08
- Predecessor: 0.0161. Candidate, not promoted.
- Scope: synthesize a composition rule from failure-frontier facts, check it
  against a positive goal and a negative relation, then reuse it on held tasks.
- Analysis: `/research/analysis-synth-frontier-0162.md`.

## Changes

New `src/dlm/synth.l`:

- `s-candidates` — find two binary facts connecting the failed goal endpoints
- `s-synthesize` — propose `R(x,z) :- P(x,y), Q(y,z)` from those facts
- support/provenance: the two fact IDs used in synthesis
- admission requires:
  - synthesized rule proves the failed positive goal
  - no negative fact is derived
- fixed `l-var` constructor in the minimal logic core.

## Experiment

`scripts/synth.sh`:

```text
ROUND1 ancestor proof
FRONTIER missing path(r,t)
SYNTH synth107 support=(h0 h1)
PATH proof negative=clean
ESSENTIAL (2)
HELD PATH proof
RETAINED ANCESTOR proof
FROZEN FRONTIER missing path(r,t)
```

That is:

1. p-rec proves ancestor.
2. path fails; frontier names `path(r,t)`.
3. hop1(r,s), hop2(s,t) facts synthesize
   `path(x,z) :- hop1(x,y), hop2(y,z)` with support h0,h1.
4. synthesized rule proves path and does not derive path(t,r).
5. the rule proves a held path chain and p-rec remains usable for ancestor.

## Self-host

```text
compiler.sh reproduce
→ 20261109T075609Z-5928
compiler.sh verify 20261109T075609Z-5928
→ Verified
```

Verify includes core, MLIR, typed, proof, synth, and next/third equality.
Only benign clang target-triple warnings remain.

## Measured

```text
native normal   13 checks / 0 FAIL
native safety-2 13 checks / 0 FAIL
self-host       verified
```

## Still not

- Synthesis is limited to two binary facts sharing an endpoint/middle.
- Fixed tasks/alignments; no general ILP search.
- Provenance is fact-ID support, not full source/span/quote in this layer.
- No minimality/independence or theory revision.
- Task positive/negative are fixed constraints; not label-free self-supervision.
