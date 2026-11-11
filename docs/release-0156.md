# Release 0.0156 — fresh CPU-only deductive matching in the Maru REPL (candidate)

- Date: 2026-11-08
- Predecessor: 0.0155. Candidate, not promoted.
- Scope: fresh implementation of fixed-data/fixed-axiom deductive matching and
  selection, driven from the Maru REPL.
- Analysis: `/research/analysis-deduce-repl-0156.md`.

## Fresh implementation

New `src/dlm/d107-deduce.l` (not an extension of the inductive learner):

```text
task107 NAME FACTS POS NEG
dax107 ID RULES
```

- `p107-deduce-eval` applies an active rule set to fixed task facts and returns
  `(covered total conflict)`.
- `p107-deduce-select` grows an active axiom subset: it adds a candidate only
  when coverage increases and conflict remains zero.
- `p107-deduce-run` carries the active subset across tasks.

The module does not induce rules. It matches a fixed axiom library to fixed
data by deductive closure.

## REPL experiment

`experiments/deduce_repl/start.l` is launched by `scripts/deduce.sh` through
`run.sh deduce` in the original Maru REPL.

Four fixed tasks and six fixed axioms:
- A recursive ancestor
- B recursive reaches
- C composition path
- D recursive inside
- E wrong reverse reaches
- F irrelevant foo

| arm | tasks covered | active axioms | conflicts |
|---|---:|---:|---:|
| deductive selection | 4/4 | 4 (A,B,C,D) | 0 |
| frozen | 0/4 | 0 | 0 |
| all axioms | 4/4 | 6 | 0 |

Selection adds exactly one matching axiom per task shape and does not select the
wrong/irrelevant axioms.

## Measured

```text
native normal   379 ok / 0 FAIL
native safety-2 379 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

## Still not

- Fixed task set and fixed axiom library; no new rule invention.
- Greedy selection only; no global minimality/independence proof.
- No schema alignment; predicate names are already aligned.
- Fixed positive/negative task labels.
- The REPL experiment is a sequential curriculum, not a resident idle loop.
- No proof-DAG credit or theory revision yet.
