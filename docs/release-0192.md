# Release 0.0192 — web subclass facts + teacher label → inverse deduction (candidate)

- Date: 2026-11-10
- Predecessor: 0.0191. Candidate, not promoted.
- Scope: extract web subclass facts and one teacher positive label, induce a
  recursive isa rule, store it as a basis axiom, and answer a held-out English
  query through the NL boundary.
- Analysis: `/research/analysis-web-inverse-0192.md`.

## Changes

```text
nl-parse:
  "A dog is a kind of mammal." → nl-subclass
  "A dog is a living thing."   → nl-fact
nl-build:
  nl-subclass → subclass facts
nl-article:
  a/an realization for English answers
web-to-records:
  kind-of quotes parsed as subclass observations
```

## Experiment

```text
OBS 5 FACTS 5 RULES 2
Q1 proved Yes, a cat is a living thing.
Q2 unknown I cannot prove that a living thing is a cat.
done-web-inverse
```

Held-out query: cat was not in the teacher positive; the induced transitive
rule plus cat→mammal proves cat→living-thing. Reverse is rejected.

## Self-host

```text
compiler.sh reproduce
→ 20261110T092218Z-1730
compiler.sh verify 20261110T092218Z-1730
→ Verified
```

## Measured

```text
native normal   61 checks / 0 FAIL
native safety-2 61 checks / 0 FAIL
self-host       verified
```

## Still not

- local/controlled web fixture, not open web
- one teacher label; no behavior sampling
- observations/basis in-process only
- no web rule induction beyond the current template
