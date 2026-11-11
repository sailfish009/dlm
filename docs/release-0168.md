# Release 0.0168 — counterexample-driven stride-2 revision (candidate)

- Date: 2026-11-08
- Predecessor: 0.0167. Candidate, not promoted.
- Scope: use a negative counterexample to reject the one-step recursive template
  and select a two-base-step (stride-2) seed/step program.
- Analysis: `/research/analysis-synth-revise-0168.md`.

## Motivation

0.0167 synthesized:

```text
ancestor(x,z) :- parent(x,z).
ancestor(x,z) :- parent(x,y), ancestor(y,z).
```

from one long positive. But that program derives every intermediate point. If
the data says `ancestor(a,d)` is false while `ancestor(a,e)` is true, the
one-step program is over-general.

## Changes

`src/dlm/synth.l`:

- `s-seed2-candidates` — seed `R(x,z) :- P(x,y), P(y,z)`
- `s-rec2-candidates` — step `R(x,z) :- P(x,y), P(y,w), R(w,z)`
- `s-stride2-synthesize` — pair search with negative rejection
- `s-revise-synthesize` — keep the one-step program only when it is
  non-conflicting; otherwise try the stride-2 template

`experiments/synth_revise_repl/` + `scripts/synth_revise.sh`.

## Experiment

Training chain: `parent(a,b..e,f)` (5 edges).
Positive: `ancestor(a,e)` (distance 4).
Negative: `ancestor(a,d)` (distance 3).

```text
ONE STEP program conflict=yes
PROGRAM stride2 rules=2 support=(s0)
COVERAGE 1/1
NEGATIVE clean
HELD proof
HELD NEG fail
SEED ONLY HELD fail
FROZEN fail
done-revise
```

The revised program:

```text
ancestor(x,z) :- parent(x,y), parent(y,z).
ancestor(x,z) :- parent(x,y), parent(y,w), ancestor(w,z).
```

It derives the positive even-distance case, does not derive the odd-distance
negative, and transfers to a held chain while still rejecting the held negative.

## Self-host

```text
compiler.sh reproduce
→ 20261109T082552Z-31747
compiler.sh verify 20261109T082552Z-31747
→ Verified
```

## Measured

```text
native normal   28 checks / 0 FAIL
native safety-2 28 checks / 0 FAIL
self-host       verified
```

## Still not

- Revision chooses between two fixed template strides (1 and 2); no general
  guard/constraint invention.
- A single negative is not a complete theory-revision criterion.
- Base predicate and recursive shape are still template-bound.
- Provenance is template fact-ID support, not full derivation evidence.
