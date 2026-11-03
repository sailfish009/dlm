# Release 0.0092 — Maru declarative deductive control

## Delivered

New directory `/research/dlm_v0.0092`, copied from0091. The source predecessor is
unchanged, including its already-dirty/untracked Git state. Its232 recorded
product-file hashes are preserved. Of inherited product paths, only `.gitignore`,
`README.md`, `VERSION`, and `scripts/run.sh` differ in0092. The new root README
preserves the previous one as `README-0091.md`.

Five new native modules implement typed focus/restore/global/widen commands,
goal/binding-dependent primitive/basis selection, exact original source handles,
dependency closure, actual scoped interpretation, provisional workspaces,
independent coverage and complete-row admission, and replay-admitted persistence.
The original Basis91 implementation is unchanged. No GPU, neural service,
network access, third-party attention package, or compiler change is needed.

Compiler SHA256 remains:

```text
2cbe804829509f5386933d832cbba2fef1bad367b7510a543b5d3f5818136fc9
```

## What is demonstrated

- A fixed learned core can select different actual query plans for different
  data distributions and goals; verified bindings influence subsequent choices.
- Balanced chain data selects B2, which actually dispatches B1. Selective-tail
  data selects t→s→r with original fact scopes7→4→0 in the unshuffled demo.
- On the latter, worker reads64→3 versus the **same new backend's** fixed order;
  checker units78→70, while actions5→13. Index/checker reads are not included in
  worker reads. This is not64/3 total-runtime or total-access improvement.
- Incomplete focus produces pending/need-widen, not a global negative. Full-view
  retry recovers correct answers. A poisoned index cannot conceal missing
  premises from the independent source gate.
- Wrong/omitted rows, unknown/conflicting variable entries, stale handles, false
  role rewrites, altered work/history, and failed checkpoints do not publish
  completed false results.
- Pause/resume reproduces next action, results and final state in a fresh process.
  Exclusive writer locks, failed-close retention and successful release work.

The native policy is a fixed marginal-count heuristic. It is **not trained**.
The core is frozen during query control; this release does not feed query traces
back into formation, discover new world laws, prove latent axiom geometry, or
supply a new general learning theory. A logical goal is supplied as the question;
no desired answer or basis body is supplied to the selector.

## Final verification

| Check | Result |
|---|---|
| Python offline regression | 186 passed,588.770s; includes26 new tests |
| Legacy local-HTTP tests | Six excluded, not silently counted as passing |
| New independent finite oracle | 256 graphs ×8 patterns ×4 policies =8,192 full answer/witness checks; zero mismatches |
| Large workspace | 343 answer rows, all four policies, original witnesses preserved |
| Malformed input | 500 seeded trees, command/shape/snapshot boundaries, no observed native crash |
| Native test driver | Passed |
| Legacy store, embedded runtime, graph-store | Passed |
| Model/archive separation | New core inference works without current learner, training rows or audit |
| Source version/retraction | Fresh current-model contexts reject old handles; no stale worker tables |
| Persistence | Forgery, failure, external file change, fresh process and two-process lock tests passed |
| Source compatibility | Predecessor hashes/Git state and compiler preserved |

`attention-tests.log` is an explicitly labeled extraction of the26 new cases
from the final full offline run, **not a separate test invocation**. Python socket
guards are not an OS sandbox. Independent finite tests do not constitute a
formal general completeness proof.

## Measured negative result

210 sequential fresh native runs: five fixed workloads, three shuffle/rename
seeds, seven arms, two repeats. Two batches run per child; the final batch's
3,360 complete question/witness results were independently checked, with zero
mismatches. Repetitions are not additional independent oracle cases.

Median whole-process wall seconds:

| Workload | memo | ordered92 | indexed92 | adaptive92 |
|---|---:|---:|---:|---:|
| chain | 0.9537 | 1.3978 | 1.3853 | 1.3673 |
| selective-tail | 0.9712 | 1.5014 | 1.4903 | 1.5278 |
| fork | 0.7656 | 1.2056 | 1.2046 | 1.2190 |
| ambiguous | 2.0295 | 2.5775 | 2.5664 | 2.6564 |
| no-repeat | 0.7444 | 1.1200 | 1.1023 | 1.1223 |

The adaptive path loses to memo on all five whole-process workload medians.
Even versus the same new backend, its hand-designed heuristic is not uniformly
better. Fixed indexed control is a necessary control, not a renamed innovation.

Raw/memo/basis controls share complete source-local tables within a batch; memo
also shares structural plan results. All arms retain the same learned core and
pay the same formation. New policies have fresh per-query indexes/workspaces
and an additional independent full-source local replay. Timings include startup,
formation, index/control/checking, repeated questions and output, but not attached
checkpoint/replay. No isolated steady-state or broad speedup claim is made.

Core bytes are identical across arms. Adaptive peak serialized per-query control
profile medians are1,639–2,345 bytes, separate from model/evidence/audit. These
are not heap estimates. Child RSS, CPU and all other arms are in the JSON.
Metrics91/92 are not directly comparable units.

## Limits and unchanged defects

- Positive connected conjunctive binary grammar and inherited8-fact/8-node caps;
  no unrestricted FOL, negation, hidden existential projection or new empirical laws.
- Depth4,64 accepted transitions,512 rows, logical fuel≤200000. Allocation,
  metadata walks, validation and serialization are not fully fuel-metered.
- `local92` admits prepared work; it is not an arbitrary local theorem language.
- Models are explicit frozen contexts. Retained historical models still infer
  historical answers; callers must start from a new current model after changes.
- Full-source reference checking is intentionally expensive; there is no partial
  result cache and no attention-policy learning or persistent library retirement.
- Replay is synchronous; attached per-step replay can repeat prefix work. Advisory
  locks and atomic rename do not provide an fsync power-loss guarantee.
- Native web raw/hash/span integrity and truncated-HTTP handling remain unresolved
  inherited issues. Free-text acquisition is not automatically trusted logic.
- This is not a reproduction of the referenced neural paper or upstream vLLM path.

## Reproduction and evidence

```sh
./scripts/run.sh attention92
./scripts/run.sh attention92-input < experiments/attention92/input-example.sexp
./scripts/run.sh proof experiments/attention92/interventions.l
python3 -B -m unittest discover -s tests -p 'test_attention92.py' -v
python3 -B tests/run_offline.py
./scripts/run.sh test
bash tests/store-tests.sh
bash tests/runtime-tests.sh
bash tests/graph-store-tests.sh
python3 -B adapters/attention92_experiment.py --output /tmp/attention92.json
sha256sum -c docs/attention92-evidence/source.sha256
sha256sum -c docs/attention92-evidence/SHA256SUMS
```

- [Design/contracts](attention92-design.md)
- [Measurement JSON](attention92-experiment.json)
- [Demo trace](attention92-demo.sexp)
- [Compact interventions](attention92-interventions.sexp)
- [Input demo](attention92-input-demo.sexp)
- [Offline log](attention92-evidence/offline-tests.log)
- [New-case extraction](attention92-evidence/attention-tests.log)
- [Native log](attention92-evidence/native-tests.log)
- [Store/runtime log](attention92-evidence/store-runtime-tests.log)
- [Environment](attention92-evidence/environment.json)
- [Predecessor hashes/status](attention92-evidence/predecessor.json)
- [Preservation check](attention92-evidence/preservation.json)
- [Final link/whitespace checks](attention92-evidence/final-checks.json)
