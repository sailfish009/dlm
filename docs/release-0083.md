# DLM 0.0083 — native REPL/Ground82 integration

Promoted release: `20261022T050940Z-18663`.
Previous directory `/research/dlm_v0.0082` is preserved.

## Implemented

- Actual `(dlm 'step/start)` feedback connection, opt-in `(dlm 'ground 'on/off)`.
- Previous-round verified spatial cache orders next-round candidates without
  adding or dropping any native candidate facts.
- Original observations retain source provenance; derived native Horn proofs
  are independently checked and stored as conditional supports, never evidence.
- Cached proof queries are filtered by source episode and reverified with the
  current native kernel; miss/stale/unavailable cache uses ordinary native query.
- Retraction rebuilds from remaining episodes, preserving independent evidence
  and learned conservative definitions without stale source facts.
- Routing mode persists as whitelisted `routing83` events. Extended checkpoints
  use `dlm-session83`; legacy `dlm-session77` remains accepted when unextended.
- Native model/events are authoritative; derived graph/layout is reconstructed
  and verified on restore rather than trusted from serialized cache data.
- Six new tests cover actual next-step feedback, proof retrieval, retraction,
  exact cache/next-step restart in a fresh process, mode rejection/ablation,
  unsupported projection fallback, and learning via the original idle REPL.

See `docs/bridge83-design.md` for architecture, trust boundaries and limitations.
No registered LLVM MLIR dialect, LLM, neural policy or new compiler dependency.

## Experiment — functionality, not speedup

`python3 adapters/bridge_experiment.py` ran OFF/ON arms for three shuffled
source fixtures, six rounds with pair-budget8 each, fresh process per arm.
Results are in `docs/bridge83-experiment.json`.

OFF discovered three path definitions for all seeds. ON discovered three for
seeds0/1 and two for seed2. All arms proved the evaluated depth-two query. ON
recorded six ordering calls, 45/45/47 candidate hits and one reverified query-cache
hit. Median observed process time: ~0.355s OFF, ~0.665s ON. Measurements include
startup, closure, proof checking and cache maintenance; small single-run fixtures
are not generalization or statistical performance evidence.

Thus integration is established, but the proposed spatial policy is not an
efficiency improvement. It remains OFF by default. Entire-cache rebuilding,
association-list cell scans and a fixed-origin layout heuristic are known costs.

## Final verification

`compiler.sh reproduce`, `verify 20261022T050940Z-18663`, and `promote` completed.

- 67 Python tests passed in 93.930s.
- Native, store, runtime, graph-store tests passed.
- Sibling0066 graph and Horn differential checks passed.
- Candidate/next/third LLVM outputs and stripped binary images matched.
- `src/maru` unchanged from v0.0082.

Logs: `docs/verification.log`, `docs/python-tests.log`, and runtime release log.
Matching manifests: `docs/release.sources.sha256`, `docs/release.tests.sha256`.
Native example output: `docs/bridge83-demo.sexp`.

Older retained release/design documents describe their respective historical
versions; this note identifies v0.0083 behavior and current verification.
