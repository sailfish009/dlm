# Release 0.0141 — recursive rule-schema transfer (candidate)

- Date: 2026-11-08
- Predecessor: 0.0140. Candidate, not promoted.
- Scope: lift a learned recursive program to a relation-level schema and
  instantiate it on a new predicate pair without target labels.
- Analysis: `/research/analysis-schema-transfer-0141.md`.

## Changes

`src/dlm/d107-rulelearn.l`:

- `p107-rule-schema-from-program` extracts:
  ```text
  (schema107 TARGET BODY RECURSIVE?)
  ```
  from a checked seed+recursive program.
- `p107-rule-schema-instantiate` substitutes new relation names:
  ```text
  reaches(x,z) :- manages(x,z)
  reaches(x,z) :- manages(x,y), reaches(y,z)
  ```
- Instantiated rules must pass `p107-rule-safe?`; no truth is asserted by the
  schema itself.

## Experiment

`experiments/schema_transfer/`:

```text
source: parent/ancestor (labeled)
target: manages/reaches (no reaches labels at all)
held:   new manages chains; direct/length-2/length-3 reaches queries
```

| arm | held positives | held negatives clean | notes |
|---|---:|---:|---|
| transfer | 9/9 | 5/5 | schema instantiated on target |
| source-only | 0/9 | 5/5 | ancestor rules do not mention reaches |
| single composition | 3/9 | 5/5 | length-2 only |
| frozen | 0/9 | 5/5 | no rules |
| oracle | 9/9 | 5/5 | true target program |
| random/reverse | 0/9 | 4/5 | one false positive |
| no-source | 0/9 | 5/5 | no source labels; no schema |

This is transfer without target labels. It is structural analogy, not semantic
proof that `manages/reaches` means the same thing as `parent/ancestor`.

## Measured

```text
native normal   340 ok / 0 FAIL
native safety-2 340 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- One relation shape, one target pair, synthetic data.
- Transfer assumes the new relation has the same composition shape; there is no
  semantic validation of that analogy.
- No target labels means no target-domain FP check during transfer; held
  positives/negatives are evaluation only.
- No multi-schema selection, negation, arity>2, or live web.
- 0.0137's all-witness grounding and derived-evidence traversal remain separate.
