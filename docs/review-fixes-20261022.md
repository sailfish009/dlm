# v0.0080 review-defect fixes

Source review: `docs/review_20261022.md` against `dlm_v0.0079`.
This release keeps the v0.0079 runtime/release image and changes DLM application
sources only.

## Fixed contracts

| Finding | Change | Regression |
|---|---|---|
| P1 malformed definition signature crashed in `dlm-length` | `space-definitions.l` checks `sq-signature?`/`sq-name?` before length and limit checks; session replay uses the same path | `test_malformed_signature_is_rejected_not_a_crash` |
| P2 failed certificate check left the purpose job in `checking` | `s79-check-fail` finishes the check unit and resolves its `job` or `reuse` purpose | `test_check_failure_finishes_the_purpose_job` |
| P2 exhausted alternatives stayed `waiting` | `s79-program-fail` counts active statuses only; `s79-program-resume` moves an all-terminal program to `exhausted` | `test_alternative_exhaustion_is_terminal` |
| P2 rejected child job suspended the parent silently | `i79-child-job` fails the parent unit and completes its job with `(internal79 rejected ...)` | `test_child_job_rejection_and_beth_capacity_are_explicit` |
| P2 Beth limit was checked only at submit | Beth verification rechecks capacity and name collision before storing the definition | same test checks 64 stored definitions and an explicit `capacity` result |
| P2 annotation traversal re-expanded shared DAG regions | `i79-annotation-step` memoizes `(node-id, left-colors, right-colors)`; color lists stay part of the key | `test_annotation_traversal_is_linear_in_certificate_dag` |

## Annotation traversal

`docs/review-evidence/annotation.l` now reports:

```
(depth 2 certificate-nodes 3 annotation-events 7)
(depth 4 certificate-nodes 5 annotation-events 13)
(depth 6 certificate-nodes 7 annotation-events 19)
(depth 8 certificate-nodes 9 annotation-events 25)
(depth 10 certificate-nodes 11 annotation-events 31)
```

The previous counts were `10, 46, 190, 766, 3070`. The memo key includes both
partition color lists; caching by node ID alone would be unsound because the same
certificate node can be visited with different partitions.

## Verification

```
python3 -m unittest discover -s tests -p 'test_*.py' -v
Ran 48 tests in 72.774s
OK
DEFINABILITY-ORACLE 16 Beth theories, 256 Craig pairs, zero mismatches
ND78-ORACLE 417 sequents, four valuations each, zero mismatches
ORACLE 3392 sequents, all 4 valuations each, zero mismatches
DEFINITION-ORACLE 8 graphs, 47 definitions, zero mismatches
SPACE79-ORACLE 417 sequents, zero mismatches
SPACE79-INTERPOLATION 100 formula pairs; BETH six theories, zero mismatches
```

The new tests are in `tests/test_review80.py`; the existing v0.0079 suite and
inherited oracles remain green. No compiler, MLIR dialect, neural training or
performance claim is added by this release.