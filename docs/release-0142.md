# Release 0.0142 — evidence-based schema selection (candidate)

- Date: 2026-11-08
- Predecessor: 0.0141. Candidate, not promoted.
- Scope: replace 0.0141's untested structural transfer with a small target
  calibration check and candidate-schema selection.
- Analysis: `/research/analysis-schema-selection-0142.md`.

## Changes

`src/dlm/d107-rulelearn.l`:

- `scandidate107 NAME RULES` packages a transfer candidate.
- `p107-schema-eval` runs a candidate with the Horn kernel over calibration
  facts and counts positive/negative target hits.
- `p107-schema-select` chooses the candidate with maximal calibration TP and
  FP=0; it returns `(selected107 NAME RULES TP FP CANDIDATES)` or `(none ...)`.
- Selection does not mutate a basis; the caller installs the returned rules.

## Experiment

`experiments/schema_selection/`:

```text
source: parent/ancestor (labeled)
target: manages/reaches
calibration: one held-aside chain with a few reaches labels
candidates: direct, single composition, recursive, reverse
held: three new chains, evaluation only
```

| arm | selected/installed | held positives | held negatives clean |
|---|---:|---:|---:|
| select | recursive | 9/9 | 5/5 |
| first candidate | direct | 3/9 | 5/5 |
| single | single composition | 3/9 | 5/5 |
| frozen | none | 0/9 | 5/5 |
| oracle | recursive | 9/9 | 5/5 |
| random | reverse | 0/9 | 4/5 |
| no-calibration | none | 0/9 | 5/5 |
| source-only | ancestor rules | 0/9 | 5/5 |

Calibration: recursive candidate TP=2, FP=0; single TP=1, FP=0; direct TP=0.
The selector chose recursive and held 9/9.

## Measured

```text
native normal   343 ok / 0 FAIL
native safety-2 343 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Candidate schemas are hand-supplied; selection does not invent new schemas.
- Calibration labels are required; no-calibration abstains.
- One relation shape, synthetic data.
- Selection is calibration fit, not proof-DAG credit or failure-frontier
  attribution.
- No multi-schema composition, negation, arity>2, live web.
- 0.0137's all-witness grounding and derived-evidence traversal remain separate.
