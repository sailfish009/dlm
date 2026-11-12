# Release 0.0231 — Honest Web-Schema Learning Benchmark

- Date: 2026-11-12
- Predecessor: 0.0230
- Type: candidate research release
- Runtime: `20261112T233118Z-6094`

## What changed

- Added `experiments/web_schema_honest_lab/`:
  - predicate/arity derived from parsed web observations;
  - no-web arm produces `SCHEMA none` and zero synthetic data;
  - two candidate rules (transitivity, symmetry);
  - train negative within train entities;
  - rename arm and content-destruction arm;
  - separate oracle proof-count probe;
  - experiment files included in the release source manifest.
- No Python is used in the lab.

## Result

```text
WEB TEXT 11 RECORDS 11 SCHEMA isa/2 has-web
SYNTH TRAIN 5 TEST 6 TEST-GOALS 2
BASELINE 0/2 TEMPLATE 2/2 LEARNED 1 AFTER 2/2
CANDIDATES 2 TRANS-NEG 0 SYM-NEG 1 (want 0 0) RENAME 2/2 DESTROY 0/2
NO-WEB SCHEMA none/2, SYNTH 0
ORACLE PROVED 9/15 NEG 0 (want 0)
```

The template and learned arms both reach 2/2; this still shows that a
transitivity template is sufficient on this synthetic family. Candidate 2
(symmetry) is rejected by the train negative. The content-destruction arm and
no-web arm fail as expected.

## Verification

```bash
cd /research/dlm_v0.0231/experiments/web_schema_honest_lab
./run_all.sh
```

```text
V0231-WEB-SCHEMA-HONEST-PASS
```

Release:

```bash
cd /research/dlm_v0.0231
./scripts/verify_release.sh
```

## Limits

- Web contributes schema, not facts; entities/chains are synthetic.
- Template arm and learned arm are not separated by accuracy on this family.
- No transformer comparison yet.
- MLIR not used.
