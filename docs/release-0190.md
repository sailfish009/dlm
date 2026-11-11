# Release 0.0190 — web universal rule → basis → English answer (candidate)

- Date: 2026-11-10
- Predecessor: 0.0189. Candidate, not promoted.
- Scope: fetch a tiny local web fixture containing a fact and universal rules;
  universal sentences become basis axioms; an English query is proved and
  answered.
- Analysis: `/research/analysis-web-rule-0190.md`.

## Changes

```text
adapters/web_rule.py
  local HTTP fixture → fetch → observations

src/dlm/web.l
  w-to-records recognizes "All ..." as nl-rule via nl-normalize
```

## Experiment

```text
wrote ... observations=3
  A dog is a mammal.
  All mammals are animals.
  All animals are living things.

OBS 3
BASIS 2 rules
Q1 proved Yes, a dog is a living thing.
Q2 unknown I cannot prove that a living thing is a dog.
SOURCE http://127.0.0.1:.../index.html
done-web-rule
```

## Self-host

```text
compiler.sh reproduce
→ 20261110T083153Z-15315
compiler.sh verify 20261110T083153Z-15315
→ Verified
```

## Measured

```text
native normal   59 checks / 0 FAIL
native safety-2 59 checks / 0 FAIL
self-host       verified
```

## Still not

- web fixture is local/controlled, not open web
- one extraction pattern per fact/rule
- observations are per-run; no persistence
- no web rule induction from examples
- proof remains the truth gate
