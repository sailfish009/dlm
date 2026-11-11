# Release 0.0161 — proof-DAG credit, failure frontier and recursive curriculum (candidate)

- Date: 2026-11-08
- Predecessor: 0.0160. Candidate, not promoted.
- Scope: proof-carrying closure, counterfactual rule credit, failure frontier,
  and a failure-triggered recursive program curriculum in the Maru REPL.
- Analysis: `/research/analysis-proof-credit-0161.md`.

## Changes

New `src/dlm/proof.l`:

- `p-close` — closure where derived facts carry `(pr rule-index subst child-ids)`
- `p-proof` — proof term for a ground goal
- `p-essential-rules` — counterfactual rule credit: remove a rule and re-prove
- `p-frontier` — first missing ground body atom/goal
- fixed `l-lookup` to return the complete fact list (proof children need all IDs)

## Experiment

`scripts/proof.sh` runs a recursive failure-triggered curriculum:

```text
Round 1: p-rec active
  ancestor proof: essential rules (0 1)
  path frontier: missing path(r,t)

Round 2: add p-comp after frontier
  path proof: essential rule (2)
  ancestor2: essential rules (0 1) — p-rec retained

frozen: path frontier remains missing
```

Thus:

- proof DAG exposes which rules are necessary
- failure frontier selects the missing program
- previous program is retained and reused
- held/curriculum tasks complete after the new program is added

## Self-host

```text
compiler.sh reproduce
→ 20261109T074936Z-10091
compiler.sh verify 20261109T074936Z-10091
→ Verified
```

Verify includes:

```text
ALL-CORE-TESTS-PASSED
MLIR module 4/4
typed module 4/4
proof credit/frontier
next/third LLVM and stripped equality
```

Only benign clang target-triple warnings remain.

## Measured

```text
native normal   11 checks / 0 FAIL
native safety-2 11 checks / 0 FAIL
self-host       verified
```

## Still not

- Proof DAG dominant analysis is counterfactual, not full SSA dominance.
- Credit is per-rule index, not per-fragment/port/provenance.
- Failure frontier selects from a fixed program library; no new rule invention.
- Fixed tasks/alignments; positive/negative outcomes are constraints.
- No general theory revision or label-free self-supervision.
