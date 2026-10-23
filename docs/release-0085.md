# DLM 0.0085 — native search review fixes and experiments

Promoted release: `20261023T095209Z-2106`.
Previous directories, including `/research/dlm_v0.0084`, are preserved.

## Implemented

- Capacity/saturation stop reason is reconstructed explicitly from replay.
  Definition capacity12 with a nonempty candidate pool now resumes waiting,
  identically to uninterrupted execution, without an extra search event.
- Controlled steps preflight event/request/budget bounds before generating pools
  or verifying candidates. Exhaustion pauses native idle learning without model,
  controller or round progress; generic rejected commits also pause.
- An indexed-only mode isolates endpoint matching/frontier effects from negative
  transpositions. Cache/rank/UCB remain available, with native approval unchanged.
- New configuration events use explicit session85 tagging. Old77/83/84 stores
  remain readable; new-mode events cannot hide under old format tags.
- Five new regression/ablation tests; existing public-command snapshot expectation
  updated to85. No native proof kernel or Maru compiler/platform changes.

Full contracts and experiment interpretation: `docs/search85-design.md`.

## Experiment

`python3 adapters/search85_experiment.py` ran90 fresh native processes in a fixed
randomized arm schedule. It compares legacy/indexed/cache/rank/UCB, structurally
varied seeds, matched targets, and attached versus in-memory workflow costs.
Diagnostics and independent held-out proof evaluation are outside timed search/
workflow markers. Data: `docs/search85-experiment.json`.

Mixed workloads: cache versus indexed-only reduced certification calls from
11/8/12 to8/8/11, with the same learned definitions and held-out proof coverage.
Rank/UCB did not establish a separate improvement.

Distractor target-two tasks: legacy needed6/12/13 rounds, indexed modes2/2/2.
In-memory median workflow was0.3553s legacy vs0.3241s cache. Attached median
workflow was0.6369s legacy vs0.6955s cache; attached search/checkpoint work therefore
did not improve overall. Median observed certification calls including replay/
close were2 in memory vs15 attached. Small timing differences are exploratory,
not statistical or universal speed claims. Different raw-pair/candidate budget
units and sampled memory proxies are explicitly disclosed.

Search remains OFF by default. Evidence favors investigating incremental validated
persistence and simpler matching/cache improvements before adding full MCTS.

## Final verification

`compiler.sh reproduce`, `verify 20261023T095209Z-2106`, and `promote` completed.

- 81 Python tests passed in123.812 seconds under the verified candidate.
- Native, store, runtime and graph-store suites passed.
- Sibling0066 graph/Horn differential oracles passed.
- Candidate/next/third LLVM outputs matched.
- Candidate/next/third stripped executable images matched.
- `src/maru` matches v0.0084; no new bootstrap dependency.
- Current `docs/release.tests.sha256` verifies successfully against the source tree.

Evidence: `docs/verification.log`, `docs/python-tests.log`,
`docs/release.sources.sha256`, `docs/release.tests.sha256`, and
`runtime/releases/20261023T095209Z-2106/`.
Native example: `docs/search85-demo.sexp`.

Earlier retained review/release evidence is historical, including the v0.0084
incomplete-release finding. This release's gate and manifests refer to v0.0085.
No registered LLVM MLIR dialect, neural model, broad theorem-search superiority,
constant-time index, equal-memory benchmark or GitHub publication is claimed.
