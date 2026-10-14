# DLM v0.0038 stream experiment — does Experience accumulate?

Tests the *learning structure* itself: entities are split into disjoint **train**
and **test** sets (open universe). A law is induced only on train entities, and
after **every** admitted clause the whole Experience is scored on the unseen test
entities.

## Run

```bash
./experiments/stream/stream.sh              # synthetic, seeds 1 2 3
SEEDS="1 2 3 4 5" ./experiments/stream/stream.sh
WEB=1 DOCS=120 ./experiments/stream/stream.sh   # real web facts
```

Reports: `experiments/stream/reports/stream_seed*.json`.

## Domain (synthetic, known laws)

* transitive: `subclass_of`, `part_of`, `located_in`
* inverse: `country_of(X,Y) :- country(Y,X)`
* `Ground` is **empty** — every clause must be learned.

## The falsifiable criterion

A working learning structure must, on unseen entities:

1. add a **new** clause each round (`multi_round`),
2. **strictly increase** held-out recovery (`strictly_increases`),
3. keep `false == 0` every round (`sound_every_round`),
4. recover **all** laws (`all_laws_found`).

## Result (synthetic, 3 seeds)

| seed | identity | round1 | round2 | round3 | round4 | false_max | verdict |
|---|---|---|---|---|---|---|---|
| 1 | 0.231 | 0.252 | 0.479 | 0.756 | **1.000** | 0 | OK |
| 2 | 0.249 | 0.272 | 0.535 | 0.747 | **1.000** | 0 | OK |
| 3 | 0.249 | 0.272 | 0.281 | 0.548 | 0.788 | **9** | FAIL |

* **Accumulation is real**: seeds 1–2 recover all four laws round by round; each
  clause lifts held-out recovery on entities the induction never saw.
* **But the soundness gate is only empirical.** Seed 3 admits
  `located_in(X,Y) :- country(Y,E0), subclass_of(X,Y)` — sound on the sampled
  *train* negatives, false on unseen test entities (9 false assertions). In an
  open universe a finite negative sample cannot prove universal soundness.

## Files

* `run.py` — domain + per-round held-out curve + verdict.
* `stream.sh` — one-shot multi-seed runner with summary.
* `tests/test_stream.py` — network-free regression (small config).