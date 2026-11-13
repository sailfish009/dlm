# Release 0.0234 — Gate Record Alignment + Positive Control + Checksum

- Date: 2026-11-13
- Predecessor: 0.0233
- Type: candidate research release
- Runtime: `20261113T091520Z-19363`

## Fixes

- `recs` now emits `(kind subj obj text)`, matching `nl-build`.
- `GATE-POS: proof` and `GATE-NEG: fail` are explicit controls.
- `nl-fact-parse` empty-object regression test added to core tests.
- `verify.sh` re-executes `run.sh` and byte-compares output; forged outputs are
  rejected.
- checksum metadata is marked `full-extract-utf8` and `UNVERIFIED`.
- natural-language `kind` substring grep removed; leakage is computed.
- temporary plan file removed.

## Result

```text
GATE-POS proof GATE-NEG fail
RUN-REEXECUTED
GOLD-FIELDS-IN-INPUT false (computed)
SOURCE-META 6 CHECKSUM-TARGET full-extract-utf8 UNVERIFIED
V0234-PHASE5-COMPUTED-LEAKAGE-PASS
STUB-REJECTED
```

Actual web extraction remains TP0/22; the metric and gate paths are now aligned.

## Verification

```bash
cd /research/dlm_v0.0234/experiments/real_web_axiom_decomposition
./run_all.sh
./final_review.sh
```

and:

```bash
cd /research/dlm_v0.0234
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

## Limits

- Real web sample is small; extraction is rule-based.
- checksum is page-level and unverified against the passage text.
- No transformer extraction.
- MLIR not used.
