# Release 0.0157 — fresh minimal CPU-only deductive REPL (candidate)

- Date: 2026-11-08
- Predecessor: 0.0156. Candidate, not promoted.
- Scope: fresh minimal implementation in the Maru REPL, independent of the
  d107-* source structure.
- Analysis: `/research/analysis-minimal-deduce-0157.md`.

## New minimal source

Only four new modules:

```text
src/dlm/logic.l    terms, atoms, facts, rules, unification
src/dlm/infer.l    exhaustive positive Datalog closure
src/dlm/deduce.l   fixed-data / fixed-axiom coverage and selection
src/dlm/repl.l     REPL helpers
```

No `d107-*` file is loaded by `scripts/run.sh`. Existing 0.0156 code remains
available as reference only.

## REPL experiment

`experiments/minimal_repl/start.l`, launched by `scripts/experiment.sh` through
`run.sh experiment` in the original Maru REPL:

- 4 fixed tasks
- 6 fixed axioms
- fixed positive/negative atoms
- active axiom subset carried across tasks

| arm | tasks covered | active axioms | conflict |
|---|---:|---:|---:|
| deductive selection | 4/4 | 4 (A,B,C,D) | 0 |
| frozen | 0/4 | 0 | 0 |
| all axioms | 4/4 | 6 | 0 |

Selection picks exactly one matching axiom per task shape.

## Measured

```text
native normal   3 checks / 0 FAIL
native safety-2 3 checks / 0 FAIL
```

There is no Python test or contract oracle in this fresh minimal core; those
belong to the older d107 reference tree.

## Still not

- Fixed tasks and axiom library; no rule invention.
- Greedy selection; no global minimality/independence proof.
- No schema alignment.
- No proof-DAG credit or theory revision.
- Sequential REPL experiment, not a resident idle loop.
