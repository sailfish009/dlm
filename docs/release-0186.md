# Release 0.0186 — NL boundary feeds basis axioms (candidate)

- Date: 2026-11-08
- Predecessor: 0.0185. Candidate, not promoted.
- Scope: stop `nl-run` from handing ad-hoc rules directly to the prover. NL now
  produces observations; universal sentences become basis axioms; proof consumes
  `b-active-rules`.
- Analysis: `/research/analysis-nl-basis-0186.md`.

## Changes

`src/dlm/nl.l`:

```text
nl-basis   parsed universal rules → basis axioms (evidence = source text)
nl-run     facts + nl-basis → b-active-rules → p-prove
```

The NL layer remains the I/O boundary, but the rule path now goes through the
core basis store.

`experiments/nl_repl/start.l` prints:

```text
BASIS RULES 2
```

## Experiment

```text
PARSED (... 4 records)
BASIS RULES 2
STATUS1 proved
ANSWER1 Yes, a cat is a living thing.
WHY1 A cat is a mammal. All mammals are animals. All animals are living things.
STATUS2 unknown
ANSWER2 I cannot prove that a cat is a plant.
done-nl
```

## Self-host

```text
compiler.sh reproduce
→ 20261110T012133Z-2489
compiler.sh verify 20261110T012133Z-2489
→ Verified
```

## Measured

```text
native normal   55 checks / 0 FAIL
native safety-2 55 checks / 0 FAIL
self-host       verified
```

## Still not

- `nl-basis` is built per query; no global persistence across sessions.
- Facts are still a per-call observation list, not a persistent knowledge store.
- NL universal sentences are parsed, not induced.
- No observation/fragment decomposition yet.
- Truth remains with the proof checker.
