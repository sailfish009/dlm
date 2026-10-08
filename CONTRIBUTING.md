# Contributing

## Principles

1. **Honest claims.** Follow `/research/GUIDELINES.md`: declare claim tiers, use matched
   controls, and never call a constraint an advantage.
2. **One core variable per experiment.** Arms must differ only in the stated variable.
3. **Ties are ties.** Do not pick the best of a sweep and report it as the result.

## Layout

- `dlm/schema.py`, `interpreter.py`, `decision.py`, `adapter.py` — the v0.0002 wire path.
- `dlm/` also holds the v0.0001 engine (`terms`, `rules`, `kb`, `deduce`, `generalize`,
  `retrieval`, `decider`, `pipeline`).
- `tests/` — pytest. Run from the repository root: `python -m pytest tests -q`.
- `examples/` — runnable demos with a `sys.path` bootstrap.
- `run_eval.py` — matched-arm evaluation; writes `artifacts/eval.json`.

## Before a release

Run `python -m pytest tests -q`, both examples, and `python run_eval.py`. Then
`python tools/build_upload.py` to build the web-upload bundle.