# DLM v0.0039 online experiment — the streaming trajectory

Referents arrive one batch at a time (an *online* open universe). Each round the
arm **refits on the cumulative revealed set** — and for `abstract` folds recurring
subgoals — then the theory is scored on **unseen test entities**. One rich JSONL
row per round is logged, then read back as a multi-aspect learning report.

```bash
./experiments/online/online.sh                 # 4 arms x 3 seeds x 5 rounds (bigger data)
./experiments/online/online.sh --big           # more data (slower)
./experiments/online/online.sh --quick         # tiny smoke test
./experiments/online/online.sh --arms plain,frozen --seeds 0,1,2
./experiments/online/online.sh --analyze reports/online/<stamp>   # re-read logs
```

## Arms

| arm | what it does |
|---|---|
| `frozen` | no learning (identity baseline) |
| `plain` | `learn` each round, raw theory |
| `abstract` | `learn` then `abstract_theory` each round |
| `random` | control: learn from random (non-truth) positives |

## Data scale

Default `n_train=24`, `n_test=18`, `chains=3`, `chain_len=6` over three transitive
relations + an inverse, `rounds=5`, `max_rules=6` (≈60 revealed facts and ≈4k
sampled negatives by the last round). `--big` = 30/22/4/7, 8 rounds, 8 rules.

## Log record (per round)

`arm, seed, round, revealed_facts, revealed_entities, revealed_pairs, negatives,
clauses, new_clauses, dl, dl_delta, invented, heads, train_recovery, train_false,
generalization_gap, held_recovery, held_gain, held_new, false_assert,
avg_body_len, retention, churn, rules_admitted, intra_curve, max_depth,
mean_depth, proof_nodes, depth_sampled, learn_seconds`.

`intra_curve` is the held-out recovery after each rule admitted *within* the round.
`learn_seconds` is the only non-deterministic field (wall clock); everything else is
exact per `(arm, seed)`.

## Report sections (`--analyze`)

`[coverage]` held-out by round · `[soundness]` false asserts by round ·
`[generalisation]` train fit vs unseen + clause/DL growth · `[dynamics]`
per-round held-out gain, proof depth, cost · `[intra-round]` held-out after each
admitted rule · `[verdict]`.

## Measured (default, 3 seeds)

| arm | r1 | r2 | r3 | r4 | r5 | final false |
|---|---|---|---|---|---|---|
| plain/abstract | 0.508 | 0.508 | 0.749 | 0.960 | **1.000** | 0 |
| frozen/random | 0.247 | 0.247 | 0.247 | 0.247 | 0.247 | 0 |

The transient is the story: at round 4 the refit over-generalises (false asserts
23 / 68 / 0 across seeds), then round 5's added negatives reject the unsound clause.
`abstract` tracks `plain` exactly (`invented=0`) — the recurring subgoals in
`experiments/abstract` are built, not induced here.

## Do not read this as convergence

This "recovery" is a **same-distribution effect, not soundness**. The learner is
memoryless (each round refits from scratch) and only the growing *in-distribution*
negative sample changes; online train/test share one generator, so a counterexample
in the revealed population predicts one in the unseen one. When the counterexample
lies *outside* the revealed distribution the same gate never recovers —
`experiments/stream` seed 3 admits `located_in(X,Y) :- country(Y,E0),
subclass_of(X,Y)` with `false = [0,1,9,9]` (grows and persists). The `false` curve
is a gate-reliability monitor, not evidence that the system becomes sound.