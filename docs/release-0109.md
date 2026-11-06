# Release 0.0109 — Maru string-compare boxing; safety-2 gate green

- Date: 2026-11-06
- Predecessor: `dlm_v0.0108` preserved. Input: `/research/maru-0108-root-cause.md`.
- This release fixes a **Maru** defect, not a DLM one. Built from modified source.

## Root cause

`src/maru/source/evaluator/vm-functions.l` declared `string-compare` with no body,
so the native long bypassed boxing: `(dump (string-compare "c" "a"))` aborted with
`FATAL: type-of ... 0x2`, and comparison results were misread (0 as `()`, 1 as 0)
in ordinary builds too.

```lisp
(define-vm-function (string-compare ()) ((s1 <string>) (s2 <string>))
  (box <long> (string-compare s1 s2)))
```

The native primitive is untouched; boxing belongs in the VM wrapper only. DLM's
per-`perms`/`conj-key`/boolean flags were **not** changed (the earlier suspicion
was wrong).

## Verification (rebuilt, not reproduced)

Because the change is in the compiler source, the candidate was produced with
`compiler.sh rebuild` (seed + modified sources), not `reproduce`.

| check | normal | safety 2 |
|---|---|---|
| native checks | 72/72 | 72/72 |
| Python tests | 15/15 | 15/15 |
| three-generation LLVM/stripped | equal | equal |

Release `20261106T155013Z-17382`; manifests 25/25. `scripts/safety-build.sh`
now reports `safety2-gate: PASS`.

## Notes

- `string-compare` now returns a boxed long; DLM code that compares against 0
  (canonical keys, sorting) is unaffected in results, and the previous silent
  misreading is gone.
- The safety-2 artifact lives under `runtime/safety2/` and is not promoted;
  only the normal release is.
- Remaining limits are unchanged: no recursion, lemma or hypothesis layer;
  plan-step reduction is not a speedup; Maru's reader still aborts on invalid
  input.
