# Release 0.0133 — self-evaluation, web corpus, and recursive experiment

- Date: 2026-11-08
- Predecessor: 0.0132. Candidate, not promoted.
- Scope: read-only self/curriculum signals and a controlled web->claim->basis
  experiment. No live network, no LLM, no learned world axioms.

## Added

- `src/dlm/d107-self.l`: predicate/fact ability profile, weak predicates,
  unresolved goal gaps, next goal, self report. Read-only.
- `adapters/web_cache.py`: cached JSON claims -> `p107-claim` forms (untrusted).
- `experiments/recursive_web/run.py`: controlled rounds over cached sources.

## Experiment

Sources A/B, C/D, E/F; two sources corroborate one observation record. The DLM
kernel receives only corroborated observations. Definitions are learned from
train records; held records are added after learning and queried with the
learned basis.

Final web arm:

```text
round  sources          train_obs defs train_plan held_obs held_plan held_rows held_calls
4      A+B+C+D          2         2    2          0        2         0         1
6      A+B+C+D+E+F      2         2    2          1        2         6         1
```

Controls:

| arm | train_obs | defs | train_plan_steps | held_obs | held_plan_steps | held_rows | held_calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| web | 2 | 2 | 2 | 1 | 2 | 6 | 1 |
| no-web | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| single-source | 0 | 0 | 3 | 0 | 3 | 0 | 0 |
| scrambled | 1 | 0 | 3 | 0 | 3 | 0 | 0 |
| frozen (no learn) | 2 | 0 | 3 | 1 | 3 | 6 | 0 |

Interpretation:

- corroboration is required before any observation reaches the kernel;
- the learned b1/b2 basis reduces the train/held plan from 3 to 2 steps;
- frozen data still answers the held query but without learned basis/calls;
- single-source and scrambled sources produce no basis and no held data;
- observations and basis are not mutated by the web layer.

The held rows count 6 reflects permutations of three calls with distinct
arguments; it is not a world-truth or generalization claim.

## Limits

- **Offline cached corpus**, not live web.
- Web claims are hypotheses until corroborated; even observed claims are
  observations, not axioms.
- Only conservative definitions are learned; no empirical world-law induction.
- Conflict is limited to explicitly declared functional predicates.
- The rounds are corpus-driven, not autonomous goal generation/self-curriculum;
  self report is read-only.
- No LLM/NL grounding; the adapter is a cached structured-claim tool.
- Sized for a controlled experiment, not scale.
