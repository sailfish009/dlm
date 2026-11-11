# Release 0.0184 — English NL → proof → English answer (candidate)

- Date: 2026-11-08
- Predecessor: 0.0183 (Korean). Candidate, not promoted.
- Scope: switch the controlled NL front end to English input and English output.
- Analysis: `/research/analysis-nl-deduction-en-0184.md`.

## Changes

`src/dlm/nl.l`:

```text
"A cat is a mammal."          fact
"All mammals are animals."    universal rule
"Is a cat a living thing?"    question
```

- ASCII lowercasing
- noun plural normalization (`mammals → mammal`, `living things → living thing`)
- English answer realization
- proof-tree source explanation retained

## Experiment

```text
PARSED ((nl-fact cat mammal A cat is a mammal.)
        (nl-fact dog mammal A dog is a mammal.)
        (nl-rule mammal animal All mammals are animals.)
        (nl-rule animal living-thing All animals are living things.))

STATUS1 proved
ANSWER1 Yes, a cat is a living thing.
WHY1 A cat is a mammal. All animals are living things. All mammals are animals.

STATUS2 unknown
ANSWER2 I cannot prove that a cat is a plant.
done-nl
```

## Self-host

```text
compiler.sh reproduce
→ 20261110T000612Z-8955
compiler.sh verify 20261110T000612Z-8955
→ Verified
```

## Measured

```text
native normal   54 checks / 0 FAIL
native safety-2 54 checks / 0 FAIL
self-host       verified
```

## Implementation note

English plurals in universal sentences are normalized before lexicon lookup;
otherwise `mammals`/`animals` do not match `mammal`/`animal`. A local
`nl-list->string` remains because the minimal core does not load the conversion
module's `list->string`.

## Still not

- Controlled English only; no general parser.
- Small fixed lexicon.
- No negation, quantifier scope, tense, or morphology beyond `-s`.
- No web/source ingestion.
- NL is untrusted; proof checker remains the truth gate.
