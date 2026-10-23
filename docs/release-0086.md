# DLM 0.0086 — integrated generated-program recursive learning

Promoted release: `20261023T104654Z-20404`.
Prior directories including `/research/dlm_v0.0085` are preserved.

## Delivered

- Native candidate generation -> real space79 choose branches -> native checker
  -> branch-outcome supervision -> independent admission recheck -> next-round
  recursive definition generation, through `(dlm 'step/start)`.
- New `nd-cache` and `nd-ucb` modes; no LLM, neural policy or external Screamer.
- Data-only `certify86` instruction with branch-local tickets; bare/provisional
  accepts cannot authorize admission. Unknown verification stays retryable.
- Compact replay-reconstructed branch trace in the controller and explicit
  session86 tagging. Old77/83/84/85 stores remain readable.
- One native experiment shell: `scripts/recursive-selfssl.sh`, interactive by
  default, or finite `--rounds N` with checked durable close.
- Explicit demo observations only when requested and no source episodes remain;
  existing observations preserved. Relative store paths preserve caller context.
- CLI bounds, corrupted-store refusal, one-process original-reader idle learning,
  exact fresh-process state/next-step resume and gate safety are tested.

Primary commands:

```
./scripts/recursive-selfssl.sh --demo /tmp/recursive86.sexp
./scripts/recursive-selfssl.sh --demo --rounds 4 --budget 4 /tmp/recursive86.sexp
./scripts/recursive-selfssl.sh --rounds 1 /tmp/recursive86.sexp
```

Contracts/limitations: `docs/recursive86-design.md`.

## Evidence

The explicit native chain example learned paths2 ->3 ->4, referencing earlier
learned operators. It executed branch batches1/3/3, collected7 checked labels and
performed10 native certification calls including3 final rechecks. The fourth
round saturated; restart waited without inventing new learning events.

- `docs/recursive86-demo.sexp`: native step/trace/query output.
- `docs/recursive86-shell.log`: finite shell experiment and reopen.
- `docs/recursive86-experiment.json`:36 fresh native comparison runs.

The36-run comparison preserved the same learned definition counts and cold-probe
coverage but increased checks and latency. Mixed-memory median search time was
0.3204s direct UCB versus0.4166/0.4652s nd-cache/nd-ucb. Attached target-two median
workflow was0.7229s direct versus1.2348/1.2608s nd modes. Batch checking and final
rechecks provide extra self-supervision at real cost. No speedup claim is made.

## Final verification

`compiler.sh reproduce`, `verify 20261023T104654Z-20404`, and `promote` completed.

- 89 Python tests passed in124.199 seconds under the verified candidate.
- Native, store, runtime and graph-store suites passed.
- Sibling0066 Horn/graph differential checks passed.
- Candidate/next/third LLVM outputs and stripped binary images matched.
- `src/maru` matches v0.0085; no new compiler/bootstrap dependency.
- Current `docs/release.tests.sha256` verifies against the source tree.
- Bash syntax checks passed for launcher/run scripts.

Evidence/manifests: `docs/verification.log`, `docs/python-tests.log`,
`docs/release.sources.sha256`, `docs/release.tests.sha256`, and the runtime release
directory. Eight new tests are in `tests/test_recursive86.py`; the current public
snapshot expectation is86 while legacy codecs remain tested.

## Explicit limits

The generator is a bounded binary-relation composition grammar. It does not yet
perform arbitrary program synthesis, human-question interpretation, web-axiom
extraction or unrestricted answer generation. New launcher selects experimental
nd mode; ordinary defaults are not globally promoted. There is no physical
parallelism, full MCTS, registered LLVM MLIR dialect, hard event-time guarantee,
unlimited curriculum or GitHub publication. Retained older docs are historical.
