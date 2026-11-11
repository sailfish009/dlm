# Release 0.0158 — fragment decomposition and recombination (candidate)

- Date: 2026-11-08
- Predecessor: 0.0157. Candidate, not promoted.
- Scope: decompose axiom shapes into reusable fragments, combine them into
  templates/programs, and match the assembled programs to fixed tasks in the
  Maru REPL.
- Analysis: `/research/analysis-fragment-repl-0158.md`.

## New files

```text
src/dlm/fragment.l   fragment head/body pieces
src/dlm/assemble.l   fragment combination, templates, programs, instantiation
src/dlm/match.l      fixed task + alignment + program selection
```

The minimal `logic.l / infer.l / deduce.l / repl.l` core remains.

## Fragments

```text
seed     R(x,z) :- P(x,z)
left     P(x,y)
right    R(y,z)
q        Q(y,z)
reverse  P(z,x)
```

5 fragments combine into:

```text
seed template
recursive template  (left + right)
composition template (left + q)
reverse template
```

and 4 programs. The recursive program contains the seed + recursive rule.

## REPL experiment

`experiments/fragment_repl/start.l` via `./scripts/experiment.sh`:

- 4 fixed tasks
- 5 fragments → 4 templates → 4 programs
- active programs carried across tasks
- frozen and all-program controls

| arm | tasks covered | active programs | conflicts |
|---|---:|---:|---:|
| fragment assembly | **4/4** | **2 (p-rec, p-comp)** | 0 |
| frozen | 0/4 | 0 | 0 |
| all programs | 4/4 | 4 | 0 |

`p-rec` is reused for ancestor, reaches and inside; `p-comp` handles path.
This is fewer active units than 0.0157's one-axiom-per-task selection.

## Measured

```text
native normal   5 checks / 0 FAIL
native safety-2 5 checks / 0 FAIL
```

No Python test/oracle in this minimal tree.

## Still not

- Fragment combination is explicit minimal pairing, not a general search over all
  fragments.
- No provenance/qualifier/negation fields on fragments yet.
- No automatic extraction from web text.
- No evidence completeness check.
- Fixed tasks/alignments; greedy selection.
- No proof-DAG credit or full theory revision.
