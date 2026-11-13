# M4 — decomposition generation-first

This is the separate M4 track.  It does **not** train a ranker.  It fixes
candidate generation first, because Stage 0 showed:

```text
SPAN-COVERAGE 0/22
CANDIDATE-RECALL 0/22
ORACLE-SPAN-PRED 22/22
```

## Bug fixed

`decomposition_stage0` used `nl-split` once per sentence:

```lisp
(define-function words (s) (nl-split (nl-normalize s) " "))
```

Maru's `nl-split` returns only two pieces, so almost every sentence produced
at most two words.  M4 makes `words` recursive.

## Result

```text
WEB 15 SPANS 894 PREDS-FULL 11 PREDS-WEB 1
GOLD 22 CANDIDATE-SPACE-FULL 8791596
PRED-COVERAGE-FULL 22/22 PRED-COVERAGE-WEB 6/22
SPAN-COVERAGE 11/22
CANDIDATE-RECALL-FULL 11/22 CANDIDATE-RECALL-WEB 5/22
ORACLE-SPAN-PRED 22/22 (upper bound)
```

This is a generation-first result: recall is now non-zero, so a future ranker
has candidates to rank.  Predicate extraction is still weak (6/22), and the
full candidate space is 8.8M; indexed retrieval is required before training.

## Run

```bash
cd /research/dlm_v0.0238/experiments/decomposition_stage1
./run_all.sh
./verify.sh
```

Gate: `V0238-M4-GENERATION-PASS`.

## Limits

- Span coverage 11/22, not 22/22.
- Candidate recall is 11/22 full and 5/22 web-predicate.
- No ranker is trained in M4.
- Full candidate space is large; generation must become indexed.
