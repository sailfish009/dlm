# Release 0.0203 — DT proof-state dialect (candidate)

- Date: 2026-11-10
- Predecessor: 0.0202. Candidate, not promoted.
- Scope: a first MLIR-shaped deduction-transformer dialect that represents
  facts/atomic axioms/positives/negatives/goal/query-facts, performs minimal
  axiom selection, and invokes the proof checker.
- Analysis: `/research/analysis-dtir-0203.md`.

## Dialect

```text
mdmodule
mdop facts
mdop axioms
mdop pos
mdop neg
mdop query-facts
mdop goal
md-run
```

`dt-run`:

```text
facts + atomic axioms + pos/neg
→ a-select
→ selected rules
→ p-prove
→ (dt-result name selected coverage proof-status)
```

## Experiment

Actual web recursive atomic axioms:

```text
DT name=dt1 selected=(A-0 A-1) cov=3 proof=proof
done-dtir
```

## Self-host

```text
compiler.sh reproduce
→ 20261110T121123Z-26575
compiler.sh verify 20261110T121123Z-26575
→ Verified
```

## Measured

```text
native normal   68 checks / 0 FAIL
native safety-2 68 checks / 0 FAIL
self-host       verified
```

## Still not

- this is a DT **proof-state dialect**, not a neural DT-1 transformer
- no tensor/attention ops yet
- no looped proof-step block
- no verifier barrier enforced by MLIR passes
- truth remains with the proof checker
