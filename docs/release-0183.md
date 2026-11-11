# Release 0.0183 — Korean NL → proof → Korean answer (candidate)

- Date: 2026-11-08
- Predecessor: 0.0182. Candidate, not promoted.
- Scope: replace the parent/ancestor toy surface with a controlled Korean
  natural-language front end: sentences become facts/rules, a question becomes a
  goal, the proof kernel answers, and the answer is realized in Korean.
- Analysis: `/research/analysis-nl-deduction-0183.md`.

## Changes

New `src/dlm/nl.l`:

```text
nl-parse       Korean fact / universal rule / question
nl-build       parsed records → facts + rules + source text
nl-run         parse → p-prove → answer + why
nl-why         proof givens/rules → source sentences
nl-word        symbol → Korean word
```

Supported controlled patterns:

```text
"고양이는 포유류이다."          fact
"모든 포유류는 동물이다."       universal rule
"고양이는 생물인가?"            question
```

Both Korean particles `은` and `는` are accepted.

`scripts/run.sh` loads `nl.l` after `graph-ir.l`.

## Experiment

`experiments/nl_repl/` + `scripts/nl.sh`:

```text
PARSED ((nl-fact cat mammal ...)
        (nl-fact dog mammal ...)
        (nl-rule mammal animal ...)
        (nl-rule animal living ...))

Q1 고양이는 생물인가?
STATUS1 proved
ANSWER1 네, 고양이는 생물입니다.
WHY1 고양이는 포유류이다. 모든 동물은 생물이다. 모든 포유류는 동물이다.

STATUS2 unknown
ANSWER2 증명할 수 없습니다: 고양이는 식물입니다.
done-nl
```

The prover derives `cat -> mammal -> animal -> living`; an unprovable query
abstains rather than asserting a false negative.

## Self-host

```text
compiler.sh reproduce
→ 20261109T235727Z-26031
compiler.sh verify 20261109T235727Z-26031
→ Verified
```

## Measured

```text
native normal   54 checks / 0 FAIL
native safety-2 54 checks / 0 FAIL
self-host       verified
```

## Implementation note

The Korean subject particle alternates `은/는`; the parser accepts both. Maru
does not load `list->string` in this minimal core, so a local
`nl-list->string` was added for byte slicing. The explanation traverses the
actual `p-prove` proof tree rather than the closure table.

## Still not

- Controlled language, not open-domain Korean.
- No morphological analyzer; only the three sentence patterns.
- Small fixed lexicon.
- No negation/quantifier scope/tense.
- No web/source ingestion yet.
- The NL layer is untrusted; the proof checker remains the truth gate.
