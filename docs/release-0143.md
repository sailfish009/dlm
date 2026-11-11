# Release 0.0143 — deep evidence through derived answers (candidate)

- Date: 2026-11-08
- Predecessor: 0.0142. Candidate, not promoted.
- Scope: fix 0.0137's any-witness grounding bug and trace a rule-derived fact
  through its proof DAG to all given-leaf web evidence.
- Analysis: `/research/analysis-evidence-rule-0143.md`.

## Changes

`src/dlm/d107-ground.l`:

- `p107-fact-evidence-deep` recursively follows a derived fact's proof term:
  ```text
  derived fact dN
    -> proof children
    -> given facts
    -> claim/source/span/quote
  ```
- `p107-proof-evidence-deep` builds witness entries from the closure table.
- `p107-answer-evidenced` now uses the closure table and deep evidence.
- Missing or unevidenced leaves become `(missing-evidence107 FID)`.
- `p107-answer-grounded?` requires **every witness** to have a complete evidence
  chain; a partially evidenced proof is false.
- Old direct `p107-fact-evidence` remains available for compatibility.

## Experiment

`experiments/evidence_rule/`:

```text
web claims: parent/ancestor training + parent(j,k), parent(k,l)
learned rule: ancestor(x,z) :- parent(x,y), ancestor(y,z)
query: ancestor(j,l)
```

| arm | answer rows | grounded | evidence items | missing |
|---|---:|---:|---:|---:|
| deep | 1 | true | 2 | 0 |
| partial | 1 | false | 1 | 1 |
| no-ground | 1 | false | 0 | 2 |
| mixed p/web + q/local | 1 | false | 1 | 1 |
| direct web p | 1 | true | 1 | 0 |
| frozen | 0 | false | 0 | 0 |

`deep` resolves the derived `ancestor(j,l)` to the two web claims:
`parent(j,k)` and `parent(k,l)`.

## Measured

```text
native normal   346 ok / 0 FAIL
native safety-2 346 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Synthetic ground fixture; not the Wikipedia ground-web corpus.
- Evidence is flattened to given leaves; no per-proof-step explanation beyond
  the leaf set.
- No proof-DAG credit or versioned rule/evidence basis.
- No all-witness check for non-ground scopes beyond missing leaves.
- 0.0142's calibrated schema selection is independent of this fix.
