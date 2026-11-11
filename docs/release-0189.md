# Release 0.0189 — multi-page web observation accumulation (candidate)

- Date: 2026-11-10
- Predecessor: 0.0188. Candidate, not promoted.
- Scope: fetch two cached Simple Wikipedia pages, extract two observations,
  accumulate them in one query-time fact set, and answer two English queries.
- Analysis: `/research/analysis-web-multi-0189.md`.

## Changes

```text
adapters/web_multi.py
  cached Dog + Cat summaries
  lexically constrained object extraction

experiments/web_multi_repl/
scripts/web_multi.sh
```

## Experiment

```text
wrote ... observations=2
  dog->mammal Dogs are mammals ...
  cat->mammal Cats ... are ... mammals ...

OBS 2
DOG proved Yes, a dog is a mammal.
CAT proved Yes, a cat is a mammal.
done-web-multi
```

## Self-host

```text
compiler.sh reproduce
→ 20261110T081810Z-30036
compiler.sh verify 20261110T081810Z-30036
→ Verified
```

## Measured

```text
native normal   58 checks / 0 FAIL
native safety-2 58 checks / 0 FAIL
self-host       verified
```

## Still not

- two pages, one extraction pattern, fixed lexicon
- observations are per-run; no persistence
- no web rule induction
- no contradiction/multi-source resolution
- proof remains the truth gate
