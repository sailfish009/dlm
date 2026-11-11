# Release 0.0201 — transformer behavior → inverse deduction (candidate)

- Date: 2026-11-10
- Predecessor: 0.0200. Candidate, not promoted.
- Scope: train a tiny CPU transformer on a two-hop behavior task, collect its
  train labels, induce a symbolic rule with DLM, and prove held-out pairs.
- Analysis: `/research/analysis-teacher-transformer-0201.md`.

## Teacher

`adapters/teacher_transformer.py`:

```text
CPU PyTorch
1 encoder layer stack (2 layers, d=64, 4 heads)
24K balanced examples
12 epochs
teacher_train_acc = 0.9989
```

Input: two edges plus query pair. Behavior: whether the query is the two-hop
composition.

## Student

DLM receives only:

```text
teacher facts (edge1/edge2)
teacher train labels (pos/neg)
```

It induces one rule and stores it as a basis axiom:

```text
path(x,z) :- edge1(x,y), edge2(y,z).
```

## Experiment

```text
teacher_train_acc=0.9989
wrote ... train_pos=3 train_neg=3
TRAIN pos=3 neg=3 RULES 1
HELD 2/2 NEGPROOFS 0
done-teacher-transformer
```

Held-out two-hop chains are proved; reverse/negative pairs are not proved.

## Self-host

```text
compiler.sh reproduce
→ 20261110T113905Z-20425
compiler.sh verify 20261110T113905Z-20425
→ Verified
```

## Measured

```text
native normal   66 checks / 0 FAIL
native safety-2 66 checks / 0 FAIL
self-host       verified
```

## Still not

- tiny synthetic two-hop task, not an LLM/foundation model
- behavior collection is finite and balanced
- no exact teacher-student equivalence proof
- no web text in this teacher experiment
- proof remains the truth gate
