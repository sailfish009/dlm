# experiments/train — the training foundation

This directory is the seed of the long-run harness. It holds the bricks that
make DLM training *training-like* (many rounds, checkpointable) rather than a
one-shot smoke test, plus the accumulating learner that is the point of the loop.

## What lives here

| file | what it is |
| --- | --- |
| `accumulate.py` | streaming run: **accumulating learner vs memoryless refit**, with two guaranteed probes (retraction fires; checkpoint/resume round-trips). |
| `bench_closure.py` | micro-benchmark of the kernel closure (semi-naive vs naive). |
| `train.sh` | runs `accumulate.py` over seeds into `reports/train/<stamp>/`. |

## The accumulating learner (`dlm/accumulate.py`)

`ground.learn` always starts from a fresh `Experience`: it is a **refit** over
what has been revealed, not an accumulation, and it cannot express "this rule
used to hold". The `Learner` keeps what it learned and, each round:

1. **merges** new facts / positives / negatives (set union);
2. **retracts** any rule that the *full revealed negative complement* now
   falsifies — a greedy, insertion-ordered sound subset, so the newest rule is
   the first suspect;
3. **induces** rules for still-uncovered positives, skipping any candidate that
   is structurally equal (up to variable renaming) to a rule already held;
4. **compresses** (optional) recurring bodies with `abstract.abstract_theory`,
   accepting only a strict description-length drop the kernel certifies;
5. records `false_final` = closure ∩ negatives over the full complement, never a
   sample.

It round-trips through `dlm/theory.py` (`to_theory` / `from_theory`), so a run
can stop and resume.

## Run it

```bash
./experiments/train/train.sh                     # seeds 1 2 3 (default)
SEEDS="1 2 3 4 5" ROUNDS=6 ./experiments/train/train.sh
NO_COMPRESS=1 ./experiments/train/train.sh       # ablation
```

Output: `reports/train/<stamp>/acc_seed<k>.json` plus a printed summary.

## What the default run shows (honest)

On the controlled multi-relation domain (train/test entities disjoint), with
negatives revealed progressively:

* accumulation **retracts** the over-general rules it admitted early (e.g. a
  symmetry rule `located_in(X,Y) :- located_in(Y,X)` and cross-predicate rules
  such as `subclass_of(X,Y) :- part_of(X,Y)`), and converges to the true laws;
* a memoryless refit records **zero** retractions (it has no memory to retract);
* both end sound (`false_final == 0`) and reach full held-out recovery;
* no duplicate rules across rounds.

The lesson is not "accumulation wins the score" — they converge — it is that
accumulation gives you **retraction and resume**, which is what a long run needs
and a refit cannot represent.

## Determinism

Everything except the `seconds` field is deterministic. Tests strip that field
before comparing (same convention as `experiments/online`).